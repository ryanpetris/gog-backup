#!/usr/bin/env python

import os

GOG_API_COOKIES = os.getenv("GOG_API_COOKIES")
GOG_LANGUAGES = os.getenv("GOG_LANGUAGES", "English").split(";")
GOG_PLATFORMS = os.getenv("GOG_PLATFORMS", "Linux;Windows;Mac").split(";")
GOG_ARCHIVE_DIR = os.getenv("GOG_ARCHIVE_DIR")
