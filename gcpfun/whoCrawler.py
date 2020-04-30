
import scrapy
import datetime as dt
import uuid
from postgresConnection import PostgresConnection

class WHOCrawler(scrapy.Spider):
  name = 'WHOCrawler'
  start_urls = ['https://www.who.int/emergencies/diseases/novel-coronavirus-2019/events-as-they-happen']


  def __init__(self):
    self.localMode = False
    self.all_data = {}
    self.article_limit = 999
    self.dbConn = PostgresConnection()
    self.lastStoredArticleDate = self.dbConn.fetchLatestStoredArticlePublishDateForSource('who')

  def closed(self, reason):
      print("Finished Scraping for WHO")
      self.dbConn.commit()
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
          article_title = article_title.strip()

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
        article_date = article_date.strip()

      published_at = None
      try:
        published_at = dt.datetime.strptime(article_date, '%d %B %Y').replace(microsecond=0)
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
        'article_url': article_link,
        'scrapedAt': now_string,
        'published_at': published_at,
        'content': content
      }


      if self.localMode:
          yield article_dict
      else:
          if not published_at:
              return
              yield {}

          # Insert into Google Cloud SQL
          # First, we need to avoid duplicating articles
          if self.lastStoredArticleDate and self.lastStoredArticleDate >= published_at:
              print("Stopping scraper early, lastStoredArticleDate is", self.lastStoredArticleDate)
              return
              yield {}

          # Storing into database
          print(f'Storing into database: [{article_title}]')
          self.dbConn.insertNewArticle(article_id, article_title, 'WHO', article_dict['source'], article_link, content, 'pending', published_at, 'crawler', 'global', '')
          yield article_dict
