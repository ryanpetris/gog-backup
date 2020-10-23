#!/usr/bin/env python

import os


GOG_API_COOKIES = os.environ.get("GOG_API_COOKIES", None)
GOG_LANGUAGES = os.environ.get("GOG_LANGUAGES", "English").split(";")
GOG_PLATFORMS = os.environ.get("GOG_PLATFORMS", "Linux;Windows;Mac").split(";")
GOG_ARCHIVE_DIR = os.environ.get("GOG_ARCHIVE_DIR", None)
