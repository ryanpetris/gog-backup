#!/usr/bin/env python3

from __future__ import annotations

import requests
import requests.models
import requests.sessions

from typing import Any, Dict, List, Mapping, Union


def http_send_raw(url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None, headers: Dict[str, str] = None, stream: bool = False) -> requests.models.Response:
    if not method:
        method = 'GET'

    request = requests.Request(method=method, url=url, params=params, json=body, headers=headers).prepare()

    with requests.sessions.Session() as session:
        response: requests.models.Response = session.send(request, stream=stream)

    return response


def http_send(url: str, method: str = None, params: Dict[str, str] = None, body: Mapping = None, headers: Dict[str, str] = None) -> Union[Mapping, List[Any], Any]:
    response = http_send_raw(url, method=method, params=params, body=body, headers=headers)

    return response.json()
