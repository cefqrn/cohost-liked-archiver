from network import try_download

from itertools import count
from json import JSONDecodeError, load, loads, dump, dumps
from pathlib import Path
from re import I, search
import re  # compile

from sys import argv
INPUT_FILE = Path(argv[1])

PATH = Path("attachment")
PATH.mkdir(parents=True, exist_ok=True)

from string import ascii_letters, digits

UUID_PATTERN = r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
PATH_CHAR = fr"[-._~%!$&'()*+,;=:@{ascii_letters}{digits}]"

CDN_URL = re.compile(fr"staging.cohostcdn.org/attachment/{UUID_PATTERN}/{PATH_CHAR}+\.[a-z]+", I)


def get_filename(url):
    m = search(UUID_PATTERN, url, I)
    return m[0]


cookie = Path(".cookie").read_text().strip()

with INPUT_FILE.open() as f:
    posts = load(f)

attachments = set()
for post in posts:
    for block in post["blocks"]:
        match t := block["type"]:
            case "attachment":
                attachments.add(block["attachment"]["fileURL"])
            case "attachment-row":
                for attachment_block in block["attachments"]:
                    assert attachment_block["type"] == "attachment"
                    attachments.add(attachment_block["attachment"]["fileURL"])
            case "markdown":
                for url in CDN_URL.findall(block["markdown"]["content"]):
                    attachments.add("https://" + url)
            case "ask":
                for url in CDN_URL.findall(block["ask"]["content"]):
                    attachments.add("https://" + url)
            case _:
                raise ValueError(f"unknown block type: {t}")

written = 0
for attachment in sorted(attachments):
    path = PATH / get_filename(attachment)
    if path.is_file():
        continue

    data_b = try_download(cookie, attachment)
    if not data_b:
        continue

    path.write_bytes(data_b)
    written += 1

print((written > 0)*'\n' + "done")
