import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from centris.spiders.listings import ListingsSpider

process = CrawlerProcess(settings=get_project_settings())
process.crawl(ListingsSpider)
process.start()