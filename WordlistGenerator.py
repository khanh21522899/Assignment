import requests
import re
from bs4 import BeautifulSoup
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urls', dest='urls', default=[], nargs='+', help="Specify the URL, provide it along http/https", required=True)
    parser.add_argument('-m', '--min_lenght', dest='min_lenght', type=int, default=0, help="minimum lenght of words, default = 0")
    parser.add_argument('-t', '--top', dest='top', type=int, default=5, help="take top n words, default = 10")
    parser.add_argument('-o','--output', dest='output', default='', help='output file path')
    return parser.parse_args()


class WordGenerator:

    def __init__(self, urls, min_lenght, top, output):
        self.urls = urls
        self.min_lenght = min_lenght
        self.top = top
        self.output = output
        self.wordlist = []
        self.htmls = []
        self.allwords =[]
        self.sortwords =[]
    
    def get_htmls(self):

        htmls = []
        for url in self.urls:
            response = requests.get(url)

            if(response.status_code != 200):
                print(f'Error code {response.status_code} check again the URL')
                exit(1)

            html = response.content.decode()
            htmls.append(html)
        self.htmls = htmls
        
    def retrieve_word(self):
        allwords = []
        for html in self.htmls:
            soup = BeautifulSoup(html, 'html.parser')
            alltext = soup.get_text()
            words = re.findall(r'\w+', alltext)
            allwords.extend(words)
        self.allwords = allwords
    
    def words_count(self):
        word_count = {}
        for word in self.allwords:
            if len(word) < self.min_lenght:
                continue
            word_count[word] = word_count.setdefault(word,0)+1

        sort_words = sorted(word_count.items(), key=lambda item: item[1], reverse=True)
        self.sortwords = sort_words
    
    def generate_wordlist(self):
        self.get_htmls()
        self.retrieve_word()
        self.words_count()
        top_words = []
        sort_words = self.sortwords
        for i in range (self.top):
            top_words.append(sort_words[i][0])
        self.wordlist = top_words
        
    
    def write_output(self):
        content = ''
        for word in self.wordlist:
            content = content + word + '\n'
        try:
            with open(self.output, 'x') as file:
                file.write(content)
        except FileExistsError:
            print(f"The file '{self.output}' already exists.")

    def print_result(self):
        for word in self.wordlist:
            print(word)



if __name__ == "__main__":
    args = get_args()
    wg = WordGenerator(args.urls, args.min_lenght, args.top, args.output)
    wg.generate_wordlist()
    if(args.output != ''):
        wg.write_output()
    wg.print_result()
    