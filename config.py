import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    LOGGING_PATH = os.getenv('LOGGING_PATH', 'python_logging/logging.yaml')

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    MODE = os.environ['MODE']
    MASTER_HOST = os.getenv('MASTER_HOST', '')
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    MODE = os.environ['MODE']
    MASTER_HOST = os.getenv('MASTER_HOST', '')
    DEBUG = False
