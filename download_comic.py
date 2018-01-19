#!/usr/bin/env python3

"""Usage:
    download_comic.py <url> [-s <start_id>] -e <end_id> [-d <dir>] --img-id <img_id> [-f] [-z]

Arguments:
    <url>                                   url to comic
    -e <end_id>, --end-id=<end_id>          id for the last page of the comic
    --img-id <id>                           id of the comic img tag

Options:
    -s <start_id>, --start-id=<start_id>    id to start with [default: 1]
    -d <dir>, --dir <dir>                   dir to store images [default: ./]
    -f, --force                             download pages even if the file exists
    -z, --zero                              zero pad the file names

"""
import docopt
import requests
from bs4 import BeautifulSoup
import threading
import os
import re

failed_downloads = set()

def download(_id, args, force=False):
    try:
        if force is False:
            id_regex = re.compile('^{}\.((jpe?|pn)g|pdf)$'.format(str(_id)))
            for _file in os.listdir(args['--dir']):
                if id_regex.fullmatch(_file):
                    raise RuntimeWarning(('{} already exists. '
                           'Skipping download for id {}').format(_file, _id))
        id_url = args['<url>'].format(_id)
        page = requests.get(id_url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
        img_src = soup.find('img', attrs={'id': args['--img-id']})['src']
        img = requests.get(img_src)
        img.raise_for_status()
        fileformat = img_src.split('.')[-1]
        filename = str(_id).zfill(len(str(args['--end-id']))) + '.' + fileformat
        with open(os.path.join(args['--dir'], filename), 'wb') as fp:
            fp.write(img.content)
    except Exception as err:
        print(('[!] Encountered {exception} while processing '
               'id {_id}: {err}'.format(
                   exception=type(err).__name__, _id=_id, err=err)))
        failed_downloads.add(_id)
    else:
        print('[*] Completed download for id {}'.format(_id))


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    downloading_threads = set()
    for i in range(int(args['--start-id']), int(args['--end-id']) + 1):
        t = threading.Thread(
            target=download,
            args=(i, args, args['--force'])
        )
        downloading_threads.add(t)
        t.start()

    for thread in downloading_threads:
        thread.join()

    print('[*] Downloading finished')
    if failed_downloads:
        print('[!] Failed to download the following pages: ', end='')
        print(', '.join(map(str, sorted(failed_downloads))))
