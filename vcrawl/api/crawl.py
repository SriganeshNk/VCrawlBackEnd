from flask import jsonify, request

from . import api
import final_crawler as fc


@api.route('/crawls', methods=['GET'])
def get_crawls():
    return jsonify(token="hello world")


@api.route('/crawls/<string:path>', methods=['GET'])
def get_crawl(path):
    path = "http://"+path
    domain = fc.findDomain(path)
    urls = fc.crawl(path, domain, 100)
    out = fc.analyseMain(urls)
    return jsonify(out=out)


@api.route('/crawls', methods=['POST'])
def create_crawl():
    pass
