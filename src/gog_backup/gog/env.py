#!/usr/bin/env python

import os

GOG_API_COOKIES = os.getenv("GOG_API_COOKIES")
GOG_LANGUAGES = os.getenv("GOG_LANGUAGES", "English").split(";")
GOG_SINGLE_LANGUAGE = bool(os.getenv("GOG_SINGLE_LANGUAGE") or len(GOG_LANGUAGES) == 1)
GOG_PLATFORMS = os.getenv("GOG_PLATFORMS", "Linux;Windows;Mac").split(";")
GOG_ARCHIVE_DIR = os.getenv("GOG_ARCHIVE_DIR")
