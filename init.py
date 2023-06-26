from typing import Any
from flask import Flask, jsonify, request
from marshmallow import Schema, fields, validate

from errors import NoPlacesFoundException, ValidationError
from service.google_serp_scrapper import GoogleSERPScraper
import asyncio
from keys_enum import Keys
import traceback
import colorlog

app = Flask(__name__)

# Define the logger
# Define the logger
logger = colorlog.getLogger()

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    reset=True,
    style='%'
))

logger.addHandler(handler)
logger.setLevel(colorlog.INFO)


class ParamsSchema(Schema):
    query = fields.Str(required=True, validate=validate.Length(min=1))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)


params_schema = ParamsSchema()


@app.before_request
def validate_params():
    if request.path == '/get_places':
        errors = params_schema.validate(request.args)
        if errors:
            logger.error(f"Validation error: {errors}")
            request_info = {
                'query': request.args.get('query', ''),
                'latitude': request.args.get('latitude', ''),
                'longitude': request.args.get('longitude', '')
            }
            return jsonify({'errors': errors, 'request_info': request_info}), 400


async def async_scrape(query, url):
    if url:
        scraper = GoogleSERPScraper()
        titles = scraper.scrape_url(url)
    elif query:
        scraper = GoogleSERPScraper()
        titles = scraper.scrape(query)
    else:
        return {'error': 'No query or URL provided.'}, 400

    result = {
        "local_results": titles
    }
    return result


async def scrape_places(query, latitude, longitude):
    try:
        scraper = GoogleSERPScraper()
        result = {}
        result['request_info'] = {
            'query': query,
            'latitude': latitude,
            'longitude': longitude
        }

        places_link = scraper.generate_gmaps_url(query, latitude=latitude, longitude=longitude)
        places_array = scraper.get_places(places_link)
        if (places_array):
            result['places_result'] = scraper.places_to_json(objects=places_array)
            logger.info(
                f"Scraping places for query {query} at latitude {latitude} and longitude {longitude} was successful")
        else:
            logger.error(f"No places were scraped for query {query} at latitude {latitude} and longitude {longitude}")
            raise NoPlacesFoundException('No places were scraped')

        return result
    except NoPlacesFoundException as e:
        logger.error(f"Exception occurred: {e}", exc_info=True)  # This will log the stack trace
        return {'error': 'An error occurred while scraping places', 'request_info': result['request_info']}, 500


@app.route("/get_places", methods=['GET'])
async def get_places():
    query = request.args.get('query')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    result = await asyncio.gather(scrape_places(query=query, latitude=latitude, longitude=longitude))
    return result


@app.errorhandler(404)
def not_found_error(error):
    logger.error('Resource not found', exc_info=True)
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f'An internal error occurred: {error}', exc_info=True)
    return jsonify({'error': f'An internal error occurred {error}'}), 500


app.run()
