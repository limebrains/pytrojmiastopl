#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from trojmiastopl.category import get_category
from trojmiastopl.offer import get_descriptions

log = logging.getLogger(__file__)

if __name__ == '__main__':
    search_filters = {
        "[filter_float_price:from]": 1000
    }
    parsed_urls = get_category("cos", **search_filters)[:3]
    descriptions = get_descriptions(parsed_urls)
    for element in descriptions:
        log.info("\n")
        print(element)
    # print(parsed_urls)
