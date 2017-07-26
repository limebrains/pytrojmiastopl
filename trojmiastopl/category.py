#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

from bs4 import BeautifulSoup

from trojmiastopl import BASE_URL, WHITELISTED_DOMAINS
from trojmiastopl.utils import *

if sys.version_info < (3, 3):
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)


def get_page_count(markup):
    """ Reads page number from trojmiasto.pl search page

    :param markup: trojmiasto.pl search page markup
    :return: Total page number
    :rtype: int
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    return int(html_parser.find(title="ostatnia strona").text)


def parse_offer_url(markup):
    """ Searches for offer links in markup

    :param markup: Search page markup
    :return: Url with offer
    :rtype: str
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    url = html_parser.find('a').attrs['href']
    return url


def parse_available_offers(markup):
    """ Collects all offer links on search page markup

    :param markup: Search page markup
    :return: Links to offer on given search page
    :rtype: list
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    offers = html_parser.find_all(class_='ogl-head')
    parsed_offers = [parse_offer_url(str(offer)) for offer in offers if offer]
    return parsed_offers


def get_category(category, **filters):
    filters = {

    }
    category = "nieruchomosci-mam-do-wynajecia/wi,100,s,Gdańsk.html"
    url = get_url(category, **filters)
    parsed_urls, page = [], 0
    response = get_content_for_url(url)
    page_max = get_page_count(response.content)
    while page < 2 and page < page_max:
        url = get_url(category, page, **filters)
        log.debug(url)
        response = get_content_for_url(url)
        if response.status_code > 300:
            break
        log.info("Loaded page {0} of offers".format(page + 1))
        offers = parse_available_offers(response.content)
        if offers is None:
            break
        parsed_urls.append(offers)
        if page is None:
            page = 1
        page += 1
    parsed_urls = list(flatten(parsed_urls))
    log.info("Loaded {0} offers".format(str(len(parsed_urls))))
    return parsed_urls
