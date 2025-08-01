#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data, push_data
from pan_ip import generate_ip
import timeit

import io
import requests

verbose, debug = True, False


def pan_uid():
    uid_nets, uid_entries = 0, 0

    if 'N_UID_NETS' in cf:
        uid_nets = cf['N_UID_NETS']
    if 'N_UID_ENTRIES' in cf:
        uid_entries = cf['N_UID_ENTRIES']

    if uid_nets <= 0 or uid_entries <= 0:
        return None

    print("\nUser-ID > IP-user mappings ({0} x {1})".format(uid_nets, uid_entries), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'uid'

    data = init_data(pre)
    data['xml'].append("<uid-message><version>2.0</version><type>update</type><payload><login>")

    # static parameters: move them back to the loop if they become dynamic
    #
    uid_timeout = cf['UID_TIMEOUT']

    # static variables in the loop
    #
    n = uid_nets * uid_entries
    s = n // 10  # increment per slice: 10%, 20%, etc..

    count = 1

    for i in range(uid_nets):
        domain = chr(cf['UID_DOMAIN_i'] + i + 64)  # i mapped to A, B, etc.
        ip_list = generate_ip(cf['UID_IP'][i], uid_entries, uid_entries, with_prefix=False)

        for j in range(uid_entries):
            uid_user = cf['UID_USER'].format(domain, cf['UID_USER_j'] + j)
            uid_ip = ip_list[j]

            element = '<entry name="{0}" ip="{1}" timeout="{2}"/>'.format(uid_user, uid_ip, uid_timeout)
            data['xml'].append(element)

            time_elapsed = timeit.default_timer() - ti
            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if n > cf['LARGE_N'] and count % s == 0:
                print("{:.0%}".format(count / n), end="", flush=True)
            count += 1

    data['xml'].append("</login></payload></uid-message>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_uid()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
