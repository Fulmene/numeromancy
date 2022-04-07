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

"""demystify -- A Magic: The Gathering parser."""

import argparse
import logging
import re

import parsing
import card
import data
import test
from sets import MODERN_SETS

logging.basicConfig(level=logging.DEBUG, filename="LOG", filemode="w", encoding="utf-8")
root_logger = logging.getLogger()

stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
root_logger.addHandler(stderr_handler)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='A Magic: the Gathering parser.')
    # TODO argparser.add_argument("-t", "--test", help="Run tests then exit", action="store_true")
    argparser.add_argument("-d", "--debug", help="Enable debug logs on stderr.", action="store_true")
    argparser.add_argument("-n", "--nodownload", help="Disable downloading new data file. Only works if there is already an existing data file.", action="store_true")
    args = argparser.parse_args()
    if args.debug:
        stderr_handler.setLevel(logging.DEBUG)
    if args.nodownload:
        data.no_download = True
    card.load_cards(data.load())
