#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from trojmiastopl.category import get_category
from trojmiastopl.offer import get_descriptions

log = logging.getLogger(__file__)

if __name__ == '__main__':
    search_filters = {
        "offer_type": "Mieszkanie",
        "data_wprow": "3d",
        "cena[]": (2000, None)
    }
    parsed_urls = get_category("nieruchomosci-mam-do-wynajecia", "Gdańsk", **search_filters)[:3]
    descriptions = get_descriptions(parsed_urls)
    for element in descriptions:
        print()
        print(element)
