from flask import current_app, g
from flask.cli import with_appcontext
import hanlp
import time
import pkuseg

wordCutter = None

def init_cutter():
    global wordCutter
    print("[INFO] Loading Model...")
    # wordCutter = hanlp.load('CTB6_CONVSEG')
    wordCutter = pkuseg.pkuseg(model_name = 'medicine')
    print("[INFO] Model Loaded")
