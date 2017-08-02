#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re

from bs4 import BeautifulSoup

from trojmiastopl.utils import get_content_for_url

try:
    from __builtin__ import unicode
except ImportError:
    unicode = lambda x, *args: x

log = logging.getLogger(__file__)


def get_title(offer_markup):
    """ Searches for offer title on offer page

    :param offer_markup: Class "title-wrap" from offer page markup
    :type offer_markup: str
    :return: Title of offer
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    return html_parser.find(id="ogl-title").text.replace("\n", "").replace("  ", "").replace(u'\xa0', u' ')


def get_img_url(offer_markup):
    """ Searches for images in offer markup

    :param offer_markup: Id "gallery" from offer page markup
    :type offer_markup: str
    :return: Images of offer in list
    :rtype: list
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    images = html_parser.find_all(class_="fancybox")
    output = []
    for img in images:
        output.append(img.attrs["href"])
    return output


def get_price(offer_markup):
    """ Searches for price on offer page

    Assumes price is in PLN

    :param offer_markup: Class "title-wrap" from offer page markup
    :type offer_markup: str
    :return: Price
    :rtype: int
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    price = html_parser.find(class_="cena").text
    output = ""
    for char in price:
        if char.isdigit():
            output += char
    return int(output)


def get_surface(offer_markup):
    """ Searches for surface in offer markup

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Surface
    :rtype: float

    :except: When there is no offer surface it will return None
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    surface = html_parser.sup.parent.previous_sibling
    return float(surface.replace(" m2", "").replace("\t", "").replace("\n", "").replace(",", "."))


def get_apartment_type(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    type = html_parser.find(class_="rodzaj_nieruchomosci").contents
    return type[3].text.replace('<div class="dd">', '').replace('</div>', '').replace('  ', '').replace("\n", "")


def parse_description(description_markup):
    """ Searches for offer description

    :param description_markup: Class "ogl-description" from offer page markup
    :type description_markup: str
    :return: Offer description
    :rtype: str
    """
    html_parser = BeautifulSoup(description_markup, "html.parser").text
    # \xa0 means no-break space symbol
    return html_parser.split("$(function")[0].replace("  ", "").replace("\n", " ").replace("\r", "").replace(u'\xa0',
                                                                                                             u' ')


def get_furnished(offer_markup):
    """ Searches if offer is marked as furnished or not

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Information is offer furnished
    :rtype: bool

    :except: If there is no information if offer is furnished it will return None
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        furniture = html_parser.find(class_="umeblowane").text
        if "tak" in furniture:
            return True
    except AttributeError:
        return None
    return False


def parse_flat_data(offer_markup):
    """ Parses flat data from sidebar

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Information about floor, number of rooms, date of built and total count of floors in building
    :rtype: dict
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    flat_data = {"pietro": None, "l_pokoi": None, "rok_budowy": None, "l_pieter": None}
    for element in list(flat_data.keys()):
        current = html_parser.find(class_=element)
        if current is not None:
            correct = current.text
            if "parter" in correct:
                correct = "0"
            flat_data[element] = int(re.findall(r'\d+', correct)[0])
    return flat_data


def parse_offer(markup, url):
    """ Parses data from offer page markup

    :param markup: Offer page markup
    :param url: Url of current offer page
    :type markup: str
    :type url: str
    :return: Dictionary with all offer details
    :rtype: dict

    :except: If there is no offer title anymore - offer got deleted.
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    offer_content = str(html_parser.find(class_="title-wrap"))
    try:
        title = get_title(offer_content)
    except AttributeError as e:
        log.warning("Offer {0} got deleted. Error: {1}".format(url, e))
        pass
    images = get_img_url(str(html_parser.find(id="gallery")))
    description = parse_description(str(html_parser.find(class_="ogl-description")))
    offer_content = str(html_parser.find(id="sidebar"))
    price = get_price(offer_content)
    surface = get_surface(offer_content)
    flat_data = list(parse_flat_data(offer_content).values())
    return {
        "title": title,
        "type": get_apartment_type(offer_content),
        "price": price,
        "surface": surface,
        "price/surface": round(price / surface),
        "floor": flat_data[0],
        "rooms": flat_data[1],
        "built_date": flat_data[2],
        "furniture": get_furnished(offer_content),
        "floor_count": flat_data[3],
        "url": url,
        "description": description,
        "images": images
    }


def get_descriptions(parsed_urls):
    """ Parses details of offers in category

    :param parsed_urls: List of offers urls
    :type parsed_urls: list
    :return: List of details of offers
    :rtype: list
    """
    descriptions = []
    for url in parsed_urls:
        if url is None:
            continue
        response = get_content_for_url(url)
        log.debug(url)
        descriptions.append(parse_offer(response.content, url))
    return descriptions
