from typing import Dict, Any
from requests import get as get_request
from validators import url as url_validator
from urllib.parse import urlparse, urlunparse, ParseResult
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


def dictionarize_soup_url(url: str) -> Dict[str, Any]:
    try:
        req = get_request(url, timeout=10)
        req.raise_for_status()
    except RequestException as e:
        raise TimeoutError(f"Error fetching the URL: {e}")

    soup = BeautifulSoup(req.content, 'html.parser')

    title = soup.title.get_text(strip=True) if soup.title else None
    h1 = soup.h1.get_text(strip=True) if soup.h1 else None
    meta_description_tag = soup.find('meta', {'name': 'description'})
    description = meta_description_tag.get('content', '').strip() \
        if meta_description_tag else None

    raw_dict = {
        'status_code': req.status_code,
        'h1': h1,
        'title': title,
        'description': description,
    }

    normalized_dict = normalize_dict(raw_dict)

    return normalized_dict


def normalize_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    key_to_del = []

    for key, val in dictionary.items():

        if val is None:
            if key == 'status_code':
                raise ValueError("status code cannot be None")
            key_to_del.append(key)

        elif isinstance(val, str) and len(val) > 255:
            dictionary[key] = val[:255]

    for key in key_to_del:
        del dictionary[key]

    return dictionary


def validate_url(url: str) -> bool:
    return url_validator(url) and len(url) < 255


def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    normalized_url = urlunparse(ParseResult(scheme=parsed_url.scheme,
                                            netloc=parsed_url.netloc,
                                            path='',
                                            params='',
                                            query='',
                                            fragment=''))
    return normalized_url
