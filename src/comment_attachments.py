from network import try_download

from itertools import chain, count
from json import JSONDecodeError, load, loads, dump, dumps
from pathlib import Path
from re import I, search
from string import ascii_letters, digits
import re  # compile

from sys import argv
INPUT_FILE = Path(argv[1])

PATH = Path("attachment")
PATH.mkdir(parents=True, exist_ok=True)

AVATAR_PATH = Path("avatar")
AVATAR_PATH.mkdir(parents=True, exist_ok=True)


UUID_PATTERN = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
PATH_CHAR = fr"[-._~%!$&'()*+,;=:@{ascii_letters}{digits}]"

CDN_URL = re.compile(fr"staging.cohostcdn.org/attachment/{UUID_PATTERN}/{PATH_CHAR}+\.[a-z]+", I)


def get_filename(url):
    m = search(UUID_PATTERN, url, I)
    return m[0]


def get_avatar_filename(url):
    i = url.rfind('/') + 1
    return url[i:]


def handle_avatar(avatar):
    path = AVATAR_PATH / get_avatar_filename(avatar)
    if path.is_file():
        return

    data_b = try_download(cookie, avatar)
    assert data_b is not None

    path.write_bytes(data_b)


attachments = set()
def handle_comment(comment_data):
    comment = comment_data["comment"]

    try:
        poster = comment_data["poster"]
    except KeyError:  # deleted comment with children, body exists but is empty, poster doesn't exist
        pass
    else:
        handle_avatar(poster["avatarURL"])

    for url in CDN_URL.findall(comment["body"]):
        attachments.add("https://" + url)

    for data in comment["children"]:
        handle_comment(data)


cookie = Path(".cookie").read_text().strip()

try:
    with INPUT_FILE.open() as f:
        response = load(f)
except Exception as e:
    print("could not decode", argv[1], "error:", e)
    exit(1)

# ignore if error
if (result := response.get("result")) is None:
    print("no data for", argv[1])
    exit(1)

data = result["data"]

for comment_data in chain.from_iterable(data["comments"].values()):
    handle_comment(comment_data)

for attachment in sorted(attachments):
    path = PATH / get_filename(attachment)
    if path.is_file():
        continue

    data_b = try_download(cookie, attachment)
    if not data_b:
        continue

    path.write_bytes(data_b)
