# This file is part of Demystify.
#
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2012 Benjamin S Wolf
#
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

"""data -- Demystify library for loading and updating card data."""

import datetime
import json
import logging
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

import progressbar

_logger = logging.getLogger(__name__)

DATADIR = os.path.join(Path(__file__).parents[1], "data")
OUTPUTDIR = os.path.join(Path(__file__).parents[1], "output")
CACHEDIR = os.path.join(DATADIR, "cache")
DEFAULT_CARDS_JSON = "scryfall-default-cards.json"
JSONCACHE = os.path.join(CACHEDIR, DEFAULT_CARDS_JSON)
METADATA = os.path.join(CACHEDIR, "scryfall.metadata")

## Scryfall Client ##

_last_req = datetime.datetime.min

def send_req(req):
    """ Ratelimits 151 ms between requests. """
    n = datetime.datetime.now()
    global _last_req
    if n - _last_req < datetime.timedelta(milliseconds=150):
        time.sleep(.151)
    _last_req = datetime.datetime.now()
    req.add_header('User-Agent', r'numeromancy/0.0.1')
    req.add_header('Accept', r'application/json;q=0.9,*/*;q=0.8')
    return urllib.request.urlopen(req)

def get_metadata(data_type="default_cards"):
    """ Grab the bulk-data info for the oracle cards. """
    req = urllib.request.Request("https://api.scryfall.com/bulk-data")
    try:
        with send_req(req) as response:
            j = json.load(response)
    except urllib.error.URLError as e:
        _logger.error("Could not download bulk-data info: {}".format(e))
        return
    for obj in j["data"]:
        if obj["type"] == data_type:
            return obj
    else:
        _logger.error("Help I don't have pagination implemented!")

def save_metadata(metadata, metadata_file=METADATA):
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def load_cached_metadata(metadata_file=METADATA):
    if os.path.exists(metadata_file):
        with open(metadata_file) as f:
            return json.load(f)
    return {}

def download(filename=JSONCACHE, metadata=None):
    """ Download the file. """
    if not metadata:
        metadata = get_metadata()
        if not metadata:
            # Bail, since we get the URI from the metadata.
            return False

    req = urllib.request.Request(metadata["download_uri"])
    try:
        with send_req(req) as response:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename + ".tmp", 'wb') as f:
                block_size = 8192
                pbar = progressbar.DataTransferBar().start()
                count = 0
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    count += 1
                    pbar.update(value=count * block_size)
                pbar.finish()
                os.rename(filename + ".tmp", filename)
                save_metadata(metadata)
                return True
    except urllib.error.URLError as e:
        _logger.error("Error retrieving JSON file: {}".format(e))
        return False

def maybe_download(filename=JSONCACHE):
    """ Download the file or use the cached copy. """
    if not os.path.exists(filename):
        print("JSON file not found, downloading.")
        return download(filename)
    age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            os.path.getmtime(filename))
    # We only need to download new data when a new set releases
    # so two weeks seems reasonable enough
    if age < datetime.timedelta(weeks=2):
        print("Using recent JSON file.")
        return True
    metadata = get_metadata()
    if not metadata:
        print("Could not connect to the server, using cached JSON file.")
        return True
    m2 = load_cached_metadata()
    if not m2:
        print("No saved metadata, redownloading JSON.")
        return download(filename, metadata)
    # These will not be exactly equal since the timestamp updates daily.
    # Zipped file size will be the most telling, esp. when new cards are added.
    # URIs in objects shouldn't change, so it should be the case that only
    # content updates change the file size.
    if metadata["size"] == m2["size"]:
        print("Using unchanged JSON file.")
        return True
    print("Redownloading due to compressed file size change: {} => {}"
              .format(m2["size"], metadata["size"]))
    return download(filename, metadata)

## Loader ##

def load(filename=JSONCACHE, no_download=False):
    """ Load the cards from the Scryfall Oracle JSON file. """
    if no_download or not maybe_download(filename):
        if os.path.exists(filename):
            print("Falling back to existing JSON file.")
        else:
            _logger.critical("Failed to get JSON file.")
            return {}
    with open(filename) as f:
        j = json.load(f)
    _logger.debug(f"Loaded {len(j)} objects from {filename}.")
    return j
