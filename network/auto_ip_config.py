#!/usr/bin/python3

from find_hosts import ping, main as find_hosts_main
from router_cfg import change_settings as change_router_ip
import os
import pickle
import random
from time import sleep
import logging
import argparse
import threading


HOSTS_FILE_LOC = '/tmp/hosts.pickle'


def test_thread_worker(ip, timeout, _list):
    ret = ping(ip, timeout)
    if ret is True:
        _list.append(ip)


def test(test_ips=['10.1.1.11', '10.1.1.19', '10.1.1.45'], timeout=3):
    "return True if any of the ips in test_ips is pingable"
    main_thread = threading.currentThread()
    working = []
    for ip in test_ips:
        threading.Thread(target=test_thread_worker,
                         args=(ip, timeout, working)).start()
    for thread in threading.enumerate():
        if thread is main_thread:
            continue
        thread.join()
    return bool(len(working))


def change_ip():
    logger = logging.getLogger(__name__)
    logger.info('internet not working')
    working = False
    if os.path.exists(HOSTS_FILE_LOC):
        logger.debug('hosts file found')
        with open(HOSTS_FILE_LOC, 'rb') as fp:
            host_list = pickle.load(fp)
            index_list = list(range(len(host_list)))
            random.shuffle(index_list)
        for index in index_list:
            host = host_list[index]
            change_router_ip(host)
            logger.debug('trying ip {0}'.format(host))
            if test():
                logger.debug('ip {0} free'.format(host))
                logger.info('changed ip to {0}'.format(host))
                working = True
                break
        else:
            logger.debug('no free host in hosts file')
    else:
        logger.debug('no hosts file found')

    if working is False:
        for i in range(2, 255):
            host = '10.9.11.{i}'.format(i=i)
            change_router_ip(host)
            logger.debug('trying ip {0}'.format(host))
            if test():
                logger.debug('ip {0} free'.format(host))
                logger.info('changed ip to {0}'.format(host))
                working = True
                break

    if working is False:
        logger.debug('No free hosts found')


def main(timeout=3):
    logger = logging.getLogger(__name__)
    times_working = 0
    while True:
        if test(timeout=timeout) is False:
            times_working = 0
            change_ip()

        else:
            logger.debug('internet working')
            times_working += 1
            if times_working == 10:
                times_working = 1
            if times_working == 1:
                logger.debug('writing free hosts to file')
                find_hosts_main(used=False, sort=False, store=HOSTS_FILE_LOC,
                                timeout=timeout)
                logger.debug('free hosts written to file')

        sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    if args.verbose is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(levelname)-8s - %(asctime)s - %(message)s',
                        datefmt='%I:%M:%S %p')
    main(timeout=3)
