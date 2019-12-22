import logging
import logging.handlers
import time
import os

logger = logging.getLogger(__name__)

def timeSized():
    filePath = os.path.join(r'c:\temp\log','time.log')
    logHandler = logging.handlers.TimedRotatingFileHandler(filePath,
                                          when='s',
                                          interval=10,
                                          backupCount = 10)
    format = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s', '%Y-%m-%d %H:%M:%S')
    
    logger.setLevel(logging.INFO)
    logHandler.setFormatter(format)    
    logHandler.suffix = '%Y%m%d%H%M%S'
    logger.addHandler(logHandler)

    while True:
        logger.info('in Console')
        time.sleep(1)

def Sizedbased():
    filePath = os.path.join(r'c:\temp\log','size.log')
    logHandler = logging.handlers.RotatingFileHandler(filePath,
                                          maxBytes=20,
                                          backupCount = 10)
    format = logging.Formatter('%(name)s, %(asctime)s, %(levelname)s, %(message)s', '%Y-%m-%d %H:%M:%S')
    
    logger.setLevel(logging.INFO)
    logHandler.setFormatter(format)    
    logger.addHandler(logHandler)

    while True:
        logger.info('in Console')
        time.sleep(1)
        
    

def console():
    logging.basicConfig(level=logging.INFO,format='%(name)s, %(asctime)s, %(levelname)s, %(message)s')
    while True:
        logger.info('in Console')
        time.sleep(1)

if __name__ == '__main__':
    console()