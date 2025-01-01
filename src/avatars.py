from network import try_download

from json import load
from pathlib import Path

from sys import argv
INPUT_FILE = Path(argv[1])

PATH = Path("avatar")
PATH.mkdir(parents=True, exist_ok=True)


def get_filename(url):
    i = url.rfind('/') + 1
    return url[i:]


def handle_post(post):
    avatars.add(post["postingProject"]["avatarURL"])


cookie = Path(".cookie").read_text().strip()

with INPUT_FILE.open() as f:
    posts = load(f)

avatars = set()
for post in posts:
    handle_post(post)
    for shared_post in post["shareTree"]:
        handle_post(shared_post)

written = 0
for avatar in sorted(avatars):
    path = PATH / get_filename(avatar)
    if path.is_file():
        continue

    data_b = try_download(cookie, avatar)
    assert data_b is not None

    path.write_bytes(data_b)
    written += 1

print((written > 0)*'\n' + "done")
