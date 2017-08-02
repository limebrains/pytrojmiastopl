#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from trojmiastopl.category import get_category, get_offers_for_page
from trojmiastopl.offer import get_descriptions

log = logging.getLogger(__file__)

if __name__ == '__main__':
    search_filters = {
        "offer_type": "Mieszkanie",
        "data_wprow": "3d",
        "cena[]": (2000, None)
    }
    parsed_urls = get_category("nieruchomosci-mam-do-wynajecia", "Gdańsk", **search_filters)[:2]
    # parsed_urls = get_offers_for_page("nieruchomosci-mam-do-wynajecia", "Gdańsk", 3, **search_filters)[:2]
    descriptions = get_descriptions(parsed_urls)
    for element in descriptions:
        print()
        print(element)
