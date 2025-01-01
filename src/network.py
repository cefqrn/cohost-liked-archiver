from functools import wraps
from time import sleep, time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# minimum delay in seconds between requests
REQUEST_RATE = 1.0

# amount of request attempts before moving on
ATTEMPT_COUNT = 3

# user agent used in requests
USER_AGENT = "github.com/cefqrn/cohost-liked-archiver"


class DataNotFoundError(ValueError): ...
class DataDecodeError(ValueError):
    def __init__(self, msg, data):
        super().__init__(msg)
        self.data = data


def rate_limit(limit: float):
    """
    prevent function from getting called
    more than once per limit seconds
    """

    def inner(f):
        last_call = time() - limit

        @wraps(f)
        def inner_2(*args, **kwargs):
            nonlocal last_call

            current_time = time()
            elapsed = current_time - last_call
            if elapsed < limit:
                sleep(limit - elapsed)

            last_call = time()

            return f(*args, **kwargs)

        return inner_2

    return inner


@rate_limit(REQUEST_RATE)
def download(cookie: str, url: str) -> bytes:
    try:
        with urlopen(Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Cookie": cookie
                })) as f:
            return f.read()
    except HTTPError as e:
        raise DataNotFoundError(f"failed to fetch data (http status: {e.code})") from e
    except Exception as e:
        raise DataNotFoundError("failed to fetch data, unknown error:", e) from e


def try_download(cookie: str, url: str):
    print("\x1b[Kdownloading", url, end='\r')
    for retry_count in range(ATTEMPT_COUNT):
        if retry_count:
            print("retrying... ")

        try:
            return download(cookie, url)
        except DataNotFoundError as e:
            print((retry_count == 0)*'\n' + "failed:", e)
            continue

    print("could not download", url)
    return None
