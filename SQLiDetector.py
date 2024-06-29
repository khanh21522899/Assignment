import requests
import re
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pprint import pprint
import argparse


def get_args():
   #Retrieve user input as argument
   parser = argparse.ArgumentParser()
   parser.add_argument('-u', '--url', dest='url',default='', help="The target URL", required=True)
   return parser.parse_args()

class SQLiDetector:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"

    def login_DVWA(self):
        login_payload = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        }
        login_url = "http://192.168.2.205:80/DVWA/login.php"

        res = self.session.get(login_url)
        token = re.search("user_token'\s*value='(.*?)'", res.text).group(1)
        login_payload['user_token'] = token
        self.session.post(login_url, data=login_payload)

    def get_forms(self):
        soup = bs(self.session.get(self.url).content, "html.parser")
        return soup.find_all("form")

    def get_formdetails(self, form):
        details = {}

        try:
            action = form.attrs.get("action").lower()
        except:
            action = None

        method = form.attrs.get("method", "get").lower()

        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})
        
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs

        return details
    
    def is_vulnerable(self, response):
        errors = [
        # MySQL
        "you have an error in your sql syntax;",
        "warning: mysql",
        # SQL Server
        "unclosed quotation mark after the character string",
        # Oracle
        "quoted string not properly terminated",
        ]
        for error in errors:
            # if you find one of these errors, return True
            if error in response.content.decode().lower():
                return True
        # no error detected
        return False
    
    def scan(self):
        #Test on url first, if it vulnerable no need to perform on HTML form
        url = self.url
        for test in "\"'":
            test_url = f'{url}{test}'
            print("[!] Perform the scan on url: ", test_url)
            res = self.session.get(test_url)

            if self.is_vulnerable(res):
                # SQL Injection detected on the URL itself, 
                # no need to preceed for extracting forms and submitting them
                print("[+] SQL Injection vulnerability detected, link:", test_url)
                return
        
        #Test on form after url fail
        forms = self.get_forms()
        print(f"[+] Detected {len(forms)} forms on {url}.")
        for form in forms:
            form_details = self.get_formdetails(form)
            for test in "\"'":
                data = {}
                for input_tag in form_details["inputs"]:
                    if input_tag["value"] or input_tag["type"] == "hidden":
                        # any input form that has some value or hidden,
                        # just use it in the form body
                        try:
                            data[input_tag["name"]] = input_tag["value"] + test
                        except:
                            pass
                    elif input_tag["type"] != "submit":
                        # all others except submit, use some junk data with special character
                        data[input_tag["name"]] = f"test{test}"
                
                endpoint = urljoin(url, form_details["action"])
                if form_details["method"] == "post":
                    res = self.session.post(url, data=data)
                elif form_details["method"] == "get":
                    res = self.session.get(url, params=data)
                # test whether the resulting page is vulnerable
                if self.is_vulnerable(res):
                    print("[+] SQL Injection vulnerability detected, link:", url)
                    print("[+] Form:")
                    pprint(form_details)
                    break   

if __name__ == "__main__":
    args = get_args()

    sqli = SQLiDetector(args.url)
    sqli.login_DVWA()
    sqli.scan()

    
        