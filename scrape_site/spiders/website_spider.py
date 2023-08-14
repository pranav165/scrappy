import scrapy
import json
import os
from scrapy.linkextractors import LinkExtractor
import logging

# Getting start_url
# Getting start_url
starting_url = os.environ.get("STARTING_URL")

# Getting Output Folder Directory Path
output_file_path = os.environ.get("OUTPUT_FILE_PATH")

# Read JSON data from a file to get allowed_domains
with open(output_file_path + '/allowed_domains.json') as file:
    json_data = file.read()

# Load JSON data
doms = json.loads(json_data)

pdf_urls_json = []
pdf_urls_json = json.dumps(pdf_urls_json)
pdf_json_file_path = output_file_path + '/json_files/pdf_urls.json'
image_json_file_path = output_file_path + '/json_files/image_urls.json'

# Step 1: Read the existing JSON file
with open(pdf_json_file_path, 'r') as file:
    pdf_urls_data = json.load(file)

# Step 1: Read the existing JSON file
with open(image_json_file_path, 'r') as file:
    image_urls_data = json.load(file)

img_urls_data = []
img_file_path = 'scrape_site/output/json_files/image_urls.json'

class MySpider(scrapy.Spider):
    name = "website_spider"

    allowed_domains = doms  # Specify the allowed domains

    start_urls = [str(starting_url)]
    visited_urls = set()  # Track visited URLs
    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.directory_path = kwargs.get('directory_path')

    def parse(self, response):

        logging.info(f"retrieving url: {response.url}")

        # Add the current URL to visited URLs
        self.visited_urls.add(response.url)

        # Extract all the URLs from the allowed domains
        link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        links = link_extractor.extract_links(response)

        # Process the extracted URLs
        for link in links:
            url = link.url
            if url not in self.visited_urls:  # Check if URL is already visited
                yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        # Add the current URL to visited URLs
        self.visited_urls.add(response.url)

        # Get all of the links from the page
        link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        links = link_extractor.extract_links(response)
        # and images
        image_urls = response.css('img::attr(src)').getall()
        # and pdfs
        pdf_links = response.css('a[href*=".pdf"]::attr(href)').getall()
        #pdf_titles = response.css('a[href*=".pdf"]::attr(data-track-download-title)').getall()

        logging.info(f"-- url: {response.url.split('/', 3)[-1][:30]:<30} | links: {len(links):<5} | images: {len(image_urls):<5} | PDFs: {len(pdf_links):<5}")

        title = response.css('title::text').get()
        body_text = response.css('body').extract()

        # Example: Extracting a specific element from the page
        yield {
            'url': str(response.url),
            'page_title': str(title),
            'html_body': str(body_text)
        }

        # Continue scraping recursively for more URLs
        for link in links:
            url = link.url
            if url not in self.visited_urls:  # Check if URL is already visited
                yield scrapy.Request(url, callback=self.parse_page)

#        for pdf_link, pdf_title in zip(pdf_links, pdf_titles):
        for pdf_link in pdf_links:
            yield response.follow(pdf_link, 
                                  callback=self.save_pdf, 
#                                  meta={'title': pdf_title, 'url': response.url},
                                  meta={'url': response.url},
                                  priority = 100)

        # now find the images
        for image_url in image_urls:
            yield {'url': response.url, 'images': image_url}
            yield response.follow(image_url, callback=self.save_image)

    # This function saves the pdf that it gets in the response
    def save_pdf(self, response):
        pdf_filename = self.directory_path+'/pdfs/' + response.url.split('/')[-1]
        if len(pdf_filename) < 3:
            logging.info(f"got a filename with <3 length at {response.url})")
            return

        logging.info(f"================== saving file: {pdf_filename}")

        pdf_url = {
            'url': response.meta['url'],
#            'pdf_title': response.meta['title'],
            'pdf_url': response.url
            }
        pdf_urls_data.append(pdf_url)
        # Step 3: Write the updated data to the JSON file
        with open(pdf_json_file_path, 'w') as file:
            json.dump(pdf_urls_data, file)

        with open(pdf_filename, 'wb') as f:
            f.write(response.body)

        self.log(f'Saved file {pdf_filename}')

    # This function saves the image that it gets in the response
    def save_image(self, response):
        image_filename = self.directory_path+'/images/' + response.url.split('/')[-1]

        if '.svg' in image_filename or '.png' in image_filename or '.jpg' in image_filename or '.jpeg' in image_filename:

            # Step 2: Append the new dictionary
            image_url = {'image_url': response.url}
            image_urls_data.append(image_url)
            # Step 3: Write the updated data to the JSON file
            with open(image_json_file_path, 'w') as file:
                json.dump(image_urls_data, file)

            with open(image_filename, 'wb') as f:
                f.write(response.body)

        self.log(f'Saved file {image_filename}')