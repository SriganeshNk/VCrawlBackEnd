import subprocess
import ast
import final_crawler as fc
from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/crawls', methods=['POST'])
def create_crawl():
    path = request.form.get("url")
    page = request.form.get("pages")
    domain = fc.findDomain(path)
    path = fc.getCorrectURL(path)
    urls = fc.crawl(path, domain, int(page))
    if len(urls) > int(page):
        urls = urls[:int(page)]
    out = fc.analyseMain(urls)
    if len(out) == 0:
        response = jsonify(output=out)
        response.status_code = 500
        return response
    return jsonify(output=out)

if __name__ == '__main__':
    app.run(host='130.245.130.190', threaded=True)
