#External
import logging
import sys
import time

logging.basicConfig(filename='logs\debug-'+str(time.time())+'.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#logging.basicConfig(filename='logs\debug-'+str(time.time())+'.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def debug(text: str):
    logging.debug(text)
def info(text: str):
    logging.info(text)
def warning(text: str):
    logging.warning(text)
def error(text: str):
    logging.error(text)
def critical(text: str):
    logging.critical(text)