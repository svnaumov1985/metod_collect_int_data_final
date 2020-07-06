from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from odd_parcer.spiders.oddsparcer import OddsparcerSpider
from odd_parcer import settings

if __name__ == "__main__":

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(OddsparcerSpider)
    process.start()