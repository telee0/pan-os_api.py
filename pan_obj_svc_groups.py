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


def pan_obj_svc_groups(dg=None, seq=0):
    svc_groups, services = 0, 0

    if 'N_OBJ_SERVICE_GROUP' in cf:
        svc_groups = cf['N_OBJ_SERVICE_GROUP']
    if 'N_OBJ_SERVICE' in cf:
        services = cf['N_OBJ_SERVICE']

    if svc_groups <= 0 or services <= 0:
        return

    n = svc_groups

    print("\nObjects > Service Groups ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    data = init_data('svc_group', seq=seq)
    data['dump'].append("<service-group>")

    shared = 'SERVICE_GROUP_SHARED'
    local_path = 'service-group'

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop when they become dynamic
    #
    service_group_protocol = ""
    if 'SERVICE_GROUP_PROTOCOL' in cf and cf['SERVICE_GROUP_PROTOCOL'] in ('both', 'tcp', 'udp'):
        service_group_protocol = cf['SERVICE_GROUP_PROTOCOL']
    elif 'SERVICE_PROTOCOL' in cf and cf['SERVICE_PROTOCOL'] in ('both', 'tcp', 'udp'):
        service_group_protocol = cf['SERVICE_PROTOCOL']

    protocol_list = []
    if service_group_protocol == 'both':
        protocol_list = ['tcp', 'udp']
    elif service_group_protocol == 'tcp':
        protocol_list = ['tcp']
    elif service_group_protocol == 'udp':
        protocol_list = ['udp']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''
    m = cf['SERVICE_GROUP_MEMBER_COUNT']

    for i in range(n):
        group_name = (cf['SERVICE_GROUP_NAME'] + suf).format(i + cf['SERVICE_GROUP_NAME_i'])
        members = []

        for j in range(m):
            services = (i * m + j) % cf['N_OBJ_SERVICE']
            service_port = cf['SERVICE_PORT_DST'] + services
            for protocol in protocol_list:
                service_name = (cf['SERVICE_NAME'] + suf).format(protocol, service_port)
                members.append("<member>{0}</member>".format(service_name))

        element = "<entry name='{0}'><members>{1}</members></entry>".format(group_name, "\n".join(members))
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
    data['dump'].append("</service-group>")

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
    shared = 'SERVICE_GROUP_SHARED'
    shared_member = 'SERVICE_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_obj_svc_groups(dg, i)
            return
        elif shared_member not in cf or not cf[shared_member]:
            print()
            print("pan_obj_svc_groups: shared groups must contain shared objects.")
            print("{0}: check settings {1}} and {2}.".format(cf['CF_PATH'], shared, shared_member))
            return

    pan_obj_svc_groups()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
