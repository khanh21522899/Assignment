import scrapy
import json
import re
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="ReconSpider")
    parser.add_argument("start_url", help="The starting URL for the web crawler")
    return parser.parse_args()


#Build a custom offsite middleware 
class CustomOffsiteMiddleware(OffsiteMiddleware):
    #Overload the shoud follow function to control the spider just follow link with the domain target given
    def should_follow(self, request, spider):
        #If the crawl not have any restriction then this return true
        if not self.host_regex:
            return True
        # Seperate the domain with port to detect whether the domain is in target scope or not
        host = urlparse(request.url).netloc.split(':')[0]
        return bool(self.host_regex.search(host))

class WebReconSpider(scrapy.Spider):
    name = 'ReconSpider'
    
    def __init__(self, start_url, *args, **kwargs):
        super(WebReconSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [urlparse(start_url).netloc.split(':')[0]]
        self.visited_urls = set()
        self.results = {
            'emails': set(),
            'links': set(),
            'external_files': set(),
            'js_files': set(),
            'form_fields': set(),
            'images': set(),
            'videos': set(),
            'audio': set(),
            'comments': set(),
        }
        
    def parse(self, response):
        #apend the current visit link to visited_link set
        self.visited_urls.add(response.url)

        # Only process text responses
        if response.headers.get('Content-Type', '').decode('utf-8').startswith('text'):
            # Extract emails in the content of the current visit link
            emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text))
            #Apend those mail to the result set
            self.results['emails'].update(emails)
        
            # Extract links in achor tag
            links = response.css('a::attr(href)').getall()
            for link in links:
                #Skip mailto link since it has no value in the information we want to retrieve
                if link.startswith('mailto:'):
                    continue
                #parse link in the content
                parsed_link = urlparse(link)
                #if the scheme of link not contain http(s):// then join with the current url
                if not parsed_link.scheme:
                    link = response.urljoin(link)
                #If the link has the same domain with the target url and hasn't appear in the visited_link
                #Recursive parse that link too
                if urlparse(link).netloc == urlparse(response.url).netloc:
                    if link not in self.visited_urls:
                        yield response.follow(link, callback=self.parse)
                #add link that fit the criteria to the result set
                self.results['links'].add(link)
        
            # Extract external files (CSS, PDFs, etc.)
            external_files = response.css('link::attr(href), a::attr(href)').re(r'.*\.(css|pdf|docx?|xlsx?)$')
            for ext_file in external_files:
                self.results['external_files'].add(response.urljoin(ext_file))
        
            # Extract JS files
            js_files = response.css('script::attr(src)').getall()
            for js_file in js_files:
                self.results['js_files'].add(response.urljoin(js_file))
        
            # Extract form fields
            form_fields = response.css('input::attr(name), textarea::attr(name), select::attr(name)').getall()
            self.results['form_fields'].update(form_fields)
        
            # Extract images
            images = response.css('img::attr(src)').getall()
            for img in images:
                self.results['images'].add(response.urljoin(img))
        
            # Extract videos
            videos = response.css('video::attr(src), source::attr(src)').getall()
            for video in videos:
                self.results['videos'].add(response.urljoin(video))
        
            # Extract audio
            audio = response.css('audio::attr(src), source::attr(src)').getall()
            for aud in audio:
                self.results['audio'].add(response.urljoin(aud))
            
            # Extract comments
            comments = response.xpath('//comment()').getall()
            self.results['comments'].update(comments)
        else:
            # For non-text responses, just collect the URL
            self.results['external_files'].add(response.url)
        
        self.log(f"Processed {response.url}")

    def closed(self, reason):
        self.log("Crawl finished, converting results to JSON.")
        # Convert sets to lists for JSON serialization
        for key in self.results:
            self.results[key] = list(self.results[key])
        
        with open('results.json', 'w') as f:
            json.dump(self.results, f, indent=4)

        self.log(f"Results saved to results.json")

def run_crawler(start_url):
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            '__main__.CustomOffsiteMiddleware': 500,
        }
    })
    process.crawl(WebReconSpider, start_url=start_url)
    process.start()

if __name__ == "__main__":
    
    
    args = get_args()
    
    run_crawler(args.start_url)
