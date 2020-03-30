
import scrapy
from scrapy.crawler import CrawlerProcess
import json
from cdcCrawler import CDCCrawler
from whoCrawler import WHOCrawler
from scrapy.utils.project import get_project_settings


def lambda_handler(event, context):
    print("Starting lambda_handler...")

    crawlers = [CDCCrawler, WHOCrawler]

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    for Crawler in crawlers:
        print("Starting crawing for ", Crawler.name)
        process.crawl(Crawler)

    process.start()  # the script will block here until the crawling is finished

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == "__main__":
    result = lambda_handler(None, None)
    print("Result returned")
    print(result)
