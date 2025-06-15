#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data, push_data
from pan_ip import generate_loopback, ip_version
import json
import timeit

verbose, debug = True, False


def pan_net_if_lo():
    key = 'N_NET_IF_LOOPBACK'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > Interfaces > Loopback ({0}) with zone and VR assigned".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'lo'
    associations = ('vsys', 'zone', 'vr')

    data = init_data(pre, associations)
    data['dump'].append("<loopback>")

    if 'XPATH_TPL' not in cf:
        print("pan_net_if_lo: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']
    vsys = cf['VSYS']
    zone = cf['IF_LOOPBACK_ZONE']
    vr = cf['IF_LOOPBACK_VR']

    xpath = "{0}/config/devices/entry[@name='{1}']" \
        "/network/interface/loopback/units".format(x, lhost)
    xpath_vsys = "{0}/config/devices/entry[@name='{1}']" \
        "/vsys/entry[@name='{2}']/import/network/interface".format(x, lhost, vsys)
    xpath_zone = "{0}/config/devices/entry[@name='{1}']" \
        "/vsys/entry[@name='{2}']/zone/entry[@name='{3}']/network/layer3".format(x, lhost, vsys, zone)
    xpath_vr = "{0}/config/devices/entry[@name='{1}']" \
        "/network/virtual-router/entry[@name='{2}']/interface".format(x, lhost, vr)

    for asso in ("",) + associations:
        a = "" if asso == "" else "_" + asso
        x = eval('xpath'+a)
        data['xml'+a][0] = data['xml'+a][0] % x
        data['clean_xml'+a][0] = data['clean_xml'+a][0] % x

    ip_list = [''] * n

    if 'IF_LOOPBACK_IP' in cf \
            and cf['IF_LOOPBACK_IP'] is not None \
            and len(cf['IF_LOOPBACK_IP']) > 0:
        ip_list = generate_loopback(cf['IF_LOOPBACK_IP'], n)

    element_format = "<entry name='{0}'/>"

    if len(ip_list) > 0:
        ip_ver = ip_version(ip_list[0])
        if ip_ver == 4:  # IPv4
            element_format = """
              <entry name='{0}'>
                <adjust-tcp-mss>
                  <enable>no</enable>
                </adjust-tcp-mss>
                <ip>
                  <entry name='{1}'/>
                </ip>
              </entry>"""
        elif ip_ver == 6:  # IPv6
            element_format = """
              <entry name='{0}'>
                <ipv6>
                  <address>
                    <entry name='{1}'>
                      <enable-on-interface>yes</enable-on-interface>
                    </entry>
                  </address>
                  <enabled>yes</enabled>
                </ipv6>
                <adjust-tcp-mss>
                  <enable>no</enable>
                </adjust-tcp-mss>
              </entry>"""

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    for if_i in range(n):
        if_name = "loopback.{0}".format(if_i + cf['IF_LOOPBACK_NAME_i'])

        element = element_format.format(if_name, ip_list[if_i])
        clean_element = f"@name='{if_name}' or "

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        element = f"<member>{if_name}</member>"
        clean_element = f"text()='{if_name}' or "

        for asso in associations:
            data['xml_' + asso].append(element)
            data['clean_xml_' + asso].append(clean_element)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        count = if_i + 1

        if n > cf['LARGE_N'] and count % s == 0:
            print("{:.0%}".format(count / n), end="", flush=True)

    data['clean_xml'].append("@name='_z']")
    for asso in associations:
        data['clean_xml_' + asso].append("text()='_z']")

    data['dump'].append("</loopback>")

    # print(json.dumps(data, indent=4))
    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_net_if_lo()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
