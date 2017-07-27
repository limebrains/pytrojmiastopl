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


@pytest.mark.parametrize("list1", [[[2], [[3], [1]], [4, [0]]]])
def test_flatten(list1):
    result = trojmiastopl.utils.flatten(list1)
    for element in result:
        assert not isinstance(element, list)
