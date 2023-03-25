#!/usr/bin/python3

"""

pan-os_api v2.0 [20220728]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.git

"""

from pan_data import init_data, write_data
from time import sleep
import timeit

verbose, debug = True, False


def pan_vr_static():
    key = 'N_VR_STATIC'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]
    vr = cf['VR_STATIC_VR']

    print("\nNetwork > VR > {1} > Static Routes ({0})".format(n, vr), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'vr_static'

    data = init_data(pre)
    data['dump'].append("<routing-table><ip><static-route>")

    if 'XPATH_TPL' not in cf:
        print("pan_vpn_ike_gw: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']
    # vr = cf['VR_STATIC_VR']

    xpath = "{0}/config/devices/entry[@name='{1}']" \
        "/network/virtual-router/entry[@name='{2}']/routing-table/ip/static-route".format(x, lhost, vr)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move any of these back to the loop if they are dynamic
    #
    next_hop = ""
    if 'VR_STATIC_NEXTHOP' in cf and len(cf['VR_STATIC_NEXTHOP']) > 0:
        next_hop = cf['VR_STATIC_NEXTHOP']

    interface = ""
    if 'VR_STATIC_INTERFACE' in cf and len(cf['VR_STATIC_INTERFACE']) > 0:
        interface = "<interface>{0}</interface>".format(cf['VR_STATIC_INTERFACE'])

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    routes = 1

    for i in range(256):
        for j in range(256):
            if routes > n:
                break  # 2

            route_name = cf['VR_STATIC_NAME'] % routes
            # next_hop = cf['VR_STATIC_NEXTHOP']
            destination = cf['VR_STATIC_DESTINATION'] % (i, j)

            element = f"""
                  <entry name='{route_name}'>
                    <path-monitor>
                      <enable>no</enable>
                      <failure-condition>any</failure-condition>
                      <hold-time>2</hold-time>
                    </path-monitor>
                    <nexthop>
                      <ip-address>{next_hop}</ip-address>
                    </nexthop>
                    <bfd>
                      <profile>None</profile>
                    </bfd>
                    {interface}
                    <metric>10</metric>
                    <destination>{destination}</destination>
                    <route-table>
                      <unicast/>
                    </route-table>
                  </entry>"""  # .format(route_name, next_hop, interface, destination)

            clean_element = "@name='{0}' or ".format(route_name)

            data['xml'].append(element)
            data['clean_xml'].append(clean_element)
            data['dump'].append(element)

            time_elapsed = timeit.default_timer() - ti

            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if n > cf['LARGE_N'] and routes % s == 0:
                print("{:.0%}".format(routes / n), end="", flush=True)

            routes += 1
        else:
            continue
        break

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</static-route></ip></routing-table>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_vr_static()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
