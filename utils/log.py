#!/usr/bin/env python3
import sys
import logging

def initLog(default_min_log=logging.INFO):
    logging.basicConfig(
        level=default_min_log,
        #format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
        format="[%(asctime)s:%(msecs)d] %(levelname)s [%(filename)s:%(lineno)d] [%(processName)s] %(message)s",
        datefmt="%H:%M] [%S",
        stream=sys.stdout
    )
    return logging.getLogger()

log = initLog()
log.debug("File log.py loaded")