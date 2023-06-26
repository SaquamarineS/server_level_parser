import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import re
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
import time
from keys_enum import CssClasses

OUTPUT_FILE = 'titles.json'


def is_separator(span):
    return span.get('aria-hidden') == "true" and span.text == '·'


def is_not_phone_number(text):
    phone_regex = re.compile(r'\+?\d[\d-]+\d')
    return not phone_regex.match(text)


class GoogleSERPScraper:
    def __init__(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-extensions')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.browser = webdriver.Chrome(options=options)
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
            }
        except WebDriverException as e:
            logging.error(f"An error occurred when initializing the browser: {e}", exc_info=True)

    def __del__(self):
        self.browser.quit()

    def fill_pattern(self, query, oq, aqs, sourceid, ie):
        pattern = r"https://www.google.com/search\?q=([^&]+)&oq=([^&]+)&aqs=([^&]+)&sourceid=([^&]+)&ie=([^&]+)"
        filled_url = f"https://www.google.com/search?q={query}&oq={oq}&aqs={aqs}&sourceid={sourceid}&ie={ie}"
        match = re.match(pattern, filled_url)
        if match:
            return filled_url
        else:
            raise ValueError("Failed to fill the pattern with provided parameters.")

    def get_google_serp_via_search_url(self, search_url):
        response = requests.get(search_url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def get_google_serp_special_sections(self, serp_hrml):
        google_serp_panel_sections = serp_hrml.find_all('div', class_='Gx5Zad xpd EtOod pkphOe')
        if google_serp_panel_sections:
            return google_serp_panel_sections
        else:
            return []

    def print_local_results(self, google_serp_special_sections):
        local_result_titles = []
        local_results = []
        for special_section in google_serp_special_sections:
            if special_section.find_all('div', class_='X7NTVe'):
                local_results = special_section.find_all('div', class_='X7NTVe')
        if local_results:
            i = 0
            for result in local_results:
                print(f"Title number {i}, is pushed to array")
                local_result_titles.append(result.text)
                i += 1
        print(local_result_titles)

    def generate_gmaps_url(self, search_query, latitude, longitude):
        search_query = search_query.replace(' ', '+')
        base_url = "https://www.google.com/maps/search/"
        zoom_level = 10

        return f"{base_url}{search_query}/@{latitude},{longitude},{zoom_level}z"

    def get_link_to_places(self, google_serp_special_sections):
        more_results_link = "was not found"
        for special_section in google_serp_special_sections:
            if special_section.find_all('div', class_='X7NTVe'):
                link_location = special_section.find('div', class_=False)
                for link in link_location.find_all('a', href=True):
                    url = link["href"]
                    more_results_link = url

        return more_results_link

    def extract_number_of_reviews(self, input_string):
        pattern = r"\d+"

        number = int(re.search(pattern, input_string).group())
        return number

    def extract_place_id_from_url(self, url):
        try:
            logging.info("Starting extraction of place ID from URL.")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.path)
            for key in query_params:
                if 'data' in key:
                    data = query_params[key][0]
                    data_parts = data.split('!')
                    for part in data_parts:
                        if part.startswith('19s'):
                            logging.info("Extraction of place ID from URL finished successfully.")
                            return part[3:]
            logging.warning("No place ID found in the provided URL.")
            return None
        except Exception as e:
            logging.error(f"An error occurred in extract_place_id_from_url method: {e}", exc_info=True)
            return None

    def extract_data_id_from_url(self, url):
        try:
            logging.info("Starting extraction of data ID from URL.")
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.path)
            for key in query_params:
                if 'data' in key:
                    data = query_params[key][0]
                    data_parts = data.split('!')
                    for part in data_parts:
                        if part.startswith('1s'):
                            logging.info("Extraction of data ID from URL finished successfully.")
                            return part[2:]
            logging.warning("No data ID found in the provided URL.")
            return None
        except Exception as e:
            logging.error(f"An error occurred in extract_data_id_from_url method: {e}", exc_info=True)
            return None

    def extract_thumbnail_src(self, result):
        try:
            logging.info("Starting extraction of thumbnail source.")
            thumbnail = result.find('img')
            if 'src' in thumbnail.attrs:
                thumbnail_src = thumbnail['src']
            else:
                thumbnail_src = 'No URL is provided'
            logging.info("Extraction of thumbnail source finished successfully.")
            return thumbnail_src
        except Exception as e:
            logging.error(f"An error occurred in extract_thumbnail_src method: {e}", exc_info=True)
            return 'No URL is provided'

    def find_address_container(self, html):
        logging.info("Searching for address container.")
        w4efsd_outer = html.find_all('div', class_=CssClasses.ADDITIONAL_INFO_CLASS.value)
        if len(w4efsd_outer) >= 2:
            w4efsd_inner = w4efsd_outer[1].find('div', class_=CssClasses.ADDITIONAL_INFO_CLASS.value)
            if w4efsd_inner:
                logging.info("Address container found.")
                return w4efsd_inner
        logging.warning("Address container not found.")
        return None

    def get_address_from_spans(self, spans):
        logging.info("Extracting address from spans.")
        for span in spans:
            if span.get('aria-hidden') == "true" and span.text == '·':
                next_span = span.find_next_sibling('span')
                if next_span:
                    logging.info("Address found: %s", next_span.text)
                    return next_span.text
        logging.warning("Address not found in spans.")
        return None

    def extract_address(self, html):
        logging.info("Starting address extraction.")
        w4efsd_inner = self.find_address_container(html)
        if w4efsd_inner:
            spans = w4efsd_inner.find_all('span')
            return self.get_address_from_spans(spans)
        logging.warning("Address extraction failed.")
        return None

    def extract_data_from_result(self, result, id):
        try:
            logging.info("Starting data extraction from result.")
            data_card = {}
            thumbnail_src = self.extract_thumbnail_src(result=result)
            url_to_place = result.find('a', class_=CssClasses.URL_TO_PLACE_CLASS.value)
            data_id = self.extract_data_id_from_url(url_to_place['href'])
            place_id = self.extract_place_id_from_url(url_to_place['href'])
            title = result.find('div', class_=CssClasses.TITLE.value).text
            rating_element = result.find('span', class_=CssClasses.RATING.value)
            rating = rating_element.text if rating_element else "no rating"
            address = self.extract_address(result)
            reviews_element = result.find('span', class_=CssClasses.REVIEWS.value)
            reviews = self.extract_number_of_reviews(reviews_element.text) if reviews_element else "no reviews"

            data_card['title'] = title
            data_card['position'] = id + 1
            data_card['rating'] = rating
            data_card['reviews'] = reviews
            data_card['data_id'] = data_id
            data_card['place_id'] = place_id
            data_card['thumbnail_src'] = thumbnail_src
            data_card['address'] = address if address else "Address is not provided"

            logging.info("Data extraction from result finished successfully.")
            return data_card
        except Exception as e:
            logging.error(f"An error occurred in extract_data_from_result method: {e}", exc_info=True)
            return None

    def scroll_page_down(self, scroll_count=1):
        js_functions = """
    function getScrollableElement() {
    const scrollableElements = document.querySelectorAll('.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd');
    for (const el of scrollableElements) {
        if (el.scrollHeight > el.clientHeight) {
            return el;
        }
    }
    return document.documentElement;
}

function scrollToEndOfScrollableElement(delay, callback) {
    const scrollableElement = getScrollableElement();

  // Scroll to the bottom of the scrollable element
    scrollableElement.scrollTop = scrollableElement.scrollHeight;

  // Wait for the specified delay
    setTimeout(() => {
    // Execute the callback function
        if (typeof callback === 'function') {
            callback();
        }
        }, delay);
    }
"""
        # self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        for _ in range(scroll_count):
            self.browser.execute_script(js_functions + "scrollToEndOfScrollableElement(2000);")
            time.sleep(2)

    def get_places(self, places_link):
        try:
            logging.info("get_places method called with link: %s", places_link)

            titles = []
            self.browser.get(places_link)

            self.scroll_page_down(2)
            logging.info("Page scrolled down.")

            # Get the page source after JavaScript has been executed
            html = self.browser.page_source
            logging.info("Page source retrieved.")

            # Parse the page source with Beautiful Soup
            more_results_soup = BeautifulSoup(html, 'html.parser')
            more_results = more_results_soup.find_all('div', class_=CssClasses.SCROLLABLE_ELEMENT.value)

            if not more_results:
                logging.warning(f"No results found under {CssClasses.SCROLLABLE_ELEMENT.value} class.")
                return titles

            results = more_results[0].find_all('div', class_=CssClasses.ONE_RESULT_CLASS.value)
            if not results:
                results = more_results[0].find_all('div', class_=CssClasses.ONE_RESULT_ALTERNATIVE_CLASS.value)

            if not results:
                logging.warning(
                    f"No results found under {CssClasses.ONE_RESULT_CLASS.value} and {CssClasses.ONE_RESULT_ALTERNATIVE_CLASS.value} classes.")
                return titles

            logging.info("Found %s results.", len(results))

            if len(results) > 20:
                results = results[:20]
                logging.info("Results trimmed to top 20.")

            for index, result in enumerate(results):
                titles.append(self.extract_data_from_result(result, index))
                logging.info("Data extracted from result #%s.", index)

            logging.info("get_places method finished successfully. Found %s places.", len(titles))
            return titles

        except Exception as e:
            logging.error(f"An error occurred in get_places method: {e}", exc_info=True)
            return titles

    def scrape(self, query):
        oq = query.replace(" ", "+")
        aqs = "chrome..69i57j0i512l9.2147j1j7"
        sourceid = "chrome"
        ie = "UTF-8"
        search_url = self.fill_pattern(query, oq, aqs, sourceid, ie)

        # get the Google search results page using the search URL
        soup = self.get_google_serp_via_search_url(search_url)

        # extract the special sections from the search results page
        google_serp_special_sections = self.get_google_serp_special_sections(soup)

        # print the local results
        self.print_local_results(google_serp_special_sections)

        # get the link to the "more results" page
        more_results_link = self.get_link_to_places(google_serp_special_sections)

        # get the titles of the results on the "more results" page
        titles = self.get_places(more_results_link)

        # write the titles to a JSON file
        return self.places_to_json(titles)

    def places_to_json(self, objects):
        data = []
        for object in objects:
            data.append(object)
        with open(OUTPUT_FILE, "w") as outfile:
            json.dump(data, outfile)
        return data

    def scrape_url(self, url):
        soup = self.get_google_serp_via_search_url(url)

        # extract the special sections from the search results page
        google_serp_special_sections = self.get_google_serp_special_sections(soup)

        # print the local results
        self.print_local_results(google_serp_special_sections)

        # get the link to the "more results" page
        more_results_link = self.get_link_to_places(google_serp_special_sections)

        # get the titles of the results on the "more results" page
        titles = self.get_places(more_results_link)

        # write the titles to a JSON file
        return self.places_to_json(titles)
