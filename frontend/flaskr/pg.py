from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .cut import wordCutter
from .search import SrcEng

bp = Blueprint('pg', __name__, url_prefix = '/')

@bp.route('/', methods = ["POST", "GET"])
def query():
    if request.method == 'POST':
        keyword = request.form['queryKeyword']
        import time
        tt1 = time.time()
        # output = wordCutter.cut(keyword)
        output = SrcEng.query(keyword, 20)
        tt2 = time.time()-tt1
        print(output, tt2)
        return render_template('result.html', results = output)
    return render_template('query.html')
