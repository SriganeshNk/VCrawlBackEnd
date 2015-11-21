from urlparse import urljoin
from urllib import urlopen
from bs4 import BeautifulSoup
import httplib2
import thread
import threading
import time
from AnalyseHeader import AnalyseHeader


bsoup = None
crawled_links = 1
max_crawl = None
url_database = []
vulData = []
domain = None
lock = threading.RLock()

def analyse(thName, urls):
    h = httplib2.Http(".cache")
    global vulData
    ans = AnalyseHeader()
    for u in urls:
        (resp_headers, content) = h.request(u, "GET")
        output = {"url": u}
        output['data'] = ans.checkURLS(resp_headers, content)
        lock.acquire()
        vulData.append(output)
        lock.release()


def analyseMain(urls):
    numThread = 5
    global vulData
    n = len(urls)
    if n >= 1000:
        numThread = 15
    share = n/numThread
    last = 0
    for i in range(0, numThread):
        thread.start_new_thread(analyse, (str(i), urls[share*i:share*(i+1)]))
        last = share*(i+1)
    thread.start_new_thread(analyse, (str((last/share)+1), urls[last:]))
    while len(vulData) < n:
        time.sleep(2) #To make the thread sleep for 2 seconds
        continue
    return vulData

def findDomain(url):
    possibleDomain = url.split(".")
    n = len(possibleDomain)
    domain = possibleDomain[n-2]+"."+possibleDomain[n-1]
    return domain


def crawl(url, domain, maxurls=100):
    global url_database
    """Starting from this URL, crawl the web until
    you have collected maxurls URLS, then return them
    as a set"""
    urls = [url]
    while(len(url_database) < maxurls):
        # remove a URL at random
        url = urls.pop(0)
        links = get_links2(url, domain)
        for link in links:
            urls.append(link)
    return urls


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content"""
    fd = urlopen(url)
    content = fd.read()
    fd.close()
    return content.decode('utf8')

def get_links2(url, domain):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""
    global url_database
    # look for any http URL in the page
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
            if newurl.startswith('http'):
                if newurl not in url_database:
                    if domain in newurl:
                        links.append(newurl)
                        url_database.append(newurl)
    return links
