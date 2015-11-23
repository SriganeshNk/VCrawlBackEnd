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

    def checkCSRF(self, header, content1, content2):
        nonce_fields = ['appActionToken', 'secTok', 'authenticity_token', 'nonce', 'data-form-nonce']
        csrf_map = {'implemented' : False}
        for each in self.CSP:
            if each in header and self.CSRF in header[each]:
		        csrf_map['implemented'] = True
		        return csrf_map
        soup1 = BeautifulSoup(content1, "lxml")
        soup2 = BeautifulSoup(content2, "lxml")
        forms1 = soup1.find_all('form')
        forms2 = soup2.find_all('form')
        form1 = 0
        form2 = 0
        while form1 < len(forms1) and form2 < len(forms2):
    	    form1_attrs = forms1[form1].attrs
    	    form2_attrs = forms2[form2].attrs
    	    for form_attr in form1_attrs:
        		if self.CSRF in form_attr:
        		    if form1_attrs[form_attr] != form2_attrs[form_attr]:
        			    csrf_map['implemented'] = True
        			    return csrf_map

    	    form1_inputtags = forms1[form1].find_all('input')
    	    form2_inputtags = forms2[form2].find_all('input')
    	    for inputtag in range(len(form1_inputtags)):
                form1_inputtag_attrs = form1_inputtags[inputtag].attrs
                form2_inputtag_attrs = form2_inputtags[inputtag].attrs
                if 'type' in form1_inputtag_attrs and form1_inputtag_attrs['type']=='hidden' and 'type' in form2_inputtag_attrs and form2_inputtag_attrs['type']=='hidden':
        			if 'name' in form1_inputtag_attrs and form1_inputtag_attrs['name'] in nonce_fields and 'name' in form2_inputtag_attrs and form2_inputtag_attrs['name'] in nonce_fields:
					#print "Input tag nonce detected ", form1_inputtag_attrs['value'], form2_inputtag_attrs['value']
        				if form1_inputtag_attrs['value'] != form2_inputtag_attrs['value']:
        					csrf_map['implemented'] = True
        					return csrf_map
    	    form1 = form1 + 1
    	    form2 = form2 + 1
        return csrf_map

    def checkURLS(self, header, content1, content2):
        vul = {}
        vul['csp'] = self.checkCSP(header)
        vul['csrf'] = self.checkCSRF(header, content1, content2)
        vul['hsts'] = self.checkHSTS(header)
        vul['xframe'] = self.checkXFrame(header)
        vul['xss'] = self.checkXSS(header)
        return vul

'''
a = AnalyseHeader()
import httplib2
import json
h = httplib2.Http(".cache")
(header1, content1) = h.request("http://github.com", "GET")
(header2, content2) = h.request("http://github.com", "GET")
print json.dumps(header1, indent=4, sort_keys=True)
print json.dumps(a.checkURLS(header1, content1, content2), indent=4, sort_keys=True)
'''
