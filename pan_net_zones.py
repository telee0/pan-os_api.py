#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
import timeit

verbose, debug = True, False


def pan_net_zones():
    key = 'N_NET_ZONES'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > Zones ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'zone'
    vsys = cf['VSYS']

    data = init_data(pre)
    data['dump'].append("<vsys><entry name='{0}'><zone>".format(vsys))

    if 'XPATH_TPL' not in cf:
        print("pan_net_zones: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']

    xpath = "{0}/config/devices/entry[@name='{1}']/vsys/entry[@name='{2}']/zone".format(x, lhost, vsys)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop if they become dynamic
    #
    zone_type = ""
    if 'ZONE_TYPE' in cf and cf['ZONE_TYPE'] in ("tap", "virtual-wire", "layer2", "layer3", "tunnel"):
        zone_type = f"<network><{cf['ZONE_TYPE']}/></network>"
    zone_uid = "<enable-user-identification>yes</enable-user-identification>" if cf['ZONE_UID'] else ""

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    for i in range(n):
        zone_name = cf['ZONE_NAME'].format(i + cf['ZONE_NAME_i'])

        element = "<entry name='{0}'>{1}{2}</entry>".format(zone_name, zone_uid, zone_type)
        clean_element = "@name='{0}' or ".format(zone_name)

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and (i + 1) % s == 0:
            print("{:.0%}".format(i / n), end="", flush=True)

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</zone></entry></vsys>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_net_zones()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
