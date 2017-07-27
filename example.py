#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from trojmiastopl.category import get_category
from trojmiastopl.offer import get_descriptions

log = logging.getLogger(__file__)

if __name__ == '__main__':
    search_filters = {
        "data_wprow": "1w"
    }
    region = "Gdańsk"
    parsed_urls = get_category("nieruchomosci-mam-do-wynajecia",region, **search_filters)[:2]
    descriptions = get_descriptions(parsed_urls)
    for element in descriptions:
        print()
        print(element)
