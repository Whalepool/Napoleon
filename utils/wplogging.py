import logging
import sys




##################################
# Configure Logging
##################################
FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('root')
logger.info("Running "+sys.argv[0])


##################################
# Configure Logging
##################################


#FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'

#logging.basicConfig(level=logging.INFO, format=FORMAT)

#logger = logging.getLogger('root')

#hdlr=logging.FileHandler('/var/tmp/napoleon.log')

#formatter=logging.Formatter(FORMAT)

#hdlr.setFormatter(formatter)

#logger.addHandler(hdlr)

#logger.setLevel(logging.WARNING)

#logger.info("Running "+sys.argv[0])
