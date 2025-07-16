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


def pan_net_dns_proxy():
    key = 'N_NET_DNS_PROXY'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > DNS Proxy ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'dns'
    vsys = cf['VSYS']

    data = init_data(pre)
    data['dump'].append("<vsys><entry name='{0}'><dns-proxy>".format(vsys))

    if 'XPATH_TPL' not in cf:
        print("pan_net_dns_proxy: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']

    # xpath = "{0}/config/devices/entry[@name='{1}']/vsys/entry[@name='{2}']/dns-proxy".format(x, lhost, vsys)
    xpath = "{0}/config/devices/entry[@name='{1}']/network/dns-proxy".format(x, lhost)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop if they become dynamic
    #
    primary = secondary = ""

    if 'DNS_PROXY_PRIMARY' in cf and len(cf['DNS_PROXY_PRIMARY']) > 0:
        primary = "<primary>{0}</primary>".format(cf['DNS_PROXY_PRIMARY'])
        if 'DNS_PROXY_SECONDARY' in cf and len(cf['DNS_PROXY_SECONDARY']) > 0:
            secondary = "<secondary>{0}</secondary>".format(cf['DNS_PROXY_SECONDARY'])

    entry = {}

    entry['default'] = f"""
            <default>
              {primary}{secondary}
            </default>"""

    entry['cache'] = """
            <cache>
              <max-ttl>
                <enabled>no</enabled>
              </max-ttl>
              <enabled>yes</enabled>
            </cache>"""

    entry['tcp_queries'] = """
            <tcp-queries>
              <enabled>no</enabled>
            </tcp-queries>"""

    # flatten the interface list, and check if number of interfaces < N_NET_DNS_PROXY (which is okay)
    #
    interfaces = []
    if 'DNS_PROXY_INTERFACE_LIST' in cf and len(cf['DNS_PROXY_INTERFACE_LIST']) > 0:
        for if_name, if_i, if_n in cf['DNS_PROXY_INTERFACE_LIST']:
            for if_j in range(if_i, if_n + 1):
                interfaces.append("<interface><member>" + if_name.format(if_j) + "</member></interface>")
        n_if = len(interfaces)
        if n_if < n:
            print(f"DNS_PROXY_INTERFACE_LIST: interfaces available for only first {n_if}/{n} assignments.. ", end="")
            interfaces.extend([""] * (n - n_if))
    else:
        interfaces = [""] * n

    static_entries = []

    for i in range(cf['DNS_PROXY_STATIC_ENTRIES']):
        fqdn = cf['DNS_PROXY_STATIC_FQDN'].format(i + 1)  # 1-based naming
        address = cf['DNS_PROXY_STATIC_ADDR']  # currently a constant value
        static_entries.append(
            f"""
              <entry name="{fqdn}">
                <address>
                  <member>{address}</member>
                </address>
                <domain>{fqdn}</domain>
              </entry>""")

    if len(static_entries) > 0:
        entry['static_entries'] = """
            <static-entries>{0}
            </static-entries>""".format(''.join(static_entries))

    entry_details = ''.join(entry.values())

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    for i in range(n):
        dns_proxy_name = cf['DNS_PROXY_NAME'].format(cf['DNS_PROXY_NAME_i'] + i)

        element = f"""
          <entry name="{dns_proxy_name}">
            {entry_details}
            {interfaces[i]}
          </entry>"""

        clean_element = "@name='{0}' or ".format(dns_proxy_name)

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
    data['dump'].append("</dns-proxy></entry></vsys>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_net_dns_proxy()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
