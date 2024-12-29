from atexit import register
from enum import Enum, auto
from functools import wraps
from html.parser import HTMLParser
from itertools import count
from json import JSONDecodeError, load, loads, dump
from time import sleep, time
from typing import Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# parameters

# amount of request attempts before moving on
ATTEMPT_COUNT = 3

# minimum delay in seconds between requests
REQUEST_RATE = 3.0

# user agent used in requests
USER_AGENT = "github.com/cefqrn/cohost-archiver"

# end of parameters


SKIP_INTERVAL = 20


class ParserState(Enum):
    SEARCHING = auto()
    HANDLING = auto()
    DONE = auto()


class DataNotFoundError(ValueError): ...
class DataDecodeError(ValueError):
    def __init__(self, msg, data):
        super().__init__(msg)
        self.data = data


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.state: ParserState = ParserState.SEARCHING
        self.data: Optional[dict] = None

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "id" and v == "__COHOST_LOADER_STATE__":
                if self.state is ParserState.DONE:
                    raise DataNotFoundError("several possible data sources")

                self.state = ParserState.HANDLING

                return

    def handle_data(self, data):
        if self.state is not ParserState.HANDLING:
            return

        self.data = data
        self.state = ParserState.DONE


def parse_data(s):
    parser = Parser()
    parser.feed(s)

    data_s = parser.data
    if data_s is None:
        raise DataNotFoundError("data not found")

    try:
        data = loads(data_s)
    except JSONDecodeError as e:
        raise DataDecodeError("failed to parse data", parser.data) from e

    return data


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

            last_call = current_time

            return f(*args, **kwargs)

        return inner_2

    return inner


@rate_limit(REQUEST_RATE)
def get_interval(cookie: str, start: int):
    url = f"https://cohost.org/rc/liked-posts?refTimestamp=1735491600000&skipPosts={start}"
    try:
        with urlopen(Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Cookie": cookie
                })) as f:
            return f.read().decode()
    except HTTPError as e:
        raise DataNotFoundError(f"failed to fetch data (http status: {e.code})") from e


def get_posts(cookie: str, start: int=0):
    for skip in count(start, SKIP_INTERVAL):
        print(f"getting posts {skip}-{skip+SKIP_INTERVAL-1}")
        for retry_count in range(ATTEMPT_COUNT):
            if retry_count:
                print("retrying...")

            try:
                data_s = get_interval(cookie, skip)
            except DataNotFoundError as e:
                print("failed to fetch data:", e)
                continue

            try:
                data = parse_data(data_s)
            except DataDecodeError as e:
                print("data improperly formatted:", e)
                continue

            try:
                feed = data["liked-posts-feed"]

                yield from feed["posts"]

                pagination_mode = feed["paginationMode"]
                more_pages_forward = pagination_mode["morePagesForward"]
            except KeyError as e:
                print("data improperly formatted:", e)
            else:
                break
        else:
            print(f"could not fetch data for posts past {skip}")
            return

        if not more_pages_forward:
          break


def save_posts(posts):
    with open("posts.json", "w") as f:
        dump(posts, f, indent=2)


with open(".cookie") as f:
    cookie = f.read().strip()

try:
    with open("posts.json") as f:
        posts = load(f)
except FileNotFoundError:
    posts = []

register(save_posts, posts)

last_seen = len(posts)
for post in get_posts(cookie, last_seen):
    posts.append(post)

print("done")
