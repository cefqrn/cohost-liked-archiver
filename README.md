## instructions
1. paste cookie (`connect.sid=[...]`) into a file named `.cookie`
2. run scripts from the main directory (not src)

## requirements
* python 3.10+

## scripts
* `notifications.py`: notifications
* `liked.py`: liked posts
* `tags.py <tag>`: posts tagged with `<tag>`
* `attachments.py <filename>`: attachments used in posts (attachment blocks and cdn links in markdown and ask blocks)
* `avatars.py <filename>`: user avatars
* `posts.py <filename>`: more data on posts (eg. comments)
* `comment_attachments.py`: comment attachments and avatars, similar to `attachments.py`

## run order
```
notifications.py
liked.py | tags.py
  ├ attachments.py
  ├ avatars.py
  └ posts.py
      └ comment_attachments.py
```
`tags.py`, `liked.py`, and `notifications.py` don't depend on the output of any of the other scripts.
`attachments.py`, `avatars.py`, and `posts.py` take a filename as an argument and work with the files outputted by `tags.py` and `liked.py`.
`comment_attachments.py` takes a filename as an argument and works with the files outputted by `posts.py`.

## example
```bash
$ python3 src/notifications.py
[...]
$ python3 src/tags.py css crimes
[...]
$ python3 src/attachments.py css_crimes.json
[...]
$ python3 src/avatars.py css_crimes.json
[...]
$ python3 src/posts.py css_crimes.json
[...]
$ python3 src/liked.py
[...]
$ python3 src/posts.py liked.json
[...]
$ find posts -type f -exec python3 src/comment_attachments.py {} \;
[...]
```
