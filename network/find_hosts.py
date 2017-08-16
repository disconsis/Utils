#!/usr/bin/python3


import threading
import subprocess as proc
import argh
import os
import pickle


def ping(ip, timeout):
    ret = proc.run('ping -c 1 -W {t} {ip}'.format(t=timeout, ip=ip).split(),
                   stdout=proc.DEVNULL).returncode
    return not bool(ret)


def ping_thread_worker(ip, _list, used, timeout):
    ret = ping(ip, timeout)
    if ret == used:
        _list.append(ip)


def main(used: 'Whether to list used hosts or unused ones' =False,
         sort: 'Whether to sort the hosts' =False,
         store: 'Path to file to store hosts in, if not False' ='False',
         timeout: 'Time to wait for hosts' =2):
    host_list = []
    main_thread = threading.currentThread()
    for i in range(2, 255):
        ip = '10.9.11.{i}'.format(i=i)
        threading.Thread(target=ping_thread_worker,
                         args=(ip, host_list, used, timeout)).start()
    for thread in threading.enumerate():
        if thread is main_thread:
            continue
        thread.join()
    if sort is True:
        host_list.sort(key=lambda ip: int(ip.split('.')[-1]))
    if store == 'False':
        if used is True:
            print('Used hosts:')
        else:
            print('Free hosts:')
        print('-'*50)
        for host in host_list:
            print(host)
    else:
        with open(store, 'wb') as fp:
            pickle.dump(host_list, fp)


if __name__ == '__main__':
    argh.dispatch_command(main)
