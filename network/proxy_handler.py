#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import threading
import logging
import subprocess as proc
import os
import pickle
from time import sleep
from mako.template import Template
from auto_ip_config import test as test_ip


SAVE_FILE = '/tmp/curr_proxy.pickle'
CONF_TEMPLATE = '/home/ketan/.redsocks/redsocks.conf.template'
CONF_FILE = '/home/ketan/.redsocks/redsocks.conf'


class ProxyEntry():
    def __init__(self, addr, port, user, pwd):
        self.addr = addr
        self.port = port
        self.user = user
        self.pwd = pwd

    def __repr__(self):
        return "proxy ( {0}:{1} {2:<12} )".format(self.addr, self.port,
                                                  self.user, self.pwd)


proxy_list = (
    # feed your proxy list here:
    # ProxyEntry('proxy_addr', 'proxy_port', 'proxy_user', 'proxy_password'),
)
addr_preference = ('10.1.1.19', '10.1.1.45')


def usage_order(proxy_addr):
    url = 'http://{}:8080/squish/?'.format(proxy_addr)
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'html.parser')
    usage_table = soup.table
    rows = usage_table.find_all('tr')[2:-1]
    order = []
    for row in rows:
        proxy_user = row.find_all('td')[0].get_text()
        order.append(proxy_user)
    return order


def find_free_proxies(url='http://icanhazip.com/'):
    def _free_proxies_thread_worker(proxy, url, _list):
        if test_proxy(proxy, url) is True:
            _list.append(proxy)

    logger = logging.getLogger(__name__)
    free_proxies = []
    main_thread = threading.currentThread()
    for proxy in proxy_list:
        threading.Thread(target=_free_proxies_thread_worker,
                         args=(proxy, url, free_proxies)).start()
    for thread in threading.enumerate():
        if thread is not main_thread:
            thread.join()
    if not len(free_proxies):
        logger.critical('no working proxies')
        return None
    return free_proxies


def test_proxy(proxy, url='http://icanhazip.com'):
    logger = logging.getLogger(__name__)
    proxy_url = 'http://{}:{}@{}:{}/'.format(proxy.user, proxy.pwd,
                                             proxy.addr, proxy.port)
    try:
        r = requests.get(url, proxies={'http': proxy_url, 'https': proxy_url})
        r.raise_for_status()
    except Exception as err:
        logger.debug('{} failed'.format(proxy))
        return False
    else:
        if 'Squish - QUOTA EXCEEDED' in r.content.decode('utf-8'):
            logger.debug('{} usage exceeded'.format(proxy))
            return False
        return True


def change_proxy(proxy):
    logger = logging.getLogger(__name__)
    proc.call('pkill redsocks'.split())
    with open(CONF_TEMPLATE, 'r') as fp:
        conf_template = fp.read()
    conf = Template(conf_template).render(proxy_addr=proxy.addr,
                                          proxy_port=proxy.port,
                                          proxy_user=proxy.user,
                                          proxy_pass=proxy.pwd)
    with open(CONF_FILE, 'w') as fp:
        fp.write(conf)
    proc.Popen('redsocks -c {}'.format(CONF_FILE).split())
    logger.warning('changed to {}'.format(proxy))


# TODO: fix
def full_proxy_pref(free_proxies):
    logger = logging.getLogger(__name__)
    if not len(free_proxies):
        logger.critical('no free proxies')
        return None
    proxy_addrs = set(proxy.addr for proxy in free_proxies)
    order = {}
    for proxy_addr in proxy_addrs:
        order[proxy_addr] = usage_order(proxy_addr)
    for addr in addr_preference:
        if addr in proxy_addrs:
            return next(proxy
                        for proxy
                        in free_proxies
                        if proxy.user == order[addr][-1])


def simple_proxy_pref(free_proxies):
    for addr in addr_preference:
        for proxy in free_proxies:
            if proxy.addr == addr:
                return proxy
    return None


def main(url='http://icanhazip.com'):
    logger = logging.getLogger(__name__)
    if os.path.exists(SAVE_FILE):
        logger.debug('found save file')
        try:
            with open(SAVE_FILE, 'rb') as fp:
                curr_proxy = pickle.load(fp)
        except Exception as err:
            os.remove(SAVE_FILE)
            logger.critical('bad save file: {}'.format(err))
        else:
            while not test_ip():
                sleep(0.5)
            if test_proxy(curr_proxy, url) is True:
                logger.debug('current proxy working')
                return
            else:
                logger.warning('current proxy not working')
    while not test_ip():
        sleep(0.5)
    while True:
        free_proxies = find_free_proxies(url)
        if free_proxies is not None:
            break
        sleep(5)
    new_proxy = simple_proxy_pref(free_proxies)
    change_proxy(new_proxy)
    try:
        with open(SAVE_FILE, 'wb') as fp:
            pickle.dump(free_proxies[0], fp)
    except Exception as err:
        logger.critical('failed to write current proxy to file: {}'.format(err))
    else:
        logger.debug('wrote current proxy to file')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(levelname)-8s - %(asctime)s - %(message)s',
                        datefmt='%I:%M:%S %p')
    while True:
        main()
        sleep(2)
