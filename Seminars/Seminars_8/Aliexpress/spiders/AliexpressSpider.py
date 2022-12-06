import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urljoin
import re
import json
from Aliexpress.items import AliexpressItem

queries = ['Видеокарта']
API = ''


def get_url(url):
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class AliexpressSpider(scrapy.Spider):
    name = 'AliexpressSpider'
    page = 1

    def start_requests(self):
        for query in queries:
            url = 'https://aliexpress.ru/wholesale?' + urlencode({'g': 'n', 'SearchText': query, 'page': str(self.page)})
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        products =  set()
        for res in response.xpath('//a[contains(@target, _target)]/@href').extract():
            if 'sku_id' in res:
                products.add(res)

        for product in products:
            product_url =  'https://aliexpress.ru' + product
            yield scrapy.Request(url=get_url(product_url), callback=self.parse_product_page)

        self.page += 1
        if self.page <= 1:
            url = urlparse(response.url[-1]) + str(self.page)
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_product_page(self, response):
        item = AliexpressItem()
        title = response.xpath('//h1/text()').extract()
        category = response.xpath('//ol[contains(@class, SnowBreadcrumbs_SnowBreadcrumbs__list__1xzrg)]/li/a/text()').extract()
        price = response.xpath('//div[contains(@class, snow-price_SnowPrice__secondPrice__18x8np)][1]/text()').extract()
        sale_price = response.xpath('//div[contains(@class, snow-price_SnowPrice__mainM__18x8np)][1]/text()').extract()
        delivery = response.xpath('//div[contains(@class, SnowProductDelivery_SnowProductDelivery__item__y5v67)[0]/span[1]/text()').extract()
        rating = response.xpath('//p[contains(@class, SnowReviews_ProductRating__ratingAverage__17pz0)[0]/text()').extract()
        item["title"] = ''.join(title).strip()
        item["category"] = '/'.join(category).strip()
        item["price"] = ''.join(price).strip()
        item["sale_price"] = ''.join(sale_price).strip()
        item["delivery"] = ''.join(delivery).strip()
        item["rating"] = ''.join(rating).strip()
        yield item

