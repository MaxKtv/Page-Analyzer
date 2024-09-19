from typing import Dict, Any
from requests import Response
from validators import url as url_validator
from urllib.parse import urlparse, urlunparse, ParseResult
from bs4 import BeautifulSoup


def dictionarize_soup_url(req: Response) -> Dict[str, Any]:
    """
    Fetches the content from the provided URL and parses it to extract
    the title, H1 tag, and meta description.

    Args:
        req (Response): The HTTP response from the web page.

    Returns:
        Dict[str, Any]: A dictionary containing the HTTP
                        status code, title, H1 tag, and meta description
                        of the web page if its value is not None.

    Raises:
        TimeoutError: If there is an issue fetching the URL
                      or if the request times out.
    """

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
    """
    Normalizes the provided dictionary by removing keys with None values
    (excluding 'status_code') and truncating string values
    to a maximum length of 255 characters.

    Args:
        dictionary (Dict[str, Any]): The dictionary to be normalized.

    Returns:
        Dict[str, Any]: The normalized dictionary.

    Raises:
        ValueError: If the 'status_code' key is None.
    """

    normalized_dict = {}

    for key, val in dictionary.items():
        if val is None:
            if key =='status_code':
                raise ValueError("status code cannot be None")
            continue
        elif isinstance(val, str):
            val = val[:255]

        normalized_dict[key] = val

    return normalized_dict


def is_valid_url(url: str) -> bool:
    """
    Validates if the provided URL is well-formed and has
    a length of less than 255 characters.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL is valid, otherwise False.
    """

    return url_validator(url) and len(url) < 255


def normalize_url(url: str) -> str:
    """
    Normalizes the provided URL by removing its
    path, parameters, query, and fragment,
    leaving only the scheme and netloc.

    Args:
        url (str): The URL to be normalized.

    Returns:
        str: The normalized URL with only the scheme and netloc.
    """

    parsed_url = urlparse(url)
    normalized_url = urlunparse(ParseResult(scheme=parsed_url.scheme,
                                            netloc=parsed_url.netloc,
                                            path='',
                                            params='',
                                            query='',
                                            fragment=''))
    return normalized_url
