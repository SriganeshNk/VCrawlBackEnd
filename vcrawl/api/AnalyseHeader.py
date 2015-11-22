# https://www.owasp.org/index.php/List_of_useful_HTTP_headers

# Based on the above website information about http headers

# Nonces ---> need to check forms for nonce id's, requires parsing the content and identifying nonceIDS

from bs4 import BeautifulSoup

class AnalyseHeader(object):
    def __init__(self):
        self.CSP = ["content-security-policy", "x-content-security-policy", "x-webkit-csp"]
        self.XFRAME = ["x-frame-options", "frame-options"]
        self.XSS = "x-xss-protection"
        self.CSRF = "nonce"
        self.HSTS = "strict-transport-security"

    def checkCSP(self, header):
        #print "CSP"
        csp_directives = ['base-uri', 'child-src', 'connect-src', 'default-src', 'font-src', 'form-action', 'frame-ancestors', 'frame-src', 'img-src', 'media-src', 'object-src', 'plugin-types', 'report-uri','script-src', 'style-src', 'upgrade-insecure-requests']
        csp_map = {'implemented' : False}
        for csp in self.CSP:
            if csp in header:
                csp_map['implemented'] = True
                for directive in csp_directives:
                    csp_map[directive] = False
                policy_string = header[csp]
                policy_list = policy_string.split(';')
                for policy in policy_list:
                    policy_strings = policy.strip().split(' ')
                    if policy_strings[0] in csp_directives:
                        csp_map[policy_strings[0]] = True
        return csp_map

    def checkHSTS(self, header):
        #print "hsts"
        hsts_directives = ['max-age', 'includeSubdomains', 'preload']
        hsts_map = {'implemented' : False}
        if self.HSTS in header:
            hsts_map['implemented'] = True
            for directive in hsts_directives:
                hsts_map[directive] = False
            policy_string = header[self.HSTS]
            policy_list = policy_string.split(';')
            for policy in policy_list:
                policy_strings = policy.strip().split('=')
                #print policy, policy_strings
                if policy_strings[0] in hsts_directives:
                    if policy_strings[0] == hsts_directives[0]:
                        hsts_map[policy_strings[0]] = policy_strings[1]
                    else:
                        hsts_map[policy_strings[0]] = True
        return hsts_map

    def checkXFrame(self, header):
        #print "xframe"
        xframe_modes = ['deny', 'sameorigin', 'allow-from']
        xframe_map = {'implemented' : False}
        for xframe in self.XFRAME:
            if xframe in header:
                xframe_map['implemented'] = True
                policy_string = header[xframe]
                policy_list = policy_string.split(';')
                assert len(policy_list) == 1, "Can specify only one XFrame mode!"
                policy_strings = policy_list[0].split(' ')
                if policy_strings[0] in xframe_modes:
                    xframe_map['mode'] = policy_strings[0]
                if policy_strings[0] == 'allow-from':
                    assert len(policy_strings) == 2, "Need an external framing page URI for 'allow-from' framing mode"
                    xframe_map['framing_page_uri'] = policy_strings[1]
        return xframe_map

    def checkXSS(self, header):
        #print "xss"
        xss_directives = ['mode']
        xss_map = {'implemented' : False}
        if self.XSS in header:
            for directive in xss_directives:
                xss_map[directive] = False
            policy_string = header[self.XSS]
            policy_list = policy_string.split(';')
            for policy in policy_list:
                policy_strings = policy.strip().split('=')
                if policy_strings[0] == '1':
                    xss_map['implemented'] = True
                elif policy_strings[0] == xss_directives[0]:
                    if policy_strings[1] == 'block':
                        xss_map['mode'] = 'block'
                    else:
                        xss_map['mode'] = 'sanitize'
        return xss_map

    def checkCSRF(self, header, content):
        nonce_fields = ['appActionToken', 'secTok', 'authenticity_token', 'nonce']
        for each in self.CSP:
            if each in header and self.CSRF in header[each]:
                return True
        soup = BeautifulSoup(content, "lxml")
        for form in soup.find_all('form'):
            for formAttrs in form.attrs:
                if self.CSRF in formAttrs:
                    return True
            for inputTag in form.find_all('input'):
                if 'type' in inputTag.attrs and 'hidden' in inputTag.attrs['type']:
                    if 'name' in inputTag.attrs and inputTag.attrs['name'] in nonce_fields:
                        return True
        return False


    def checkURLS(self, header, content):
        vul = {}
        vul['csp'] = self.checkCSP(header)
        vul['csrf'] = self.checkCSRF(header, content)
        vul['hsts'] = self.checkHSTS(header)
        vul['xframe'] = self.checkXFrame(header)
        vul['xss'] = self.checkXSS(header)
        return vul


"""
a = AnalyseHeader()
import httplib2
import json
h = httplib2.Http(".cache")
(header, content) = h.request("http://github.com/integrations/gitter", "GET")
print json.dumps(header, indent=4, sort_keys=True)
print json.dumps(a.checkURLS(header, content), indent=4, sort_keys=True)
"""
