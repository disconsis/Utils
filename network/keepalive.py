#!/usr/bin/python3

import requests
from getpass import getpass
from bs4 import BeautifulSoup
from time import sleep

USERNAME = None
PASSWORD = None


def get_ka(url='http://icanhazip.com'):
    r = requests.get(url, allow_redirects=False)
    if r.status_code == 303:
        ka_url = r.headers['Location']
        return requests.get(ka_url)


def access_ka(ka):
    magic = ka.url.split('?')[-1]
    username = USERNAME
    password = PASSWORD
    url = '/'.join(ka.url.split('/')[:-1]) + '/'
    ka_page = requests.post(url, data={
        '4Tredir': 'http://icanhazip.com',
        'magic': magic,
        'username': username,
        'password': password,
    })
    return ka_page, magic


def get_page():
    ka = get_ka()
    ka_page, magic = access_ka(ka)
    return ka_page, magic


def main():
    get_page()
    page, magic = get_page()
    ret = requests.post(page.url, data={
        '4Tredir': 'http://icanhazip.com',
        'magic': magic,
        'answer': '1',
    })
    return ret


def read_auth():
    global USERNAME
    global PASSWORD
    USERNAME = input('username: ')
    PASSWORD = getpass('password: ')


def newmain():
    ka = main()
    html = ka.content.decode('utf-8').splitlines()
    for line in reversed(html):
        if 'keepalive' in line:
            ka_url = line.split('"')[1]
            break
    while True:
        requests.get(ka_url)
        sleep(60)


if __name__ == '__main__':
    read_auth()
    newmain()
