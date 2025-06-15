#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_data import gen_xpath
from pan_ip import generate_net, generate_ip_ranges
import timeit

verbose, debug = True, False


def pan_obj_addr(dg=None, seq=0):
    key = 'N_OBJ_ADDRESS'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nObjects > Addresses ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    data = init_data("addr", seq=seq)
    data['dump'].append("<address>")

    shared = 'ADDR_SHARED'
    local_path = 'address'

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop if they are dynamic
    #
    addr_type = cf['ADDR_TYPE']
    if addr_type not in ('ip-netmask', 'ip-range', 'fqdn'):
        print("pan_obj_addr: {0}: unknown type. Please check ADDR_TYPE".format(addr_type))
        return

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''

    address_list = []

    if addr_type == 'ip-netmask':
        address_list = generate_net(cf['ADDR_ADDRESS'], n, with_prefix=True)
    elif addr_type == 'ip-range':
        address_list = generate_ip_ranges(cf['ADDR_ADDRESS'], n, cf['ADDR_RANGE_SIZE'], with_prefix=False)
    elif addr_type == 'fqdn':
        address_list = [cf['ADDR_ADDRESS'].format(i) for i in range(1, n + 1)]  # 1-based

    addresses = 1

    for i in range(n):
        addr_name = (cf['ADDR_NAME'] + suf) % addresses
        address = address_list[i]

        element = "<entry name='{0}'><{1}>{2}</{1}></entry>".format(addr_name, addr_type, address)
        clean_element = "@name='{0}' or ".format(addr_name)

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and addresses % s == 0:
            print("{:.0%}".format(addresses / n), end="", flush=True)

        addresses += 1

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</address>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    # 1. PA 1 vsys
    # 2. PA all vsys
    # 3. PA shared
    # 4. PAN 1 DG
    # 5. PAN all DG
    # 6. PAN shared

    # the only set of conditions for DG's all having the objects
    # this situation needs a loop to with the same function
    #
    # 1. Panorama
    # 2. DG not specified
    # 3. objects not shared
    #
    shared = 'ADDR_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_obj_addr(dg, i)
            return

    pan_obj_addr()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
