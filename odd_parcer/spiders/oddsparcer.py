import scrapy
from scrapy.http import HtmlResponse

#ИТОГОМ СКРАПИ ИСПОЛЬЗОВАТЬ НЕ ПОУЛЧИЛОСЬ, Т.К ODDSPORTAL ДИНАМИЧЕСКИ ПОДГРУЖАЕТ ТАБЛИЦУ СТАВОК.
#ПЕРЕДЕЛЫВАЕМ НА SELENIUM

class OddsparcerSpider(scrapy.Spider):

    name = 'oddsparcer'
    allowed_domains = ['oddsportal.com']
    start_urls = ['https://www.oddsportal.com/soccer/']

    def parse(self, response: HtmlResponse):

        elems = response.xpath("//a[@foo='f']/@href")

        for egg in elems:

            yield response.follow(egg.root, callback=self.parce_matches)


    def parce_matches(self, responce: HtmlResponse):

        elems = responce.xpath("//tr[@class='']a/@href")
