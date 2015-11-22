from urlparse import urljoin
from urllib2 import urlopen
from bs4 import BeautifulSoup
from collections import deque
#import httplib2
import requests
import thread
import threading
import time
import urllib2
from AnalyseHeader import AnalyseHeader
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

bsoup = None
crawled_links = 1
max_crawl = None
url_database = set()
vulData = []
domain = None
lock = threading.RLock()


def analyse(thName, urls):
    #h = httplib2.Http(disable_ssl_certificate_validation=True)
    global vulData
    ans = AnalyseHeader()
    for u in urls:
        output = {"url": u}
        try:
            r = requests.get(u, verify=True)
            output['data'] = ans.checkURLS(r.headers, r.text)
        except Exception as e:
            print "SOME exception", e
            pass
        if 'data' in output:
            lock.acquire()
            vulData.append(output)
            lock.release()


def analyseMain(crawledUrls):
    numThread = 5
    global vulData
    vulData = []
    n = len(crawledUrls)
    if n >= 1000:
        numThread = 15
    share = n/numThread
<<<<<<< HEAD
    #tList = getThreads(n, numThread, share, crawledUrls)
=======
>>>>>>> f0d36a5e627b66d67c39250485ae920b35713064
    for i in range(numThread+1):
        start = share*i
        end = share*(i+1) if share*(i+1) < n else n
        try:
            print "Started Thread", i, start, end
            thread.start_new_thread(analyse, (str(i), crawledUrls[start:end]))
        except Exception as e:
            print "Exception with starting Threads", e
            return vulData
        if end >= n:
            break
<<<<<<< HEAD
    #for i in tList:
    #    i.start()
=======
>>>>>>> f0d36a5e627b66d67c39250485ae920b35713064
    temp = len(vulData)
    while len(vulData) < n:
        time.sleep(2) #To make the thread sleep for 2 seconds
        if temp != len(vulData):
            temp = len(vulData)
        else:
            break
        continue
<<<<<<< HEAD
    #for i in tList:
    #    i.join()
=======
>>>>>>> f0d36a5e627b66d67c39250485ae920b35713064
    return vulData[:n]


def getCorrectURL(url):
    print "URL", url
    try:
        customReq = urllib2.Request(url)
        customRes = urllib2.urlopen(customReq)
        path = customRes.geturl()
        print "RETURNED URL", path
        return path
    except:
        return url


def findDomain(url):
    website = url.split("//")
    print "WEBSITE", website
    possibleDomain = website[1].split(".")
    n = len(possibleDomain)
    domain = possibleDomain[n-2] + "." + possibleDomain[n-1]
    print "Include Domains:", domain
    return domain


def crawl(url, domain, maxurls=100):
    global url_database
<<<<<<< HEAD
    url_database = set()
    url_database.add(url)
=======
    url_database = set([url])
>>>>>>> f0d36a5e627b66d67c39250485ae920b35713064
    """Starting from this URL, crawl the web until
    you have collected maxurls URLS, then return them
    as a set"""
    urls = deque([url])
    while len(urls) < maxurls:
        print len(urls), len(url_database)
        url = urls.popleft()
        L = get_links2(url, domain)
        if L is not None:
            urls.extend(L)
            urls.append(url)
        print "-------------------------------"
    print "OUTSIDE LOOP:", len(urls), len(url_database)
    return list(urls)[:maxurls+1]


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content"""
    print "GetPage:", url
    try:
        fd = urlopen(url)
    except:
        return None
    content = fd.read()
    fd.close()
    try:
        return content.decode('utf8')
    except:
        return content.decode('latin-1')

def get_links2(url, domain):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""
    global url_database
    links = []
    text = get_page(url)
    if text is None and url in url_database:
        url_database.remove(url)
        return []
    soup = BeautifulSoup(text, "lxml")
    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            newurl = link.attrs['href']
            if newurl.startswith('/'):
                newurl = urljoin(url, newurl)
            # ignore any URL that doesn't now start with http
            if newurl.endswith('/'):
                newurl = newurl[:-1]
            if newurl.startswith('http') and newurl not in url_database and domain in newurl:
                url_database.add(newurl)
                links.append(newurl)
    return links
