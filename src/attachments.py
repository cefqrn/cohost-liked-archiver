from network import try_download

from itertools import count
from json import JSONDecodeError, load, loads, dump, dumps
from pathlib import Path
from re import search, I

from sys import argv
INPUT_FILE = Path(argv[1])

PATH = Path("attachment")
PATH.mkdir(parents=True, exist_ok=True)


def get_filename(url):
    m = search(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}", url, I)
    return m[0]


cookie = Path(".cookie").read_text().strip()

with open(".cookie") as f:
    cookie = f.read().strip()

with INPUT_FILE.open() as f:
    posts = load(f)

attachments = set()
for post in posts:
    for block in post["blocks"]:
        if block["type"] != "attachment":
            continue
        
        attachments.add(block["attachment"]["fileURL"])

for attachment in sorted(attachments):
    path = PATH / get_filename(attachment)
    if path.is_file():
        continue

    data_b = try_download(cookie, attachment)
    assert data_b is not None

    path.write_bytes(data_b)

print("done")
