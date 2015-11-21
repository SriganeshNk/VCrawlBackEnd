from flask import jsonify, request

from . import api
import final_crawler as fc
import urllib2

@api.route('/crawls', methods=['GET'])
def get_crawls():
    return jsonify(token="hello world")


@api.route('/crawls/<string:path>', methods=['GET'])
def get_crawl(path):
    path = "http://"+path
    domain = fc.findDomain(path)
    urls = fc.crawl(path, domain, 100)
    print "Length of URLS:", len(urls)
    out = fc.analyseMain(urls)
    return jsonify(output=out)


@api.route('/crawls', methods=['POST'])
def create_crawl():
    print "POST CALL"
    path = request.form.get("url")
    page = request.form.get("pages")
    domain = fc.findDomain(path)
    print "Input to the Crawler:", path, domain, page
    path = fc.getCorrectURL(path)
    urls = fc.crawl(path, domain, int(page))
    print "Length of URLS:", len(urls)
    out = fc.analyseMain(urls)
    if len(out) == 0:
        response = jsonify(out=out)
        response.status_code = 500
        return response
    return jsonify(output=out)
