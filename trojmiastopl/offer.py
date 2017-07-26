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

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Title of offer
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    return html_parser.find(id="ogl-title").text
#
# def get_img_url(offer_markup):
#     """ Searches for images in offer markup
#
#     :param offer_markup: Class "offerbody" from offer page markup
#     :type offer_markup: str
#     :return: Images of offer in list
#     :rtype: list
#     """
#     html_parser = BeautifulSoup(offer_markup, "html.parser")
#     images = html_parser.find_all(rel="fancybox")
#     print(images)
#     output = []
#     for img in images:
#         output.append(img.attrs["href"])
#     #return output

def get_price(offer_markup):
    """ Searches for price on offer page

    Assumes price is in PLN

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Price
    :rtype: int
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    price = html_parser.find(class_="font-4").text
    output = ""
    for char in price:
        if char.isdigit():
            output += char
    return int(output)


def get_surface(offer_markup):
    """ Searches for surface in offer markup

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Surface
    :rtype: float

    :except: When there is no offer surface it will return None
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    surface = html_parser.sup.parent.previous_sibling
    return float(surface.replace(" m2", "").replace("\t", "").replace("\n", "").replace(",", "."))


def parse_description(description_markup):
    html_parser = BeautifulSoup(description_markup, "html.parser").text
    # \xa0 means no-break space symbol
    return html_parser.split("$(function")[0].replace("  ", "").replace("\n", " ").replace("\r", "").replace("\xa0", "")


def get_furnished(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        furniture = html_parser.find(class_="umeblowane").text
        if "tak" in furniture:
            return True
    except:
        return None
    return False


# I know it can be done better. I'll do it soon
def get_floor(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        floor = html_parser.find(class_="pietro").text
        return re.findall(r'\d+', floor)[0]
    except:
        return None


def get_built_date(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        built_date = html_parser.find(class_="rok_budowy").text
        return re.findall(r'\d+', built_date)[0]
    except:
        return None


def get_rooms(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        built_date = html_parser.find(class_="l_pokoi").text
        return re.findall(r'\d+', built_date)[0]
    except:
        return None


def get_floor_count(offer_markup):
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        floor_count = html_parser.find(class_="l_pieter").text
        return re.findall(r'\d+', floor_count)[0]
    except:
        return None


def parse_offer(markup, url):
    """ Parses data from offer page markup

    :param markup: Offer page markup
    :param url: Url of current offer page
    :type markup: str
    :type url: str
    :return: Dictionary with all offer details
    :rtype: dict
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    offer_content = str(html_parser.find(class_="title-wrap"))
    title = get_title(offer_content)
    description = parse_description(str(html_parser.find(class_="ogl-description")))
    offer_content = str(html_parser.find(id="sidebar"))
    price = get_price(offer_content)
    surface = get_surface(offer_content)
    return {
        "title": title,
        "price": price,
        "surface": surface,
        "price/surface": round(price / surface),
        "floor": get_floor(offer_content),
        "rooms": get_rooms(offer_content),
        "built_date": get_built_date(offer_content),
        "furniture": get_furnished(offer_content),
        "floor_count": get_floor_count(offer_content),
        "url": url,
        "description": description
    }


def get_descriptions(parsed_urls):
    """ Parses details of categories

    :param parsed_urls: List of offers urls
    :type parsed_urls: list
    :return: List of details of offers
    :rtype: list
    """
    descriptions = []
    for url in parsed_urls:
        response = get_content_for_url(url)
        try:
            log.debug(url)
            descriptions.append(parse_offer(response.content, url))
        except AttributeError as e:
            log.info("This offer is not available anymore.")
            log.debug("Error: {0}".format(e))
    return descriptions
