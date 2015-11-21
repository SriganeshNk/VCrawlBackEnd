# https://www.owasp.org/index.php/List_of_useful_HTTP_headers

# Based on the above website information about http headers

# Nonces ---> need to check forms for nonce id's, requires parsing the content and identifying nonceIDS

class AnalyseHeader(object):
    def __init__(self):
        self.CSP = "content-security-policy"
        self.Xframe = ["x-frame-options", "frame-options"]
        self.XSS = "x-xss-protection"
        self.CSRF = "nonce"
        self.HSTS = "strict-transport-security"

    def checkCSP(self, header):
	csp_directives = ['base-uri', 'child-src', 'connect-src', 'default-src', 'font-src', 'form-action', 'frame-ancestors', 'frame-src', 'img-src', 'media-src', 'object-src', 'plugin-types', 'report-uri','script-src', 'style-src', 'upgrade-insecure-requests']
	csp_map = {'implemented' : 'NO'}
	
	if self.CSP in header:
		csp_map['implemented'] = 'YES'
		for directive in csp_directives:
			csp_map[directive] = 'NO'
		policy_string = header[self.CSP]
		policy_list = policy_string.split(';')
		for policy in policy_list:
			policy_strings = policy.strip().split(' ')
			if policy_strings[0] in csp_directives:
				csp_map[policy_strings[0]] = 'YES'
	return csp_map

    def checkHSTS(self, header):
        hsts_directives = ['max-age', 'includeSubDomains', 'preload']
	hsts_map = {'implemented' : 'NO'}

	if self.HSTS in header:
		hsts_map['implemented'] = 'YES'
		for directive in hsts_directives:
			hsts_map[directive] = 'NO'
		policy_string = header[self.HSTS]
		policy_list = policy_string.split(';')
		for policy in policy_list:
			policy_strings = policy.strip().split('=')
			print policy, policy_strings
			if policy_strings[0] in hsts_directives:
				if policy_strings[0] == hsts_directives[0]:
					hsts_map[policy_strings[0]] = policy_strings[1]
				else:
					hsts_map[policy_strings[0]] = 'YES' 
        return hsts_map

    def checkXFrame(self, header):
        for each in self.Xframe:
            if each in header:
                #Probably need to have additional checks, like what kind of XFrame is enabled
                return True
        return False

    def checkXSS(self, header):
        if self.XSS in header:
            #Probably need to have additional checks, like what kind of XSS is enabled
            return True
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
        vul['hsts'] = self.checkHSTS(header)
        vul['xframe'] = self.checkXFrame(header)
        vul['xss'] = self.checkXSS(header)
        return vul

a = AnalyseHeader()
import httplib2
import json
h = httplib2.Http(".cache")
(header, content) = h.request("http://twitter.com/jimmyfallon", "GET")
print json.dumps(header, indent=4, sort_keys=True)
print json.dumps(a.checkURLS(header, content), indent=4, sort_keys=True)

