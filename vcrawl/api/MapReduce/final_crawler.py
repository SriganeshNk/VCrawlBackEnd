from urlparse import urljoin
from urllib2 import urlopen
from bs4 import BeautifulSoup
from collections import deque
import requests
from multiprocessing import Process, Manager, RLock
import urllib2
from AnalyseHeader import AnalyseHeader
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

bsoup = None
crawled_links = 1
max_crawl = None
url_database = set()
man = Manager()
vulData = man.list()
domain = None

def analyse(l, st, urls):
    global vulData
    count = st
    ans = AnalyseHeader()
    #print count
    for u in urls:
        #print st, count, u
        output = {"url": u}
        try:
            r1 = requests.get(u, verify=True)
            r2 = requests.get(u, verify=True)
            Text1, Text2 = None, None
            if 'Content-Type' in r1.headers and r1.headers['Content-Type'] != 'application/zip':
                Text1, Text2 = r1.text, r2.text
            output['data'] = ans.checkURLS(r1.headers, Text1, Text2)
            output['data']['exception'] = False
        except Exception as e:
            try:
                #print "SOME exception", e
                req1 = requests.get(u, verify=False)
                req2 = requests.get(u, verify=False)
                output['data'] = ans.checkURLS(req1.headers, req1.text, req2.text)
                output['data']['exception'] = True
            except:
                pass
        if 'data' in output:
            l.acquire(timeout=5)
            vulData[count] = output
            l.release()
            count += 1
    #print count

def analyseMain(crawledUrls):
    numThread = 5
    global vulData
    l = RLock()
    vulData = man.list([0] * len(crawledUrls)) #Array containing the data of crawled URLS
    n = len(crawledUrls)
    if n >= 1000:
        numThread = 15
    if n <= 5:
        numThread = 1
    processes = []
    share = n/numThread
    for i in range(numThread+1):
        start = share*i
        end = share*(i+1) if share*(i+1) < n else n
        try:
            print "Started Process", i, start, end
            p = Process(target = analyse, args=(l, start, crawledUrls[start:end]))
            processes.append(p)
        except Exception as e:
            print "Exception with starting Threads", e
            return vulData
        if end >= n:
            break
    for p in processes:
        p.start()
    print "DONE starting"
    for p in processes:
        p.join()
    print "Finished"
    return vulData[:n]

def getCorrectURL(url):
    print "URL", url
    try:
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        customRes = urlopen(req)
        path = customRes.geturl()
        print "RETURNED URL", path
        return path
    except Exception as e:
        print "Exception in getting correct URL", e
        return None


def findDomain(url):
    website = url.split("//")
    print "WEBSITE", website
    possibleDomain = website[1].split(".")
    n = len(possibleDomain)
    domain = possibleDomain[n-2] + "." + possibleDomain[n-1].split("/")[0]
    print "Include Domains:", domain
    return domain


def crawl(url, domain, maxurls=100):
    global url_database
    url_database = set([url])
    """Starting from this URL, crawl the web until
    you have collected maxurls URLS, then return them
    as a set"""
    urls = deque([url])
    temp = len(urls)
    count = 0
    while len(urls) < maxurls:
        print len(urls), len(url_database)
        url = urls.popleft()
        L = get_links2(url, domain)
        if L is not None:
            urls.extend(L)
        urls.append(url)
        print "-------------------------------"
        if temp == len(urls):
            count += 1
        else:
            count = 0
            temp = len(urls)
        if count == 5:
            return list(urls)
    print "OUTSIDE LOOP:", len(urls), len(url_database)
    return list(urls)


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content"""
    print "GetPage:", url
    try:
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        fd = urlopen(req)
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
