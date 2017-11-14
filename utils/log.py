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
        self.color = False
        self.level = logging.INFO
        super(logger,self).__init__(*args,**kwargs)

    def initLog(self,*args,**kwargs):
        if self.l:
            self.l.handlers = []
        if self.color:
            try:
                colorlog.basicConfig(
                    level=self.level,
                    #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                    format="%(log_color)s[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s %(reset)s",
                    datefmt="%H:%M] [%S",
                    stream=sys.stderr
                )
            except:
                logging.basicConfig(
                    level=self.level,
                    #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                    format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
                    datefmt="%H:%M] [%S",
                    stream=sys.stderr
                )
            try:
                self.l = colorlog.getLogger()
            except:
                self.l = logging.getLogger()
        else:
            logging.basicConfig(
                level=self.level,
                #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
                format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
                datefmt="%H:%M] [%S",
                stream=sys.stderr
            )
            self.l = logging.getLogger()
        fh=logging.FileHandler('debug-log-messages.txt',mode='w')
        fh.setFormatter(self.l.handlers[0].formatter)
        self.l.addHandler(fh)

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
        self.level=args[0]
        self.initLog()
    def set_color(self,*args,**kwargs):
        self.color=args[0]
        self.initLog()


log=logger('main')
log.initLog()
#log.debug("File log.py loaded")