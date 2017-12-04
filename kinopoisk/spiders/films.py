import scrapy
from kinopoisk.items import Movie
from urllib.parse import urlencode, urljoin


def extract_with_xpath(elem, query):
    return elem.xpath(query).extract_first().strip()
        

class TopFilmsSpider(scrapy.Spider):
    name = 'toplist'
    params = { 
        'm_act[decade]': '2000',
        'm_act[num_vote]': '2530',
        'm_act[is_film]': 'on',
        'm_act[is_mult]': 'on',
        'perpage': '200',
        'order': 'rating',
        'page': '1',
    }
    start_urls = ['https://www.kinopoisk.ru/top/navigator/' + urlencode(params)]

    def parse(self, response):
        url = 'https://www.kinopoisk.ru/'
        for elem in response.xpath('//div[@id="itemList"]/div[contains(@id, "tr")]'):
            meta = {}
            name_rus = extract_with_xpath(elem, './/div[@class="name"]/a/text()')
            name_eng = extract_with_xpath(elem, './/div[@class="name"]/span/text()')
            rat_value = extract_with_xpath(elem, './/div[contains(@class,"numVote")]/span/text()')
            num_votes = extract_with_xpath(elem, './/div[contains(@class,"numVote")]/span/span/text()')
            meta['name'] = '{} / {}'.format(name_rus, name_eng)
            meta['rating'] = '{} {}'.format(rat_value, num_votes)
            req_url = urljoin(url, extract_with_xpath(elem, './/div[@class="name"]/a/@href'))
            yield scrapy.Request(req_url, callback=self.parse_image, meta=meta)

        tmp_res = []
        num_page = extract_with_xpath(response, '//div[@class="navigator"]/ul/li/span/text()')
        for elem in response.xpath('//div[@class="navigator"]/ul//li[@class="arr"]'):
            tmp_res.append(elem.xpath('.//a/@href').extract_first())
        last_page = tmp_res[-1].partition('page/')[2].partition('/#')[0]
        
        if int(num_page) < int(last_page):
            yield response.follow(tmp_res[2], callback=self.parse)

    def parse_image(self, response):
        img = extract_with_xpath(response, './/div[@id="photoBlock"]//img/@src')
        yield Movie(
            name=response.meta['name'],
            rating=response.meta['rating'],
            reference = response.url,
            image = img
        )