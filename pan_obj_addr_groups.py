#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_data import gen_xpath
import timeit

verbose, debug = True, False


def pan_obj_addr_groups(dg=None, seq=0):
    addr_groups, addresses = 0, 0

    if 'N_OBJ_ADDRESS_GROUP' in cf:
        addr_groups = cf['N_OBJ_ADDRESS_GROUP']
    if 'N_OBJ_ADDRESS' in cf:
        addresses = cf['N_OBJ_ADDRESS']

    if addr_groups <= 0 or addresses <= 0:
        return

    n = addr_groups

    print("\nObjects > Address Groups ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    data = init_data('addr_group', seq=seq)
    data['dump'].append("<address-group>")

    shared = 'ADDR_GROUP_SHARED'
    local_path = 'address-group'

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''
    m = cf['ADDR_GROUP_MEMBER_COUNT']

    addresses = 1

    for i in range(1, n + 1):

        group_name = (cf['ADDR_GROUP_NAME'] + suf) % i
        members = []

        for _ in range(m):
            addr_name = (cf['ADDR_NAME'] + suf) % addresses
            members.append("<member>{0}</member>".format(addr_name))
            addresses = addresses % cf['N_OBJ_ADDRESS'] + 1

        element = "<entry name='{0}'><static>{1}</static></entry>".format(group_name, "\n".join(members))
        clean_element = "@name='{0}' or ".format(group_name)

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and i % s == 0:
            print("{:.0%}".format(i / n), end="", flush=True)

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</address-group>")

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
    # this situation needs a loop with the same function
    #
    # 1. Panorama
    # 2. DG not specified
    # 3. objects not shared
    #
    shared = 'ADDR_GROUP_SHARED'
    shared_member = 'ADDR_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_obj_addr_groups(dg, i)
            return
        elif shared_member not in cf or not cf[shared_member]:
            print()
            print("pan_obj_addr_groups: shared groups must contain shared objects.")
            print("{0}: check settings {1}} and {2}.".format(cf['CF_PATH'], shared, shared_member))
            return

    pan_obj_addr_groups()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
