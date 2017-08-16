#!/usr/bin/python3


import requests
from bs4 import BeautifulSoup
import argh
from collections import OrderedDict


setting_form_name = {
    'ip_address': 'staip_ipaddr',
    'subnet_mask': 'staip_netmask',
    'default_gateway': 'staip_gateway',
    'mtu_size': 'staip_mtusize',
    'dns_server_1': 'wan_dns1',
    'dns_server_2': 'wan_dns2'
}


def get_soup(router_ip):
    resp = requests.get(
        'http://{ip}/wan.htm'.format(ip=router_ip),
        headers={
            'Referer': 'http://{ip}/wizard_step1_start.htm'.format(ip=router_ip)
        }
    )
    return BeautifulSoup(resp.content, 'html.parser')


def get_form_soup(ip):
    soup = get_soup(ip)
    return soup.find('form', attrs={'action': 'form2Wan.cgi',
                                    'name': 'wan'})


def print_dict(_dict):
    for key in _dict.keys():
        print('{key}: {value}'.format(key=key, value=_dict[key]))


def get_settings(router_ip='192.168.100.1', *settings):
    """Retrieve router settings"""

    if ''.join(settings) == 'all':
        settings = ('ip_address',
                    'subnet_mask',
                    'default_gateway',
                    'mtu_size',
                    'dns_server_1',
                    'dns_server_2')

    form = get_form_soup(router_ip)
    if form is False:
        print('Network error')
        exit(1)

    wan_access_type = form.find('select', attrs={'name': 'wantype'})
    wan_access_type = wan_access_type.find('option', selected='').text.strip()
    assert wan_access_type == 'Static IP', NotImplementedError(
        '''functionality not implemented for non-static ips
        access type found: {0}
        '''.format(wan_access_type)
    )

    setting_values = OrderedDict()
    for setting in settings:
        setting_values[setting] = form.find(
            'input', attrs={'name': setting_form_name[setting]}
        ).get('value')
    return setting_values


@argh.decorators.named('get')
@argh.decorators.arg('settings', choices=['ip_address',
                                          'subnet_mask',
                                          'default_gateway',
                                          'mtu_size',
                                          'dns_server_1',
                                          'dns_server_2',
                                          'all'])
def print_settings(router_ip: 'IP of router' ='192.168.100.1',
                   *settings: 'which settings to get from the router'):
    if 'all' in settings:
        if len(settings) > 1:
            print("can't have both 'all' and other settings")
            exit(1)
        else:
            settings = 'all'
    setting_values = get_settings(router_ip, *settings)
    print_dict(setting_values)


@argh.decorators.named('set')
def change_settings(ipaddr, router_ip: 'IP of router' ='192.168.100.1'):
    soup = get_soup(router_ip)
    setting_values = OrderedDict()
    for field in soup.find_all('input'):
        name = field.get('name')
        if name != 'reset':
            if name == 'staip_ipaddr':
                setting_values[name] = ipaddr
            else:
                setting_values[name] = field.get('value')
                if name == 'wanconn_type':
                    setting_values['wantype'] = '0'
    requests.post('http://{ip}/form2Wan.cgi'.format(ip=router_ip),
                  headers={
                      'Referer': 'http://{ip}/wan.htm'.format(ip=router_ip),
                  },
                  data=setting_values)


if __name__ == '__main__':
    argh.dispatch_commands([print_settings, change_settings])
