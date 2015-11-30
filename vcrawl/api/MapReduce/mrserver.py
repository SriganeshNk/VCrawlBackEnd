import subprocess
import ast
import final_crawler as fc
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/mrcrawls', methods=['POST'])
def check_vulnerabilities():
    path = request.form.get("url")
    page = request.form.get("pages")
    domain = fc.findDomain(path)
    path = fc.getCorrectURL(path)
    urls = fc.crawl(path, domain, int(page))
    data = open("./urllist.txt", "w")
    for url in urls:
        data.write("%s\n" % (url))
    data.close()

    # Cleans the HDFS paths and loads the urllists to HDFS
    subprocess.call("./mrstartup.sh", shell=True)
    
    # Starts the MR job for the urls in the urllist
    subprocess.call("./mrlauncher.sh --input=/user/smullassery/syssec/urllist.txt --output=/user/smullassery/syssec/output", shell=True)
    
    # Reads the result from MR job
    result = subprocess.Popen(["hdfs", "dfs" ,"-cat", "/user/smullassery/syssec/output/*"], stdout=subprocess.PIPE)
    result_string, error = result.communicate()
    results = result_string.split('\t\n')
    print("Map Reduce job completed")
    final_result = []
    for temp in results:
        if temp:
            list1 = ast.literal_eval(temp)
            if list1:
                final_result.extend(list1)
    
    out = final_result
    return jsonify(output=out)

if __name__ == '__main__':
    app.run(host='130.245.130.190', threaded=True)
