import requests
import argparse
from bs4 import BeautifulSoup
import re



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urls', dest='urls',default=[], nargs='+', help="Specify the URLs, provide it along http/https", required=True)
    parser.add_argument('-d', '--depth', dest='depth', type=int, default=1, help="Specify the recursion depth limit")
    parser.add_argument('-o', '--output', dest='output',default='',help='Specify output file path')
    return parser.parse_args()


class URLCrawler:
    def __init__(self, urls, output):
        self.urls = urls
        self.output = output
        self.htmls = []
        self.total = []

    def get_html(self):
        #Retrieve the HTMLs by given URLs
        for url in self.urls:
            response = requests.get(url)

            if(response.status_code != 200):
                print(f'Error code {response.status_code} check again the URL')
                exit(1)

            html = response.content.decode()
            self.htmls.append(html)
    
    def retrieve_links(self):
        #Get all url contain on HTML pages
        urls =[]
        for html in self.htmls:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all("a")
            for link in links:
                text_link = str(link.get('href'))
                if('http' in text_link):
                    urls.append(text_link)
        self.total.extend(urls)
        self.total.extend(self.urls)
        self.total = list(set(self.total))


    def write_output(self):
        content = ''
        for link in self.total:
            content = content + link + '\n'
        try:
            with open(self.output, 'x') as file:
                file.write(content)
        except FileExistsError:
            print(f"The file '{self.output}' already exists.")

    def print_result(self):
        for link in self.total:
            print(link)

if __name__ == "__main__":
    args = get_args()
    cr = URLCrawler(args.urls, args.output)
    cr.get_html()
    cr.retrieve_links()
    if(args.output != ''):
        cr.write_output()
    cr.print_result()