from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoyoulaItem


def clear_price(item: str):
    try:
        return float(item.replace("\u2009", ''))
    except ValueError:
        return None



class AutoyoulaLoader(ItemLoader):
    default_item_class = AutoyoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
