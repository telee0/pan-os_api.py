#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_ip import generate_ip, ip_version
import timeit

verbose, debug = True, False


def pan_net_if_eth():
    key = 'N_NET_IF_ETHERNET'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]
    m = len(cf['IF_ETHERNET_LIST'])

    print("\nNetwork > Interfaces > Ethernet ({1} x {0}) with zone and VR assigned".format(n, m), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'eth'
    associations = ('vsys', 'zone', 'vr')

    data = init_data(pre, tuple([f"{i}" for i in range(1, m + 1)]) + associations)
    data['dump'].append("<ethernet>")

    if 'XPATH_TPL' not in cf:
        print("pan_net_if_eth: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']
    vsys = cf['VSYS']
    zone = cf['IF_ETHERNET_ZONE']
    vr = cf['IF_ETHERNET_VR']

    xpath_vsys = "{0}/config/devices/entry[@name='{1}']" \
                 "/vsys/entry[@name='{2}']/import/network/interface".format(x, lhost, vsys)
    xpath_zone = "{0}/config/devices/entry[@name='{1}']" \
                 "/vsys/entry[@name='{2}']/zone/entry[@name='{3}']/network/layer3".format(x, lhost, vsys, zone)
    xpath_vr = "{0}/config/devices/entry[@name='{1}']" \
               "/network/virtual-router/entry[@name='{2}']/interface".format(x, lhost, vr)

    for asso in associations:
        a = "_" + asso
        xpath = eval('xpath'+a)
        data['xml'+a][0] = data['xml'+a][0] % xpath
        data['clean_xml'+a][0] = data['clean_xml'+a][0] % xpath

    # static variables in the loop
    #
    nm = n * m
    s = nm // 10  # increment per slice: 10%, 20%, etc..

    ip_list = [''] * nm

    if 'IF_ETHERNET_IP' in cf \
            and cf['IF_ETHERNET_IP'] is not None \
            and len(cf['IF_ETHERNET_IP']) > 0:
        ip_list = generate_ip(cf['IF_ETHERNET_IP'], nm, 1)

    element_format = "<entry name='{0}'/>"
    address_ipv4 = address_ipv6 = ""

    if len(ip_list) > 0:
        ip_ver = ip_version(ip_list[0])
        if ip_ver == 4:  # IPv4
            address_ipv4 = """
                        <ip>
                          <entry name='{1}'/>
                        </ip>"""
        elif ip_ver == 6:  # IPv6
            address_ipv6 = """
                      <address>
                        <entry name="{1}">
                          <advertise>
                            <enable>no</enable>
                            <valid-lifetime>2592000</valid-lifetime>
                            <preferred-lifetime>604800</preferred-lifetime>
                            <onlink-flag>yes</onlink-flag>
                            <auto-config-flag>yes</auto-config-flag>
                          </advertise>
                          <enable-on-interface>yes</enable-on-interface>
                        </entry>
                      </address>
                      <enabled>yes</enabled>"""

        element_format = """
              <entry name="{0}">
                <ipv6>
                  <neighbor-discovery>
                    <router-advertisement>
                      <enable>no</enable>
                    </router-advertisement>
                  </neighbor-discovery>""" + address_ipv6 + """
                </ipv6>
                <ndp-proxy>
                  <enabled>no</enabled>
                </ndp-proxy>
                <adjust-tcp-mss>
                  <enable>no</enable>
                </adjust-tcp-mss>""" + address_ipv4 + """
                <tag>{2}</tag>
              </entry>"""

    count = 1

    for eth_i in range(m):
        eth_name = cf['IF_ETHERNET_LIST'][eth_i]  # e.g. eth_name = "ethernet1/13"

        xpath = "{0}/config/devices/entry[@name='{1}']" \
            "/network/interface/ethernet/entry[@name='{2}']/layer3/units".format(x, lhost, eth_name)

        xml = f"xml_{eth_i + 1}"
        clean_xml = f"clean_{xml}"
        data[xml][0] = data[xml][0] % xpath
        data[clean_xml][0] = data[clean_xml][0] % xpath

        for eth_j in range(n):
            eth_k = eth_i * n + eth_j

            if_name = "{0}.{1}".format(eth_name, eth_j + 1)
            if_ip = ip_list[eth_k]
            if_tag = eth_k + cf['IF_ETHERNET_TAG']

            element = element_format.format(if_name, if_ip, if_tag)
            clean_element = "@name='{0}' or ".format(if_name)

            data[xml].append(element)
            data[clean_xml].append(clean_element)
            data['dump'].append(element)

            element = "<member>{0}</member>".format(if_name)
            clean_element = "text()='{0}' or ".format(if_name)
            for asso in associations:
                data['xml_' + asso].append(element)
                data['clean_xml_' + asso].append(clean_element)

            time_elapsed = timeit.default_timer() - ti

            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if nm > cf['LARGE_N'] and count % s == 0:
                print("{:.0%}".format(count / nm), end="", flush=True)

            count += 1

        data[clean_xml].append("@name='_z']")

    for asso in associations:
        data['clean_xml_' + asso].append("text()='_z']")

    data['dump'].append("</ethernet>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_net_if_eth()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
