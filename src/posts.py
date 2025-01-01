from network import try_download

from itertools import filterfalse, islice, repeat
from json import JSONDecodeError, load, loads, dump
from pathlib import Path

from sys import argv
INPUT_FILE = Path(argv[1])

PATH = Path("posts")
PATH.mkdir(parents=True, exist_ok=True)

# amount of posts downloaded per request
BATCH_SIZE = 50


def get_filename(url):
    i = url.rfind('/') + 1
    return url[i:]


def get_info(post):
    return post["postingProject"]["handle"], post["postId"]


def already_downloaded(post):
    author, post_id = get_info(post)

    filename = PATH / author / f"{post_id}.json"
    return filename.is_file()


def get_comments(cookie, posts):
    url = format_request(posts)

    data_b = try_download(cookie, url)
    if data_b is None:
        raise ValueError(f"could not download from {url}")

    data = loads(data_b)
    for post_data, (author, post_id) in zip(data, map(get_info, posts)):
        path = PATH / author
        path.mkdir(exist_ok=True)

        filename = path / f"{post_id}.json"
        with filename.open("w") as f:
            dump(post_data, f, indent=2)


def format_request(posts):
    url = "https://cohost.org/api/v1/trpc/"
    url += ",".join(repeat("posts.singlePost", len(posts)))
    url += f"?batch={len(posts)}&input="

    url += "%7B"
    url += ",".join(
        f'%22{i}%22:%7B%22handle%22:%22{author}%22,%22postId%22:{post_id}%7D'
        for i, (author, post_id) in enumerate(map(get_info, posts))
    )
    url += "%7D"

    return url


def batched(it, n):
    it = iter(it)
    while t := tuple(islice(it, n)):
        yield t


cookie = Path(".cookie").read_text().strip()

with INPUT_FILE.open() as f:
    posts = load(f)

for p in batched(filterfalse(already_downloaded, posts), BATCH_SIZE):
    get_comments(cookie, p)

print("done")
