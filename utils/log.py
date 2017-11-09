#!/usr/bin/env python3
import sys
import logging
logcolor = None
try:
    import colorlog
except:
    pass

def initLog(default_min_log=logging.INFO,*args,**kwargs):
    try:
        colorlog.basicConfig(
            level=default_min_log,
            #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
            format="%(log_color)s[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s %(reset)s",
            datefmt="%H:%M] [%S",
            stream=sys.stdout
        )
    except:
        pass

    logging.basicConfig(
        level=default_min_log,
        #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
        format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
        datefmt="%H:%M] [%S",
        stream=sys.stdout
    )
    if 'color' in kwargs and kwargs['color']:
        return colorlog.getLogger()
    else:
        return logging.getLogger()

log = initLog(color=True)
log.debug("File log.py loaded")