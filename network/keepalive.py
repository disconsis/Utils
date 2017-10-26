#!/usr/bin/python3

import requests
from getpass import getpass
from bs4 import BeautifulSoup
from time import sleep

# change these to avoid reading from stdin each time
USERNAME = None
PASSWORD = None

TIMEOUT = 60  # seconds
TEST_URL = 'http://icanhazip.com'


def get_auth_page():
    page = requests.get(TEST_URL, allow_redirects=False)
    if page.status_code == 303:
        auth_url = r.headers['Location']
        auth_page = requests.get(auth_url)
        return auth_page


def authorize(auth_page):
    magic = auth_page.url.split('?')[-1]
    action_url = '/'.join(ka.url.split('/')[:-1]) + '/'
    page = requests.post(url, data={
        '4Tredir': TEST_URl,
        'magic': magic,
        'username': USERNAME,
        'password': PASSWORD,
    })
    return page, magic


def get_terms_page():
    auth_page = get_auth_page()
    terms_page, magic = authorize(auth_page)
    return terms_page, magic


def agree_terms():
    get_terms_page()
    terms_page, magic = get_terms_page()
    keepalive_page = requests.post(terms_page.url, data={
        '4Tredir': 'http://icanhazip.com',
        'magic': magic,
        'answer': '1',
    })
    return keepalive_page


def keepalive_loop():
    ka_page = agree_terms()
    html = ka_page.content.decode('utf-8').splitlines()
    for line in reversed(html):
        if 'keepalive' in line:
            ka_url = line.split('"')[1]
            break
    while True:
        requests.get(ka_url)
        sleep(TIMEOUT)


def read_auth():
    global USERNAME
    global PASSWORD
    if USERNAME is None:
        USERNAME = input('username: ')
    else:
        print('username:', USERNAME)
    if PASSWORD is None:
        PASSWORD = getpass('password: ')


if __name__ == '__main__':
    read_auth()
    keepalive_loop()
