import scrapy
from scrapy.selector import Selector
import json


class ListingsSpider(scrapy.Spider):
    name = 'listings'
    allowed_domains = ['www.centris.ca']
    position = {"startPosition": 0}
    query = {
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [
                {
                    "MatchType": "CityDistrictAll",
                    "Text": "Montréal (All boroughs)",
                    "Id": 5
                }
            ],
            "FieldsValues": [
                {
                    "fieldId": "CityDistrictAll",
                    "value": 5,
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "Category",
                    "value": "Residential",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SellingType",
                    "value": "Rent",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "LandArea",
                    "value": "SquareFeet",
                    "fieldConditionId": "IsLandArea",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 0,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 1500,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                }
            ]
        },
        "isHomePage": True
    }
    uck = {"uc": 0, "uck": "ac973fe9-5ffc-4ca0-82d9-45e1ab6c69f9"}

    def start_requests(self):

        yield scrapy.Request(
            url="https://www.centris.ca/UserContext/UnLock",
            method="POST",
            body=json.dumps(self.uck),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.update_query
        )

    def update_query(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/property/UpdateQuery",
            method="POST",
            body=json.dumps(self.query),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.page_request
        )

    def page_request(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def parse(self, response):

        page_dict = json.loads(response.body)
        page = page_dict.get('d').get('Result').get('html')

        sel = Selector(text=page)

        posts = sel.xpath("//div[@class='shell']")
        print(posts[0].get())

        for post in posts:
            category = post.xpath(
                "normalize-space(.//span[@class='category']/div/text())").get()
            address = ' '.join(post.xpath(
                ".//span[@class='address']/child::node()/text()").getall())
            features = f"""{post.xpath(".//div[@class='cac']/text()").get()} bed {post.xpath(".//div[@class='sdb']/text()").get()} bath"""
            price = post.xpath(".//span[@itemprop='price']/text()").get()
            url = response.urljoin(post.xpath(
                ".//a[@class='a-more-detail']/@href").get())

            yield {
                'category': category,
                'address': address,
                'price': price,
                'features': features,
                'url': url
            }

        count = page_dict.get('d').get('Result').get('count')
        increment_number = page_dict.get('d').get(
            'Result').get('inscNumberPerPage')

        if self.position.get('startPosition') <= count:
            self.position['startPosition'] += increment_number
            yield scrapy.Request(
                url="https://www.centris.ca/Property/GetInscriptions",
                method="POST",
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )
