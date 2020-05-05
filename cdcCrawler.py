
import scrapy
import datetime as dt
import uuid
from postgresConnection import PostgresConnection

# To run individually
# scrapy runspider cdcCrawler.py -o cdcCrawler.json

class CDCCrawler(scrapy.Spider):
  name = 'CDCCrawler'
  start_urls = ['https://www.cdc.gov/coronavirus/2019-ncov/whats-new-all.html']

  def __init__(self):
    self.localMode = False
    self.all_data = {}
    self.article_limit = 999
    self.dbConn = PostgresConnection()
    self.lastStoredArticleDate = self.dbConn.fetchLatestStoredArticlePublishDateForSource('cdc')

  def closed(self, reason):
      print("Finished Scraping for CDC")
      if not self.localMode:
          self.dbConn.commit()

      # for k,v in self.all_data.iteritems():
      #     print(f"Data [{k}: P{v}]")

  def parse(self, response):

    ul_data = response.css('ul.feed-item-list')[0]

    for item_data in ul_data.css('li'):
      if self.article_limit <= 0:
        break
      self.article_limit -= 1

      article_title = item_data.css('a::text').extract_first()
      article_uri = item_data.css('a::attr("href")').extract_first()
      article_date = item_data.css('span.feed-item-date::text').extract_first()

      if article_uri[-4:] != 'html':
        print('Note: Removing uncrawlable ' + article_uri[-4:] + ' link')
        continue

      article_link = response.urljoin(article_uri)
      now_string = dt.datetime.utcnow().replace(microsecond=0).isoformat()
      article_id = str(uuid.uuid4())
      published_at_string = dt.datetime.strptime(article_date, '%A, %B %d, %Y').replace(microsecond=0).isoformat()
      published_at = dt.datetime.strptime(article_date, '%A, %B %d, %Y').replace(microsecond=0)

      article_dict = {
        'source': 'cdc',
        'articleId': article_id,
        'title': article_title,
        'article_url': article_link,
        'scrapedAt': now_string,
        'published_at': published_at,
      }

      if self.localMode:
          yield scrapy.Request(article_link, callback=self.parse_item_link, cb_kwargs=dict(article_dict=article_dict))
      else:
          yield scrapy.Request(article_link, callback=self.parse_item_link, cb_kwargs=dict(article_dict=article_dict))

  def parse_item_link(self, response, article_dict):
    content = response.css('div.content')
    if not content or len(content) == 0:
        return
        yield {}
    content_data = content[0]
    content_title = content_data.css('h1#content').extract_first()

    content_string = ''
    for content_div in content_data.css('div.syndicate div'):
      for content_p in content_div.css('p *::text'):
        p_string = content_p.get()

        content_string += p_string
        content_string += " "

    if content_string:
      content_string = content_string

    article_dict['content'] = content_string
    article_id = article_dict['articleId']
    published_at = article_dict['published_at']
    article_title = article_dict['title']

    if self.localMode:
        self.all_data[article_id] = article_dict
        yield article_dict
    else:
        if not published_at:
            return
            yield {}

        # Insert into Google Cloud SQL
        # First, we need to avoid duplicating articles

        print('lastStoredArticleDate', self.lastStoredArticleDate)
        print('published_at', published_at)
        if self.lastStoredArticleDate and self.lastStoredArticleDate >= published_at:
            print("Stopping scraper early, lastStoredArticleDate is", self.lastStoredArticleDate)
            return
            yield {}


        # Storing into database
        print(f'Storing into database: [{article_title}]')
        self.dbConn.insertNewArticle(article_id, article_title, 'CDC', article_dict['source'], article_dict['article_url'], content_string, 'pending', published_at, 'crawler', 'country', 'us')
        yield article_dict




# soup = BeautifulSoup(html_doc, 'html.parser')
