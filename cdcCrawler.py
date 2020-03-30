from bs4 import BeautifulSoup
import scrapy
import datetime as dt
import uuid

# To run individually
# scrapy runspider whoCrawler.py -o whoCrawler.json

class CDCCrawler(scrapy.Spider):
  name = 'CDCCrawler'
  start_urls = ['https://www.cdc.gov/coronavirus/2019-ncov/whats-new-all.html']

  def __init__(self):
    self.all_data = {}
    self.article_limit = 999

  def closed(self, reason):
      print("Finished Scraping for CDC")
    # for k,v in self.all_data.iteritems():
    #     print("Data [{}: P{}]".format(k,v))

  def parse(self, response):

    ul_data = response.css('ul.feed-item-list')[0]

    for item_data in ul_data.css('li'):
      if self.article_limit <= 0:
        break
      self.article_limit -= 1

      article_title = item_data.css('a::text').extract_first().encode('ascii', 'ignore')
      article_uri = item_data.css('a::attr("href")').extract_first()
      article_date = item_data.css('span.feed-item-date::text').extract_first()

      if article_uri[-4:] != 'html':
        print('Note: Removing uncrawlable ' + article_uri[-4:] + ' link')
        continue

      article_link = response.urljoin(article_uri)
      now_string = dt.datetime.utcnow().replace(microsecond=0).isoformat()
      article_id = str(uuid.uuid4())
      published_at= dt.datetime.strptime(article_date, '%A, %B %d, %Y').replace(microsecond=0).isoformat()

      article_dict = {
        'source': 'cdc',
        'articleId': article_id,
        'title': article_title,
        'articleURL': article_link,
        'scrapedAt': now_string,
        'publishedAt': published_at,
      }

      self.all_data[article_id] = article_dict

      yield scrapy.Request(article_link, callback=self.parse_item_link, cb_kwargs=dict(article_dict=article_dict))


  def parse_item_link(self, response, article_dict):

    content_data = response.css('div.content')[0]
    content_title = content_data.css('h1#content').extract_first()

    content_string = ''
    for content_div in content_data.css('div.syndicate div'):
      for content_p in content_div.css('p *::text'):
        p_string = content_p.get()

        content_string += p_string
        content_string += " "

    if content_string:
      content_string = content_string.encode('ascii', 'ignore')

    article_dict['content'] = content_string
    article_id = article_dict['articleId']

    self.all_data[article_id] = article_dict
    yield article_dict




# soup = BeautifulSoup(html_doc, 'html.parser')
