import os
from configparser import ConfigParser
import logging

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