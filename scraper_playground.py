import datetime
import time
from service.google_serp_scrapper import GoogleSERPScraper
from urllib.parse import parse_qs, urlparse
# scraper = GoogleSERPScraper()

# query = "caffee"
# latitude = "43.4354116"
# longtitude = "-79.6160457"

# url = scraper.generate_gmaps_url(query , latitude=latitude , longitude=longtitude)
# # url = "https://www.enso.security/?utm_term=enso&utm_campaign=BKW+Enso+2022&utm_source=adwords&utm_medium=ppc&hsa_acc=6823131170&hsa_cam=16914160280&hsa_grp=132910165422&hsa_ad=593182702229&hsa_src=g&hsa_tgt=kwd-1284132831&hsa_kw=enso&hsa_mt=b&hsa_net=adwords&hsa_ver=3&gclid=Cj0KCQjwmN2iBhCrARIsAG_G2i6FAVEapYq0ZwCVPVBqGljFhhERvJxmGyvwDwsxjJJo_XsPIYHf8zQaAr1WEALw_wcB"

# print(url)
# result = scraper.get_places(url)
# if result :
#     print("Success", result, len(result))
# else:
#     print("Failure", result)


import asyncio
import aiohttp
import json

# Define the array of coordinates
coordinates = [
    (51.5032702, -0.1487915),
    (51.5052702, -0.1507915),
    (51.5072702, -0.1527915),
    (51.5092702, -0.1547915),
    (51.5112702, -0.1567915)
]
# Define the base URL
base_url = "https://scraperld.herokuapp.com//get_places"
george_url = 'http://localhost:3000/api/scraper/bulkScrape'
george_urlV2 = 'http://localhost:3000/api/scraper/bulkScrapeV2'

# Define the query parameter
query = "Irish Pub"

async def fetch(session, url):
    async with session.get(url) as response:
        data = await response.json()
        return data

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []

        for latitude, longitude in coordinates:
            request_url = f"{base_url}?query={query}&latitude={latitude}&longitude={longitude}"
            print(request_url)
            tasks.append(asyncio.ensure_future(fetch(session, request_url)))

        results = await asyncio.gather(*tasks)

        # Save the results to a new file
        with open("results.json", "w") as outfile:
            json.dump(results, outfile, indent=4)


# Request to George
params = [
    {
        "query": query,
        "latitude": 40.7128 + 0.001 * i,
        "longitude": -74.0060 + 0.001 * i
    }
    for i in range(18)
]

async def fetch_george(session, url, params):
    print(f"Start request with params {params}")
    async with session.post(url, json=params) as response:
        data = await response.json()
        print(f"Result: {data}")
        return data

async def george_bulk_request():
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        result = await fetch_george(session, george_url, params)

        # Save the results to a new file
        with open("results.json", "w") as outfile:
            json.dump(result, outfile, indent=4)
        end_time =time.time()
        duration = end_time - start_time
        print(f"fetch duration is  {duration} seconds for bulk request of {len(params)} bulk elements.")
            
def get_data_id(url):
    data = extract_data_id_from_url(url = url)
    return data

def extract_data_id_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.path)
    print(query_params)

    for key in query_params:
        if 'data' in key:
            data = query_params[key][0]
            data_parts = data.split('!')

            for part in data_parts:
                if part.startswith('19s'):
                    return part[3:]

    return None

# Run the async main function
asyncio.run(george_bulk_request())
# asyncio.run(main())
# url = "https://www.google.com/maps/place/Brampton+books/data=!4m7!3m6!1s0x882b15c79401c85d:0x5ce21ec7351e35df!8m2!3d43.6958155!4d-79.7564732!16s%2Fg%2F11rxsxsjrp!19sChIJXcgBlMcVK4gR3zUeNcce4lw?authuser=0&hl=iw&rclk=1"
# print(get_data_id(url))