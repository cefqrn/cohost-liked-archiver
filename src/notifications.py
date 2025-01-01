from network import try_download

from atexit import register
from itertools import filterfalse, islice, repeat
from json import JSONDecodeError, load, loads, dump
from pathlib import Path

FILENAME = Path("notifications.json")
FILENAME.parent.mkdir(parents=True, exist_ok=True)

# amount of notifications downloaded per request
BATCH_SIZE = 80


def format_request(cursor):
    url = "https://cohost.org/api/v1/trpc/notifications.list?batch=1&input="

    url += "%7B%220%22:%7B"
    
    url += f"%22limit%22:{BATCH_SIZE}"
    if cursor is not None:
        url += ","
        url += f"%22cursor%22:%22{cursor}%22"
    
    url += "%7D%7D"

    return url


def save_notifications(notifications):
    with FILENAME.open("w") as f:
        dump(notifications, f, indent=2)


cookie = Path(".cookie").read_text().strip()

notifications = []
register(save_notifications, notifications)

cursor = None
while True:
    url = format_request(cursor)

    data_b = try_download(cookie, url)
    if data_b is None:
        print("could not download notifications")
        print("failed at cursor:", cursor)

    data = loads(data_b)[0]["result"]["data"]
    notifications.append(data)

    cursor = data["nextCursor"]

    if not data["notifications"]:
        break

print("\ndone")
