import scrapy


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    css_query = {
        'brands': 'div.TransportMainFilters_block__3etab a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.blackLink',
        'images': 'div.PhotoGallery_block__1ejQ1 img.PhotoGallery_photoImage__2mHGn',
    }

    data_query = {
        'title': lambda resp: resp.css('div.AdvertCard_advertTitle__1S1Ak::text').get(),
        'price': lambda resp: float(resp.css('div.AdvertCard_price__3dDCr::text').get().replace('\u2009', '')),
        # 'img': lambda resp: resp.css('div.PhotoGallery_block__1ejQ1 img.PhotoGallery_photoImage__2mHGn'),
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
        images = response.css(self.css_query['images'])
        img_links = []
        for img in images:
            img_links.append(img.attrib['src'])
        data['img'] = img_links
        return data
        print(1)

    def img_parse(self, response):
        img_links = response.css(self.css_query['images'])

    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib['href'], callback=callback)
