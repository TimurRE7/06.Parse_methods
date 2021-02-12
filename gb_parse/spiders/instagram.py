import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']

    def __init__(self, login, password, tag_list: list, *args, **kwargs):
        self.tag_list = tag_list
        self.tag_urls = [f'/explore/tags/{tag}' for tag in self.tag_list]
        self.login = login
        self.password = password
        super().__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for tag in self.tag_urls:
                    yield response.follow(tag, callback=self.tag_page_parse)
        print(1)

    def tag_page_parse(self, response):
        print(1)

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", "")[:-1])
