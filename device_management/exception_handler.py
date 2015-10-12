# -*- coding: utf-8 -*-

import os, sys
import threading, traceback, platform
import time

class ExceptionHandler(object):
    
    def __init__(self, path, app_title='[No title]', app_version='[No version]'):
        self.path = path
        self.app_title = app_title
        self.app_version = app_version
        self.ignored_exceptions = []

    def _get_last_traceback(self, tb):
        while tb.tb_next:
            tb = tb.tb_next
        return tb

    def _format_namespace(self, d, indent='    '):
        return '\n'.join(['%s%s: %s' % (indent, k, repr(v)[:10000]) for k, v in d.iteritems()])

    def _handle_exception(self, e_type, e_value, e_traceback):
        traceback.print_exception(e_type, e_value, e_traceback) # this is very helpful when there's an exception in the rest of this func
        last_tb = self._get_last_traceback(e_traceback)
        ex = (last_tb.tb_frame.f_code.co_filename, last_tb.tb_frame.f_lineno)
        if ex not in self.ignored_exceptions:
            date = time.ctime()
            bug_report_path = self.path+os.sep+"bug_report_"+date.replace(':','-').replace(' ','_')+".txt"
            self.ignored_exceptions.append(ex)
            info = {
                'app-title' : self.app_title,
                'app-version' : self.app_version,
                'python-version' : platform.python_version(), #sys.version.split()[0],
                'platform' : platform.platform(),
                'e-type' : e_type,
                'e-value' : e_value,
                'date' : date,
                'cwd' : os.getcwd(),
                }

            if e_traceback:
                info['traceback'] = ''.join(traceback.format_tb(e_traceback)) + '%s: %s' % (e_type, e_value)
                last_tb = self._get_last_traceback(e_traceback)
                exception_locals = last_tb.tb_frame.f_locals # the locals at the level of the stack trace where the exception actually occurred
                info['locals'] = self._format_namespace(exception_locals)
                if 'self' in exception_locals:
                    info['self'] = self._format_namespace(exception_locals['self'].__dict__)

            output = open(bug_report_path,'w')
            lst = info.keys()
            lst.sort()
            for a in lst:
                output.write(a+":\n"+str(info[a])+"\n\n")

    def _addExceptionHook(self):
        sys.excepthook = self._handle_exception

    def AddExceptHook(self):
        self._addExceptionHook()

        # threading
        init_old = threading.Thread.__init__

        def init(self, *args, **kwargs):
            init_old(self, *args, **kwargs)
            run_old = self.run
            def run_with_except_hook(*args, **kw):
                try:
                    run_old(*args, **kw)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    sys.excepthook(*sys.exc_info())
            self.run = run_with_except_hook

        threading.Thread.__init__ = init
