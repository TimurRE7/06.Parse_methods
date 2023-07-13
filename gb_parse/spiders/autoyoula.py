import scrapy
import re
import base64


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    user_url_start = 'https://youla.ru/user/'
    company_url_start = 'https://auto.youla.ru/cardealers/'

    user_id_regex = re.compile(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar')
    company_name_regex = re.compile(r'cardealers%2F([0-9|a-zA-Z|-]+)%2F%23info')
    phone_number_regex = re.compile(r'phone%22%2C%22([0-9|a-zA-Z]+)%3D%3D%22%2C%22time')

    url_script = 'window.transitState = decodeURIComponent'

    css_query = {
        'brands': 'div.TransportMainFilters_brandsList__2tIkv a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'div.SerpSnippet_titleWrapper__38bZM a.blackLink',
        'images': 'div.PhotoGallery_block__1ejQ1 img.PhotoGallery_photoImage__2mHGn',
        'description': 'div.AdvertCard_descriptionInner__KnuRi',
    }

    data_query = {
        'title': lambda resp: resp.css('div.AdvertCard_advertTitle__1S1Ak::text').get(),
        'price': lambda resp: float(resp.css('div.AdvertCard_price__3dDCr::text').get().replace('\u2009', '')),
        'img': lambda resp: list(
            map(lambda img: img.attrib['src'],
                resp.css(AutoyoulaSpider.css_query['images']))
        ),
        'specifications': lambda resp: dict(
            map(lambda spec: (spec.css('div.AdvertSpecs_label__2JHnS::text').get(),
                              spec.css('div.AdvertSpecs_data__xK2Qx ::text').get()),
                resp.css('div.AdvertSpecs_row__ljPcX'))
        ),
        'description': lambda resp: resp.css('div.AdvertCard_descriptionInner__KnuRi ::text').get(),
        'author_url': lambda resp: AutoyoulaSpider.author_parse(resp),
        'phone': lambda resp: AutoyoulaSpider.phone_parse(resp),
    }

    def parse(self, response, **kwargs):
        brands_links = response.css(self.css_query['brands'])
        yield from self.gen_task(response, brands_links, self.brand_parse)

    def brand_parse(self, response):
        pagination_links = response.css(self.css_query['pagination'])
        yield from self.gen_task(response, pagination_links, self.brand_parse)
        ads_links = response.css(self.css_query['ads'])
        yield from self.gen_task(response, ads_links, self.ads_parse)

    def ads_parse(self, response):
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        if list(data.values())[0]:
            return data

    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib['href'], callback=callback)

    @staticmethod
    def author_parse(response):
        if re.search(AutoyoulaSpider.company_name_regex,
                     response.css(f'script:contains("{AutoyoulaSpider.url_script}")::text').get()):
            author = f'''{AutoyoulaSpider.company_url_start}{re.findall(AutoyoulaSpider.company_name_regex,
                                                                        response.css(f"script:contains('{AutoyoulaSpider.url_script}')::text").get())[0]}'''
        else:
            author = f'''{AutoyoulaSpider.user_url_start}{re.findall(AutoyoulaSpider.user_id_regex,
                                                                     response.css(f"script:contains('{AutoyoulaSpider.url_script}')::text").get())[0]}'''
        return author

    @staticmethod
    def phone_parse(response):
        phone_code = f'''{re.findall(AutoyoulaSpider.phone_number_regex,
                                     response.css(f"script:contains('{AutoyoulaSpider.url_script}')::text").get())[0]}'''
        phone_code += "=" * ((4 - len(phone_code) % 4) % 4)
        phone_bytes = base64.b64decode(base64.b64decode(phone_code))
        phone = phone_bytes.decode('UTF-8')
        return phone
