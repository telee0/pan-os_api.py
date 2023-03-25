#!/usr/bin/python3

"""

pan-os_api v2.0 [20220728]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.git

"""

from pan_data import init_data, write_data
import timeit

verbose, debug = True, False


def pan_net_if_eth():
    key = 'N_NET_IF_ETHERNET'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > Interfaces > Ethernet ({0}) with zone and VR assigned".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'eth'
    associations = ('vsys', 'zone', 'vr')

    data = init_data(pre, associations)
    data['dump'].append("<ethernet>")

    if 'XPATH_TPL' not in cf:
        print("pan_net_if_eth: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']

    if_name = cf['IF_ETHERNET_NAME']
    vsys = cf['VSYS']
    zone = cf['IF_ETHERNET_ZONE']
    vr = cf['IF_ETHERNET_VR']

    xpath = "{0}/config/devices/entry[@name='{1}']" \
        "/network/interface/ethernet/entry[@name='{2}']/layer3/units".format(x, lhost, if_name)
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

    ip_octet_i = cf['IF_ETHERNET_IP_OCTET_i']
    ip_octet_j = cf['IF_ETHERNET_IP_OCTET_j']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    interfaces = 1

    for i in range(ip_octet_i, 256):
        for j in range(ip_octet_j, 256):
            if interfaces > n:
                break  # 2

            interface_name = "{0}.{1}".format(cf['IF_ETHERNET_NAME'], interfaces)
            interface_ip = cf['IF_ETHERNET_IP'] % (i, j)

            element = f"""
                  <entry name='{interface_name}'>
                    <ipv6>
                      <neighbor-discovery>
                        <router-advertisement>
                          <enable>no</enable>
                        </router-advertisement>
                      </neighbor-discovery>
                    </ipv6>
                    <ndp-proxy>
                      <enabled>no</enabled>
                    </ndp-proxy>
                    <adjust-tcp-mss>
                      <enable>no</enable>
                    </adjust-tcp-mss>
                    <ip>
                      <entry name='{interface_ip}'/>
                    </ip>
                    <tag>{interfaces}</tag>
                  </entry>"""  # .format(interface_name, interface_ip, interfaces)

            clean_element = "@name='{0}' or ".format(interface_name)

            data['xml'].append(element)
            data['clean_xml'].append(clean_element)
            data['dump'].append(element)

            element = "<member>{0}</member>".format(interface_name)
            clean_element = "text()='{0}' or ".format(interface_name)
            for asso in associations:
                data['xml_' + asso].append(element)
                data['clean_xml_' + asso].append(clean_element)

            time_elapsed = timeit.default_timer() - ti

            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if n > cf['LARGE_N'] and interfaces % s == 0:
                print("{:.0%}".format(interfaces / n), end="", flush=True)

            interfaces += 1
        else:
            ip_octet_j = 0  # normalize j for next i
            continue
        break

    data['clean_xml'].append("@name='_z']")
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
