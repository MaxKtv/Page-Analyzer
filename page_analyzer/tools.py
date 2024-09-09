from typing import Dict, Any
from requests import get
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


def dictionarize_soup_url(url: str) -> Dict[str, Any]:
    try:
        req = get(url, timeout=10)
        req.raise_for_status()
    except RequestException as e:
        raise Exception(f"Error fetching the URL: {e}")

    soup = BeautifulSoup(req.content, 'html.parser')

    title = soup.title.get_text(strip=True) if soup.title else None
    h1 = soup.h1.get_text(strip=True) if soup.h1 else None
    meta_description_tag = soup.find('meta', {'name': 'description'})
    description = meta_description_tag.get('content', '').strip() \
        if meta_description_tag else None

    return {
        'status_code': req.status_code,
        'h1': h1,
        'title': title,
        'description': description,
    }
