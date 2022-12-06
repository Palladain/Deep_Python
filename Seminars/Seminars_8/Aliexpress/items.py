# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AliexpressItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()
    sale_price = scrapy.Field()
    delivery = scrapy.Field()
    rating = scrapy.Field()
