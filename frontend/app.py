import os

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, Markup, jsonify
)

import pkuseg
from flask_bootstrap import Bootstrap
from search import SrcEng


wordCutter = None

def init_cutter():
    global wordCutter
    print("[INFO] Loading Model...")
    # wordCutter = hanlp.load('CTB6_CONVSEG')
    wordCutter = pkuseg.pkuseg(model_name = 'medicine')
    print("[INFO] Model Loaded")


app = Flask(__name__, instance_relative_config = True)
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

# set default button sytle and size, will be overwritten by macro parameters
app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'


init_cutter()


@app.route('/', methods = ["POST", "GET"])
def query():
    if request.method == 'POST':
        keyword = request.form['queryKeyword']
        output = SrcEng.query(keyword, 20)
        return render_template('result.html', keyword = keyword, results = output)
    return render_template('query.html')

@app.route('/query', methods = ['GET'])
def rawquery():
    word = request.args.get('word')
    results = SrcEng.query_raw(word, 100)
    return render_template('raw_query.html', results = results)

if __name__ == "__main__" :
    app.run(host = '0.0.0.0', port = 2333)