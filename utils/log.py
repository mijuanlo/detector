#!/usr/bin/env python3
import sys
import logging
try:
    import colorlog
except:
    pass

class logger(logging.getLoggerClass()):
    def __init__(self,*args,**kwargs):
        self.l = None
        super(logger,self).__init__(*args,**kwargs)

    def initLog(self,default_min_log=logging.INFO,*args,**kwargs):
        if self.l:
            self.l.handlers = []
        if 'color' in kwargs and kwargs['color']:
            try:
                colorlog.basicConfig(
                    level=default_min_log,
                    #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                    format="%(log_color)s[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s %(reset)s",
                    datefmt="%H:%M] [%S",
                    stream=sys.stdout
                )
            except:
                self.color=False
                logging.basicConfig(
                    level=default_min_log,
                    #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                    format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
                    datefmt="%H:%M] [%S",
                    stream=sys.stdout
                )
            self.l = colorlog.getLogger()
        else:
            logging.basicConfig(
                level=default_min_log,
                #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
                datefmt="%H:%M] [%S",
                stream=sys.stdout
            )
            self.l = logging.getLogger()

        return self

    def debug(self,*args,**kwargs):
        self.l.debug(*args,**kwargs)
    def warning(self,*args,**kwargs):
        self.l.warning(*args,**kwargs)
    def error(self,*args,**kwargs):
        self.l.error(*args,**kwargs)
    def info(self,*args,**kwargs):
        self.l.info(*args,**kwargs)
    def set_level(self,*args,**kwargs):
        self.l.level=args[0]


log=logger('main')
log.initLog(color=False)
log.debug("File log.py loaded")