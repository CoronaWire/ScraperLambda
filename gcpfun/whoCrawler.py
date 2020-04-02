
import scrapy
import datetime as dt
import uuid


class WHOCrawler(scrapy.Spider):
  name = 'WHOCrawler'
  start_urls = ['https://www.who.int/emergencies/diseases/novel-coronavirus-2019/events-as-they-happen']


  def __init__(self):
    self.all_data = {}
    self.article_limit = 999

  def closed(self, reason):
      print("Finished Scraping for WHO")
    # for k,v in self.all_data.iteritems():
    #     print("Data [{}: P{}]".format(k,v))

  def parse(self, response):

    for item_data in response.css('div#PageContent_C229_Col01 > div.content-block > div'):

      titleIndex = 0
      article_title = None
      titleRetries = 4
      while not article_title and titleIndex <= 4:
        titleIndex += 1
        article_title = item_data.css('h2:nth-child({}) *::text'.format(titleIndex)).get()
        if article_title:
          article_title = article_title.strip().encode('ascii', 'ignore')

      if not article_title:
        continue

      dateIndex = titleIndex + 1
      article_date = item_data.css('p:nth-child({})::text'.format(dateIndex)).get()

      if not article_date:
        dateIndex += 1
        article_date = item_data.css('p:nth-child({})::text'.format(dateIndex)).get()

      if not article_date:
        article_date = item_data.css(':nth-child({}) *::text'.format(dateIndex)).get()

      if article_date is not None:
        article_date = article_date.strip().encode('ascii', 'ignore')

      published_at = None
      try:
        published_at = dt.datetime.strptime(article_date, '%d %B %Y').replace(microsecond=0).isoformat()
      except:
        print("Article date cannot be found")

      content = item_data.css('*:not(:first-child):not(:nth-child({})) ::text'.format(dateIndex+1)).get()
      if content:
        content = content.encode('ascii', 'ignore')

      article_link = response.url.encode('utf-8')
      now_string = dt.datetime.utcnow().replace(microsecond=0).isoformat()
      article_id = str(uuid.uuid4())

      article_dict = {
        'source': 'who',
        'articleId': article_id,
        'title': article_title,
        'articleURL': article_link,
        'scrapedAt': now_string,
        'publishedAt': published_at,
        'content': content
      }

      yield article_dict
