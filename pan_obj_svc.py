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
    service_port_dst = cf['SERVICE_PORT_DST']
    service_port_src = 0
    if 'SERVICE_PORT_SRC' in cf and cf['SERVICE_PORT_SRC'] > 0:
        service_port_src = cf['SERVICE_PORT_SRC']
    service_protocol = "both"
    if 'SERVICE_PROTOCOL' in cf and cf['SERVICE_PROTOCOL'] in ('both', 'tcp', 'udp'):
        service_protocol = cf['SERVICE_PROTOCOL']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''

    services = 1

    for i in range(n):
        service_port = service_port_dst + i

        source_port = ""
        if service_port_src > 0:
            source_port = "<source-port>{0}</source-port>".format(service_port_src + i)

        element1, element2 = "", ""
        clean_element1, clean_element2 = "", ""

        if service_protocol in ('both', 'tcp'):
            service_name = (cf['SERVICE_NAME'] + suf) % ("tcp", service_port)

            element1 = f"""
      <entry name='{service_name}'>
        <protocol>
          <tcp>
            <port>{service_port}</port>
            <override>
              <no/>
            </override>
            {source_port}
          </tcp>
        </protocol>
      </entry>"""  # .format(service_name, service_port, source_port)

            clean_element1 = "@name='{0}' or ".format(service_name)

        if service_protocol in ('both', 'udp'):
            service_name = (cf['SERVICE_NAME'] + suf) % ("udp", service_port)

            element2 = f"""
      <entry name='{service_name}'>
        <protocol>
          <udp>
            <port>{service_port}</port>
            <override>
              <no/>
            </override>
            {source_port}
          </udp>
        </protocol>
      </entry>"""  # .format(service_name, service_port, source_port)

            clean_element2 = "@name='{0}' or ".format(service_name)

        data['xml'].append(element1 + element2)
        data['clean_xml'].append(clean_element1 + clean_element2)
        data['dump'].append(element1 + element2)

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
