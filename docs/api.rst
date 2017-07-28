Introduction
============
pytrojmiastopl supplies two methods to scrape data from www.ogloszenia.trojmiasto.pl website

.. _categories:

======================
Scraping category data
======================
This method scrapes available offer urls from trojmiasto.pl search results with parameters

.. autofunction:: trojmiastopl.category.get_category

It can be used like this:

::

    input_dict = {"cena[]": (300, None)}
    parsed_urls = trojmiastopl.category.get_category("nieruchomosci-mam-do-wynajecia", "Gdańsk", **input_dict)

The above code will put a list of urls containing all the apartments found in the given category into the parsed_url variable

===================
Scraping offer data
===================
This method scrapes all offer details from

.. autofunction:: trojmiastopl.offer.get_descriptions

It can be used like this:

::

    descriptions = trojmiastopl.offer.get_descriptions(parsed_urls)

The above code will put a list of offer details for each offer url provided in parsed_urls into the descriptions variable
