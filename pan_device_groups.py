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


def pan_device_groups():
    key = 'N_PAN_DG'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nPanorama > Device Groups ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'pan_dg'

    data = init_data(pre)
    data['dump'].append("<device-group>")

    xpath = "xpath=/config/devices/entry[@name='{0}']/device-group".format(cf['LHOST'])

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    for i in range(n):
        group_name = cf['DG_NAME'].format(i + cf['DG_NAME_i'])

        element = "<entry name='{0}'><devices/></entry>".format(group_name)
        clean_element = "@name='{0}' or ".format(group_name)

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
    data['dump'].append("</device-group>")

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0))

    write_data(data)


def go():
    if 'TARGET' in cf and cf['TARGET'] == 'PANORAMA':
        pan_device_groups()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = not cf['DEBUG']
