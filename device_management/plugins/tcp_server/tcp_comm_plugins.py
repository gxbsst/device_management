# -*- coding: utf-8 -*-
import sys, socket, threading
import logging
import time

from task_order_parser import TaskOrderRequestParser
from plugins.base_plugin import BasePlugin

'''
class StreamRequestHandler(SocketServer.StreamRequestHandler):
    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def handleRequest(self, request_data):
        return request_data

    def handle(self):
        global SendCondition
        global SendData
        global RequestComing
        self.logDebug('handle')
        print '...connected from:', self.client_address
        try:
            RequestComing = True
            request_data = self.request.recv(4096)
            if request_data:
                self.logDebug('{}: recv()->"{}"'.format(threading.currentThread().getName(),
                                                        request_data))
                response_data = self.handleRequest(request_data)
                self.request.sendall(response_data)

                # Wait for task status
                with SendCondition:
                    while not SendData:
                        SendCondition.wait()
                    self.request.sendall(SendData)
        except socket.timeout:
            print "caught socket.timeout exception"

    def logTemplate(self, s):
        return '[id.' + str(id(self.request)) + ']:  ' + str(s)

    def logDebug(self, s):
        ss = self.logTemplate(s)
        print ss
        
class TcpServer(SocketServer.TCPServer):
    allow_reuse_address = True
'''

class TaskStatusServer(threading.Thread):
    def __init__(self, name, server_address, num_of_connections, **kwargs):
        threading.Thread.__init__(self, name=name, kwargs=kwargs)
        self.setDaemon(True)
        self.server_address = server_address
        self.num_of_connections = num_of_connections
        self.started = False

        self.new_task_status_cond = threading.Condition()

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port        
        print >> sys.stderr, '[Task-Status-Server] ... starting up on %s port %s' % self.server_address
        self.sock.bind(self.server_address)

        # Listen for incoming connections
        self.sock.listen(self.num_of_connections)

        self.connections = []

    def run(self):
        self.started = True
        while self.started:
            # Wait for a connection
            connection, client_address = self.sock.accept()
            print >>sys.stderr, '[Task-Status-Server] ... connection from: ', client_address
            if not connection in self.connections:
                self.connections.append(connection)
        self.started = False

    def sendTaskStatus(self, status):
        from xml.dom.minidom import Document
        doc = Document()
        root_element = doc.createElement("status")
        doc.appendChild(root_element)
        root_element.setAttribute("timeStamp", str(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())))
        root_element.setAttribute("orderName", status[0])
        root_element.setAttribute("orderState", str(status[1]))
        if len(status) > 2:
            detail_element = doc.createElement("details")
            root_element.appendChild(detail_element)
            detail_element.appendChild(doc.createTextNode(str(status[2])))

        data = doc.toxml(encoding="utf-8")
        if self.connections:
            for connection in self.connections:
                try:
                    connection.sendall(data)
                except Exception, e:
                    connection.close()
                    self.connections.remove(connection)
                    
    def stop(self):
        self.started = False
        if self.connections:
            for connection in self.connections:
                # Clean up the connection
                try:
                    connection.close()
                except Exception, e:
                    pass
        self.sock.close()

class TaskOrderRequestHandler:
    def __init__(self, app):
        self.app = app
        self.request_parser = TaskOrderRequestParser()

    def handleRequest(self, request):
        orders = self.request_parser.parseRequest(request)
        response = self.crateAndAddNewTask(orders)
        return response

    def crateAndAddNewTask(self, orders):        
        try:
            new_task = self.app.createAndAddTask(orders)
        except Exception, e:
            return self.request_parser.createResponse(False, str(e))
        return self.request_parser.createResponse(True, new_task)

class TaskOrderServer(threading.Thread):
    def __init__(self, name, server_address, num_of_connections, request_handler, **kwargs):
        threading.Thread.__init__(self, name=name, kwargs=kwargs)
        self.setDaemon(True)
        self.server_address = server_address
        self.num_of_connections = num_of_connections
        self.request_handler = request_handler
        self.started = False

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port        
        print >> sys.stderr, '[Task-Order-Server] ... starting up on %s port %s' % self.server_address
        self.sock.bind(self.server_address)

        # Listen for incoming connections
        self.sock.listen(self.num_of_connections)

    def handleRequest(self, request):
        response = self.request_handler.handleRequest(request)
        return response

    def run(self):
        self.started = True
        while self.started:
            # Wait for a connection
            connection, client_address = self.sock.accept()
            try:
                print >>sys.stderr, '[Task-Order-Server] ... connection from: ', client_address

                #while True:
                request = connection.recv(4096)
                print >>sys.stderr, '[Task-Order-Server] ... received "%s"' % request
                if request:
                    response = self.handleRequest(request)
                    connection.sendall(response)
                else:
                    print >>sys.stderr, '[Task-Order-Server] ... no data from', client_address
                    #break
            finally:
                # Clean up the connection
                connection.close()
        self.started = False

    def stop(self):
        self.started = False
        self.sock.close()

class TcpCommucation(BasePlugin):
    def __init__(self, app):
        BasePlugin.__init__(self, app)
        # host, port
        order_server_address = ('localhost', 22222)
        status_server_address = ('localhost',22223)
        self.task_status_server = TaskStatusServer("Task-Status-Server-Thread",
                                                   status_server_address,
                                                   5)
        self.task_order_server = TaskOrderServer("Task-Order-Server-Thread", 
                                             order_server_address, 
                                             1,
                                             TaskOrderRequestHandler(app))

        #self.server = TcpServer(server_address, StreamRequestHandler)
        #self.task_order_server = threading.Thread(target=self.server.serve_forever)
        #self.task_order_server.setDaemon(True)
 
    def install(self):
        self.registerTaskMessageHandler(self.task_status_server.sendTaskStatus)
        self.task_status_server.start()
        self.task_order_server.start()
                
    def uninstall(self):
        self.unregisterTaskMessageHandler(self.task_status_server.sendTaskStatus)
        print "[Task-Status-Server] closing..."
        self.task_status_server.stop()        
        print "[Task-Order-Server] closing..."
        self.task_order_server.stop()
        #self.server.socket.close()