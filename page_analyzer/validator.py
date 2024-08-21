from validators import url as url_validator

def is_valid_url(url):
    if url_validator(url) and len(url) < 255:
        return url
    else:
        raise ValueError("Invalid URL")
