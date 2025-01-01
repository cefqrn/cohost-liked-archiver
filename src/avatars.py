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


cookie = Path(".cookie").read_text().strip()

with INPUT_FILE.open() as f:
    posts = load(f)

avatars = set()
for post in posts:
    avatars.add(post["postingProject"]["avatarURL"])

for avatar in sorted(avatars):
    path = PATH / get_filename(avatar)
    if path.is_file():
        continue

    data_b = try_download(cookie, avatar)
    assert data_b is not None

    path.write_bytes(data_b)

print("done")
