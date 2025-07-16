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


def pan_obj_svc(dg=None, seq=0):
    key = 'N_OBJ_SERVICE'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nObjects > Services ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    data = init_data('svc', seq=seq)
    data['dump'].append("<service>")

    shared = 'SERVICE_SHARED'
    local_path = 'service'

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop if they are dynamic
    #
    service_port_i = cf['SERVICE_PORT_DST']
    src_port_i = 0
    src_port_format = ""
    if 'SERVICE_PORT_SRC' in cf and cf['SERVICE_PORT_SRC'] > 0:
        src_port_i = cf['SERVICE_PORT_SRC']
        src_port_format = "<source-port>{0}</source-port>"
    protocol_list = []
    if 'SERVICE_PROTOCOL' in cf:
        service_protocol = cf['SERVICE_PROTOCOL']
        if service_protocol == 'both':
            protocol_list = ['tcp', 'udp']
        elif service_protocol == 'tcp':
            protocol_list = ['tcp']
        elif service_protocol == 'udp':
            protocol_list = ['udp']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''

    services = 1

    for i in range(n):
        service_port = service_port_i + i
        source_port = src_port_format.format(src_port_i + i)

        element_list, clean_element_list = [], []

        for protocol in protocol_list:
            service_name = (cf['SERVICE_NAME'] + suf).format(protocol, service_port)
            element = f"""
      <entry name='{service_name}'>
        <protocol>
          <{protocol}>
            <port>{service_port}</port>
            <override>
              <no/>
            </override>
            {source_port}
          </{protocol}>
        </protocol>
      </entry>"""
            element_list.append(element)
            clean_element_list.append("@name='{0}' or ".format(service_name))

        elements = "".join(element_list)
        clean_elements = "".join(clean_element_list)

        data['xml'].append(elements)
        data['clean_xml'].append(clean_elements)
        data['dump'].append(elements)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and services % s == 0:
            print("{:.0%}".format(services / n), end="", flush=True)

        services += 1

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</service>")

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
    shared = 'ADDR_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_obj_svc(dg, i)
            return

    pan_obj_svc()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
