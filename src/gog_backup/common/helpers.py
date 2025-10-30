#!/usr/bin/env python3

import re


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?!*,.]', ' ', filename)
    filename = re.sub(r'[^\x00-\x7F]+', ' ', filename)
    filename = re.sub(r'[\'"`]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)

    return filename.strip().title()
