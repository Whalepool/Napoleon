# Load config

from pprint import pprint 
import os
from pathlib import Path
import yaml
import sys

PATH = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]

config_file = PATH+'/config.yaml'
my_file     = Path(config_file)
if my_file.is_file():
	with open(config_file) as fp:
	    config = yaml.load(fp)
	    globals().update(config)
	    del config
else:
	pprint('config.yaml file does not exists. Please make from config.sample.yaml file')
	sys.exit()
