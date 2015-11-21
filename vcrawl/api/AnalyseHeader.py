# https://www.owasp.org/index.php/List_of_useful_HTTP_headers

# Based on the above website information about http headers

# Nonces ---> need to check forms for nonce id's, requires parsing the content and identifying nonceIDS

class AnalyseHeader(object):
    def __init__(self):
        self.CSP = ["content-security-policy", "x-content-security-policy", "x-webkit-csp"]
        self.Xframe = ["x-frame-options", "frame-options"]
        self.XSS = "x-xss-protection"
        self.CSRF = "nonce"
        self.HTTPS = "strict-transport-security"

    def checkCSP(self, header):
        for each in self.CSP:
            if each in header:
                #Probably need to have additional checks, like what kind of CSP is secure
                return True
        return False

    def checkHTTPS(self, header):
        if self.HTTPS in header:
            #Probably need to have additional checks, like what kind of HTTPS is enabled
            return True
        return False

    def checkXFrame(self, header):
        for each in self.Xframe:
            if each in header:
                #Probably need to have additional checks, like what kind of XFrame is enabled
                return True
        return False

    def checkXSS(self, header):
        if self.XSS in header:
            #if "" in header[self.XSS]:
            #    return False    
            if "mode=block" in header[self.XSS]:
                return "block"
            elif "1" in header[self.XSS]:
                return True 
            else:
		return False            

    def checkCSRF(self, header):
        if self.CSRF in header:
            #Probably need to have additional checks, like what kind of CSRF is enabled
            return True
        return False

    def checkURLS(self, header, response):
        vul = {}
        vul['csp'] = self.checkCSP(header)
        vul['csrf'] = self.checkCSRF(header)
        vul['https'] = self.checkHTTPS(header)
        vul['xframe'] = self.checkXFrame(header)
        vul['xss'] = self.checkXSS(header)
        return vul

a = AnalyseHeader()
import httplib2
import json
h = httplib2.Http(".cache")
(header, content) = h.request("http://github.com/integrations/gitter", "GET")
print json.dumps(header, indent=4, sort_keys=True)
print json.dumps(a.checkURLS(header, content), indent=4, sort_keys=True)
