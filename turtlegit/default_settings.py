from os import path

class Config(object):
    DOMAIN = 'http://localhost/'
    AUTOADD = True
    AUTOCOMMIT = True
    ROOT_DIR = path.dirname(path.dirname(__file__)).replace('\\','/')
    
class Logging(object):
    LEVEL = 'DEBUG'