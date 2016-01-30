from flask import Flask, request
import os
from flask.ext.sqlalchemy import SQLAlchemy
import threading

yourThread = threading.Thread()

threadstopped = False


app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))
app.config['polling'] = True

db = SQLAlchemy(app)
