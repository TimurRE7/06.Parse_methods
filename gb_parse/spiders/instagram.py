import json
import scrapy
import datetime as dt
# from ..items import InstTag, InstPost
from ..items import InstUser, InstFollow, InstFollowers


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']
    api_url = '/graphql/query/'
    query_hash = {
        # 'tag_posts': "9b498c08113f1e09617a1703c22b2f32",
        'follow': "3dec7e2c57367ef3da3d987d89f9dbc8",
        'followers': "5aefa9893005572d237da5068082d8d5",
    }

    # def __init__(self, login, password, tag_list: list, *args, **kwargs):
    #     self.tag_list = tag_list
    #     self.tag_urls = [f'/explore/tags/{tag}' for tag in self.tag_list]
    #     self.login = login
    #     self.password = password
    #     super().__init__(*args, **kwargs)

    def __init__(self, login, password, usr_list: list, *args, **kwargs):
        self.usr_list = usr_list
        self.usr_urls = [f'/{usr}/' for usr in self.usr_list]
        self.login = login
        self.password = password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
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
                # for tag in self.tag_urls:
                #     yield response.follow(tag, callback=self.tag_page_parse)
                for usr in self.usr_urls:
                    yield response.follow(usr, callback=self.usr_page_parse)

    # def tag_page_parse(self, response):
    #     tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
    #     yield InstTag(
    #         date_parse=dt.datetime.utcnow(),
    #         data={
    #             'id': tag['id'],
    #             'name': tag['name'],
    #             'profile_pic_url': tag['profile_pic_url'],
    #         }
    #     )
    #     yield from self.get_tag_posts(tag, response)
    #
    # def tag_api_parse(self, response):
    #     yield from self.get_tag_posts(response.json()['data']['hashtag'], response)
    #
    # def get_tag_posts(self, tag, response):
    #     if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
    #         variables = {
    #             'tag_name': tag['name'],
    #             'first': 100,
    #             'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
    #         }
    #         url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
    #         yield response.follow(
    #             url,
    #             callback=self.tag_api_parse,
    #         )
    #     yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    def usr_page_parse(self, response):
        user_data = self.js_data_extract(response)["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        yield InstUser(date_parse=dt.datetime.utcnow(), data=user_data)
        yield from self.get_api_request(response, user_data)

    def get_api_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                "id": user_data["id"],
                "first": 24,
            }
        url_f = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
        url_fs = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url_f, callback=self.get_api_follow, cb_kwargs={"user_data": user_data})
        yield response.follow(url_fs, callback=self.get_api_followers, cb_kwargs={"user_data": user_data})

    def get_api_follow(self, response, user_data):
        if b"application/json" in response.headers["Content-Type"]:
            data = response.json()["data"]["user"]["edge_follow"]
            yield from self.get_follow_item(user_data, data["edges"])
            if data["page_info"]["has_next_page"]:
                variables = {
                    "id": user_data["id"],
                    "first": 24,
                    "after": data["page_info"]["end_cursor"],
                }
                yield from self.get_api_request(response, user_data, variables)

    def get_api_followers(self, response, user_data):
        if b"application/json" in response.headers["Content-Type"]:
            data = response.json()["data"]["user"]["edge_followed_by"]
            yield from self.get_followers_item(user_data, data["edges"])
            if data["page_info"]["has_next_page"]:
                variables = {
                    "id": user_data["id"],
                    "first": 24,
                    "after": data["page_info"]["end_cursor"],
                }
                yield from self.get_api_request(response, user_data, variables)

    @staticmethod
    def get_follow_item(user_data, follow_users_data):
        for user in follow_users_data:
            yield InstFollow(
                user_id=user_data["id"],
                user_name=user_data["username"],
                follow_id=user["node"]["id"],
                follow_name=user["node"]["username"],
            )

    @staticmethod
    def get_followers_item(user_data, follow_users_data):
        for user in follow_users_data:
            yield InstFollowers(
                user_id=user_data["id"],
                user_name=user_data["username"],
                follower_id=user["node"]["id"],
                follower_name=user["node"]["username"],
            )

    # @staticmethod
    # def get_post_item(edges):
    #     for node in edges:
    #         yield InstPost(
    #             date_parse=dt.datetime.utcnow(),
    #             data=node['node']
    #         )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", "")[:-1])
