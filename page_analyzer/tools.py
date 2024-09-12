from typing import Dict, Any
from requests import get as get_request
from validators import url as url_validator
from urllib.parse import urlparse, urlunparse, ParseResult
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


def dictionarize_soup_url(url: str) -> Dict[str, Any]:
    try:
        req = get_request(url, timeout=3000)
        req.raise_for_status()
    except RequestException as e:
        raise RequestException(f"Error fetching the URL: {e}")

    soup = BeautifulSoup(req.content, 'html.parser')

    title = soup.title.get_text(strip=True) if soup.title else None
    h1 = soup.h1.get_text(strip=True) if soup.h1 else None
    meta_description_tag = soup.find('meta', {'name': 'description'})
    description = meta_description_tag.get('content', '').strip() \
        if meta_description_tag else None

    result = {
        'status_code': req.status_code,
        'h1': h1,
        'title': title,
        'description': description,
    }

    for value in result.values():
        normalize_values(value)

    return result


def normalize_values(val: Any) -> None:
    if isinstance(val, str) and len(val) >= 255:
        val = slice(0, 254)


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
