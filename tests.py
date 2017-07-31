#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pytest
from bs4 import BeautifulSoup

import trojmiastopl
import trojmiastopl.utils
import trojmiastopl.category
import trojmiastopl.offer

if sys.version_info < (3, 3):
    from mock import mock
else:
    from unittest import mock

SEARCH_URL = "http://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/wi,100,ai,2500_,dw,3d,s,Gda%C5%84sk.html"
OFFER_URL = "http://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/mieszkanie-2-pok-gdansk-kokoszki-od-wrzesnia-ogl60598311.html"


@pytest.mark.parametrize("list1", [[2, [[3], [1]], [4, [0]]]])
def test_flatten(list1):
    result = trojmiastopl.utils.flatten(list1)
    for element in result:
        assert not isinstance(element, list)


@pytest.mark.parametrize("to_decode", ["Mieszkanie", "Dom", "Biuro"])
def test_decode(to_decode):
    assert trojmiastopl.utils.decode_type(to_decode) > 0


response = trojmiastopl.utils.get_content_for_url(SEARCH_URL)
html_parser = BeautifulSoup(response.content, "html.parser")
offers = html_parser.find_all(class_='ogl-head')
parsed_urls = [OFFER_URL]


@pytest.mark.parametrize("payload", [(("id_kat", 104), ("cena[]", 300), ("data_wprow", "1d"))])
def test_get_url_for_filters(payload):
    assert "http://trojmiasto.pl/" in trojmiastopl.utils.get_url_for_filters(payload)


@pytest.mark.parametrize("category,region,filters", [
    ("nieruchomosci-mam-do-wynajecia", "Gdansk", {"data_wprow": "1d", "cena[]": (300, None)}),
])
def test_get_url(category, region, filters):
    with mock.patch("trojmiastopl.utils.get_url_for_filters") as get_url_for_filters:
        get_url_for_filters.return_value = "http://trojmiasto.pl/ogloszenia/nieruchomosci-mam-do-wynajecia/ai,300_,dw,1d,s,Gdansk.html"
        assert trojmiastopl.utils.get_url(category, region, **filters) == \
               "http://trojmiasto.pl/ogloszenia/nieruchomosci-mam-do-wynajecia/ai,300_,dw,1d,s,Gdansk.html"


@pytest.mark.parametrize("test_url", [OFFER_URL])
def test_get_conntent_for_url(test_url):
    assert trojmiastopl.utils.get_content_for_url(test_url)


@pytest.mark.parametrize("page_count", [response.content])
def test_get_page_count(page_count):
    assert trojmiastopl.category.get_page_count(page_count) == 2


@pytest.mark.parametrize("offers", [response.content])
def test_parse_available_offers(offers):
    assert trojmiastopl.category.parse_available_offers(offers)


@pytest.mark.parametrize("offer_url", [
    str(offer) for offer in offers if offer
])
def test_parse_offer_url(offer_url):
    trojmiastopl.category.parse_offer_url(offer_url)


@pytest.fixture
def response_parser():
    return trojmiastopl.utils.get_content_for_url(OFFER_URL).content


@pytest.fixture
def sidebar_parser(response_parser):
    html_parser = BeautifulSoup(response_parser, "html.parser")
    return str(html_parser.find(id='sidebar'))


@pytest.fixture
def title_parser(response_parser):
    html_parser = BeautifulSoup(response_parser, "html.parser")
    return str(html_parser.find(class_='title-wrap'))


@pytest.fixture
def gallery_parser(response_parser):
    html_parser = BeautifulSoup(response_parser, "html.parser")
    return str(html_parser.find(id='gallery'))


@pytest.fixture
def description_parser(response_parser):
    html_parser = BeautifulSoup(response_parser, "html.parser")
    return str(html_parser.find(class_='ogl-description'))


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
def test_parse_description(description_parser):
    assert trojmiastopl.offer.parse_description(description_parser)


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
def test_get_title(title_parser):
    assert trojmiastopl.offer.get_title(title_parser) == "Mieszkanie 2 pok. Gdańsk Kokoszki od września"


def test_get_price(sidebar_parser):
    assert trojmiastopl.offer.get_price(sidebar_parser) == 1200


def test_get_surface(sidebar_parser):
    assert trojmiastopl.offer.get_surface(sidebar_parser) == 42.0


def test_get_img_url(gallery_parser):
    images = trojmiastopl.offer.get_img_url(gallery_parser)
    assert isinstance(images, list)
    for img in images:
        assert "ogloszenia/foto" in img


def test_parse_offer(response_parser):
    assert isinstance(trojmiastopl.offer.parse_offer(response_parser, OFFER_URL), dict)


def test_parse_flat_data(sidebar_parser):
    test = trojmiastopl.offer.parse_flat_data(sidebar_parser)
    assert test["pietro"] == 1
    assert test["l_pokoi"] == 2
    assert test["rok_budowy"] == 2009
    assert test["l_pieter"] == 4


@pytest.mark.parametrize("urls", [parsed_urls])
def test_get_descriptions(urls):
    assert isinstance(trojmiastopl.offer.get_descriptions(urls), list)


@pytest.mark.parametrize("category,region,filters", [
    ("nieruchomosci-mam-do-wynajecia", "Gdansk", {"data_wprow": "1d", "cena[]": (300, None)}),
])
def test_get_category(category, region, filters):
    with mock.patch("trojmiastopl.utils.get_url") as get_url:
        with mock.patch("trojmiastopl.utils.get_content_for_url") as get_content_for_url:
            with mock.patch("trojmiastopl.category.parse_available_offers") as parse_available_offers:
                parse_available_offers.return_value = trojmiastopl.category.parse_available_offers(response.content)
                get_content_for_url.return_value = response
                get_url.return_value = trojmiastopl.utils.get_url
                trojmiastopl.category.get_category(category, region, **filters)
