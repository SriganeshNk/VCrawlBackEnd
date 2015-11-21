from urlparse import urljoin
from urllib2 import urlopen
from bs4 import BeautifulSoup
from collections import deque
import httplib2
import thread
import threading
import time
import urllib2
from AnalyseHeader import AnalyseHeader


bsoup = None
crawled_links = 1
max_crawl = None
url_database = set()
vulData = []
domain = None
lock = threading.RLock()

def analyse(thName, urls):
    h = httplib2.Http()
    global vulData
    ans = AnalyseHeader()
    for u in urls:
        try:
            (resp_headers, content) = h.request(u, "GET")
            output = {"url": u}
            output['data'] = ans.checkURLS(resp_headers, content)
            lock.acquire()
            vulData.append(output)
            lock.release()
        except Exception as e:
            print "SOME exception", e
            pass

def analyseMain(urls):
    numThread = 5
    global vulData
    n = len(urls)
    if n >= 1000:
        numThread = 15
    share = n/numThread
    print share
    last = 0
    try:
        for i in range(0, numThread):
            thread.start_new_thread(analyse, (str(i), urls[share*i:share*(i+1)]))
            last = share*(i+1)
        thread.start_new_thread(analyse, (str((last/share)+1), urls[last:]))
    except Exception as e:
        print "Exception with starting Threads" + e
        return vulData
    temp = len(vulData)
    while len(vulData) < n:
        time.sleep(2) #To make the thread sleep for 2 seconds
        if temp != len(vulData):
            temp = len(vulData)
        else:
            break
        continue
    return vulData

def getCorrectURL(url):
    customReq = urllib2.Request(url)
    customRes = urllib2.urlopen(customReq)
    path = customRes.geturl()
    print "RETURNED URL", path
    return path

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
    url_database = {url}
    """Starting from this URL, crawl the web until
    you have collected maxurls URLS, then return them
    as a set"""
    urls = deque([url])
    while len(urls) < maxurls:
        print len(urls), len(url_database)
        url = urls.popleft()
        urls.extend(get_links2(url, domain))
        urls.append(url)
        print "-------------------------------"
    print "OUTSIDE LOOP:", len(urls), len(url_database)
    return list(urls)[:maxurls+1]


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content"""
    print "GetPage:", url
    fd = urlopen(url)
    content = fd.read()
    fd.close()
    return content.decode('utf8')

def get_links2(url, domain):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""
    global url_database
    links = []
    text = get_page(url)
    soup = BeautifulSoup(text)
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
