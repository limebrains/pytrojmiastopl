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
    parsed_urls[2]="http://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/rukosin-rukosin-11500-m2-ogl60624149.html"
    descriptions = get_descriptions(parsed_urls)
    for element in descriptions:
        print()
        print(element)
