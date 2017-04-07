#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import logging
from csv import QUOTE_ALL
from csvkit.py2 import CSVKitDictReader, CSVKitDictWriter
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim
from time import sleep

"""
Logging
"""
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'
LOG_LEVEL = logging.INFO
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# GLOBAL SETTINGS
cwd = os.path.dirname(__file__)
CACHE_PATH = os.path.join(cwd, 'cache')
OUTPUT_PATH = os.path.join(cwd, 'output')
HEADER = ["address", "street", "city", "state", "country", "postalcode",
          "latitude", "longitude"]
CACHE_HEADER = ["address", "latitude", "longitude"]
DEFAULT_WAIT = 2

cache = {}


def persist_cache():
    """
    Persist cache to disk
    """
    with open('%s/cached_locations.csv' % CACHE_PATH, 'w') as fout:
        writer = CSVKitDictWriter(fout, fieldnames=CACHE_HEADER,
                                  quoting=QUOTE_ALL)
        writer.writeheader()
        for k, v in cache.iteritems():
            row = {'address': k, 'latitude': v[1], 'longitude': v[0]}
            writer.writerow(row)


def format_address(row=None):
    """
    Format the addresses into something that may be geocoded
    """
    query = None
    cached_address = None
    QUERY_FIELDS = ['street', 'city', 'state', 'country', 'postalcode']
    # Test for unstructured query
    try:
        if row['address'] and row['address'] != "":
            query = row['address']
            cached_address = row['address']
            return query, cached_address
    except KeyError:
        pass
    query = {}
    address_fields = []
    for field in QUERY_FIELDS:
        try:
            if row[field] and row[field] != "":
                query[field] = row[field]
                address_fields.append(row[field])
        except KeyError:
            pass
    cached_address = '_'.join(address_fields)
    return query, cached_address


def geocode_nominatim(row=None, geocoder=None):
    """geocode based on address"""
    row['latitude'] = None
    row['longitude'] = None
    query, cached_address = format_address(row)
    logger.debug(query)

    if cached_address not in cache:
        try:
            # Give mapBox some rest
            if args.wait:
                sleep(args.wait)
            else:
                sleep(DEFAULT_WAIT)
            location = geocoder.geocode(query, exactly_one=True, timeout=2)
        except GeocoderServiceError:
            location = None
        if location:
            logger.debug("found location for: %s" % query)
            coordinates = [location.longitude, location.latitude]
        else:
            # If we did not find a location set to None and cache to avoid
            # hitting the same error again
            logger.debug("location not found for %s" % query)
            coordinates = [None, None]
    else:
        coordinates = cache[cached_address]

    # Store into cache for reuse
    cache[cached_address] = coordinates

    # update geolocation to the record
    if coordinates:
        row['latitude'] = coordinates[1]
        row['longitude'] = coordinates[0]


def load_geocoded_cache():
    """ Load persisted geocoded locations"""
    try:
        with open('%s/cached_locations.csv' % CACHE_PATH, 'r') as f:
            reader = CSVKitDictReader(f)
            for row in reader:
                cache[row['address']] = [row['longitude'], row['latitude']]
    except IOError:
        # No cache file found
        pass


def run(args):
    try:
        if args.debug:
            logger.setLevel(logging.DEBUG)

        if args.no_cache:
            load_geocoded_cache()

        # Create output
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        # Initialize geocoder
        geocoder = Nominatim()

        with open('%s/output.csv' % OUTPUT_PATH, 'w') as fout:
            writer = CSVKitDictWriter(fout, fieldnames=HEADER,
                                      extrasaction='ignore',
                                      quoting=QUOTE_ALL)
            writer.writeheader()
            with open(args.input, 'r') as f:
                reader = CSVKitDictReader(f)
                logger.info('start processing %s' % args.input)
                for ix, row in enumerate(reader):
                    if (ix + 1) % 100 == 0:
                        logger.debug("processed %s records" % (ix + 1))
                    if args.sample and (ix >= args.sample):
                        break
                    # Geocode
                    geocode_nominatim(row, geocoder)
                    # Write to csv file
                    writer.writerow(row)
                logger.info('finished processing %s' % args.input)
    finally:
        if args.no_cache:
            # Always persist cache file to disk
            persist_cache()


def is_valid_file_path(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    return arg


if __name__ == '__main__':
    # Arguments handling
    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help="input csvfile with addresses to process",
                        metavar="FILE",
                        type=lambda x: is_valid_file_path(parser, x))
    parser.add_argument("-d",
                        "--debug",
                        help="execute with debug level",
                        action="store_true")
    parser.add_argument("-C",
                        "--no-cache",
                        help="don't use cached locations",
                        action="store_false")
    parser.add_argument("-s",
                        "--sample",
                        help="test geolocation on a sample",
                        action="store",
                        type=int)
    parser.add_argument("-w",
                        "--wait",
                        help="wait time between calls to the geocoding service",
                        action="store",
                        type=int)
    args = parser.parse_args()
    run(args)
