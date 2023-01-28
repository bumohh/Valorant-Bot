import os
from configparser import ConfigParser
import logging
from datetime import datetime
import asyncio

#file reading / writing
def readGlobalVariable(name: str) :
    config = ConfigParser()
    path_to_config = os.path.dirname(__file__)+"\config.cfg"
    config.read(path_to_config)

    return config["Global Variables"][name]

def writeGlobalVariable(name: str, value : str) : 
    config = ConfigParser()
    path_to_config = os.path.dirname(__file__)+"\config.cfg"
    config.read(path_to_config)
    
    config["Global Variables"][name] = value
    with open(path_to_config, 'w') as conf:
        config.write(conf)

def internalSoftReset():
    logging.debug("starting internalsoftreset function")
    writeGlobalVariable("index","0")
    writeGlobalVariable("count","0")
    writeGlobalVariable("current_minute",str(datetime.now().minute))


# ??????? Test fuction for potential API call limiter
def minuteLimit():
    minute = datetime.now().minute
    if str(minute) == readGlobalVariable("current_minute"):
        writeGlobalVariable("minute_counter", str(int(readGlobalVariable("minute_counter"))+1))
    else:
        writeGlobalVariable("current_minute",str(datetime.now().minute))


