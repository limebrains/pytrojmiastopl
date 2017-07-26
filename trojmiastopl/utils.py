#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

import requests
from scrapper_helpers.utils import caching

from trojmiastopl import BASE_URL

log = logging.getLogger(__file__)


def flatten(container):
    """ Flatten a list

    :param container: list with nested lists
    :type container: list
    :return: list with elements that were nested in container
    :rtype: list
    """
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i


def get_url(category, page=None, **filters):
    url = "/".join([BASE_URL, category])
    if page is not None:
        url += "?strona={0}".format(page)
    return url


@caching
def get_content_for_url(url):
    """ Connects with given url

    If environmental variable DEBUG is True it will cache response for url in /var/temp directory

    :param url: Website url
    :type url: str
    :return: Response for requested url
    """
    response = requests.get(url, allow_redirects=False)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        log.warning('Request for {0} failed. Error: '.format(url, e))
        return None
    return response
