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


def parse_region(offer_markup):
    """ Parses region information

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Region of offer
    :rtype: dict
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    parsed_address = html_parser.find(class_="address").find(class_="dd").contents
    output = {"voivodeship": "Pomorskie", "city": None, "district": None}
    output["city"] = str(parsed_address[0]).replace("\xa0", "")
    # Just city
    if len(parsed_address) == 1:
        output["address"] = output["city"]
        return output
    district_parser = BeautifulSoup(str(parsed_address[1]), "html.parser")
    district = district_parser.find("a")
    # City, district, street
    if district is not None and len(parsed_address) > 2:
        output["district"] = district.text
        output["address"] = "{0}, {1}, {2}".format(
            output["city"],
            output["district"],
            str(parsed_address[3]).replace("\xa0", "")
        )
    # City, district
    elif district is not None:
        output["district"] = district.text
        output["address"] = "{0}, {1}".format(
            output["city"],
            output["district"]
        )
    # City, street
    else:
        output["address"] = "{0}, {1}".format(output["city"], str(parsed_address[2]).replace("\xa0", ""))
    return output


def parse_dates_and_id(offer_markup):
    """ Searches for date of creating and date of last update of an offer. Additionally parses offer id number.

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Date added and date updated if found and offer id (id, added, updated)
    :rtype: dict
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    parsed_details = html_parser.find_all("li")
    output = {"updated": None}
    for detail in parsed_details:
        if "numer" in detail.text:
            output["id"] = detail.span.text
        elif "wprowadzenia" in detail.text:
            output["added"] = detail.span.text
        elif "aktualizacja" in detail.text:
            output["updated"] = detail.span.text
    return output


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
    return float(surface.replace("m2", "").replace("\t", "").replace("\n", "").replace(",", ".").replace(" ", ""))


def get_apartment_type(offer_markup):
    """ Searches for apartment type in offer markup

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Apartment type
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    built_type = html_parser.find(class_="rodzaj_nieruchomosci").contents
    return built_type[3].text.replace('<div class="dd">', '').replace('</div>', '').replace('  ', '').replace("\n", "")


def get_available_from(offer_markup):
    """ Searches for available from in offer markup

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Available from
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    try:
        available = html_parser.find(class_="dostepne_od").contents
        return available[3].text.replace('<div class="dd">', '').replace('</div>', '').replace('  ', '').replace("\n",
                                                                                                                 "")
    except AttributeError:
        return None


def get_additional_information(offer_markup):
    """ Searches for additional info and heating type

    :param offer_markup: Class "sidebar" from offer page markup
    :type offer_markup: str
    :return: Additional info with optional heating type
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    found = None
    for item in html_parser.find_all('div', class_="odd"):
        if "informacje" in item.text:
            found = item
            break
    for item in html_parser.find_all('div', class_="even"):
        if "informacje" in item.text:
            found = item
            break
    heating = html_parser.find('div', class_="typ_ogrzewania")
    if found is None and heating is None:
        return
    elif heating is None:
        return found.find(class_="dd").text
    elif found is None:
        return "ogrzewanie " + heating.find(class_="dd").text.replace("  ", "").replace("\n", " ")
    return found.find(class_="dd").text + ", ogrzewanie " + heating.find(class_="dd").text.replace("  ", "").replace(
        "\n", " ")


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
    :return: Information about price, deposit, floor, number of rooms, date of built and
    total count of floors in building
    :rtype: dict
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    flat_data = {"pietro": None, "l_pokoi": None, "rok_budowy": None, "l_pieter": None, "cena": None, "kaucja": None}
    for element in list(flat_data.keys()):
        current = html_parser.find(class_=element)
        if current is not None:
            correct = current.text
            if "parter" in correct:
                correct = "0"
            flat_data[element] = int("".join(re.findall(r'\d+', correct)))
    return flat_data


def parse_poster_name(contact_markup):
    """ Parses poster name

    :param contact_markup: Class "contact-box" from offer page markup
    :type contact_markup: str
    :return: Poster name
    :rtype: str
    """
    html_parser = BeautifulSoup(contact_markup, "html.parser")
    poster_name = html_parser.find(class_="name")
    if poster_name is not None:
        poster_name = poster_name.text.replace("\n", "").replace("  ", "")
    else:
        poster_name = None
    return poster_name


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
    log.debug(url)
    html_parser = BeautifulSoup(markup, "html.parser")
    offer_content = str(html_parser.find(class_="title-wrap"))
    try:
        title = get_title(offer_content)
    except AttributeError as e:
        log.warning("Offer {0} is not available anymore. Error: {1}".format(url, e))
        return
    images = get_img_url(str(html_parser.find(id="gallery")))
    contact_content = str(html_parser.find(class_="contact-box"))
    date_details = str(html_parser.find(class_="ogl-info-wrap"))
    dates_id = parse_dates_and_id(date_details)
    description = parse_description(str(html_parser.find(class_="ogl-description")))
    offer_content = str(html_parser.find(id="sidebar"))
    surface = get_surface(offer_content)
    flat_data = parse_flat_data(offer_content)
    address = parse_region(offer_content)
    return {
        "title": title,
        "offer_id": dates_id["id"],
        "type": get_apartment_type(offer_content),
        "address": address["address"],
        "voivodeship": address["voivodeship"],
        "city": address["city"],
        "district": address["district"],
        "price": flat_data["cena"],
        "deposit": flat_data["kaucja"],
        "surface": surface,
        "price/surface": round(flat_data["cena"] / surface),
        "floor": flat_data["pietro"],
        "floor_count": flat_data["l_pieter"],
        "rooms": flat_data["l_pokoi"],
        "built_date": flat_data["rok_budowy"],
        "available_from": get_available_from(offer_content),
        "furniture": get_furnished(offer_content),
        "additional: ": get_additional_information(offer_content),
        "poster_name": parse_poster_name(contact_content),
        "date_added": dates_id["added"],
        "date_updated": dates_id["updated"],
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
        current_offer = parse_offer(response.content, url)
        if current_offer is not None:
            descriptions.append(current_offer)
    return descriptions
