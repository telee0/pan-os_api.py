#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_ip import generate_net
import timeit

from pan_ip import generate_ip

verbose, debug = True, False


def pan_vpn_ipsec_tun():
    key = 'N_NET_IPSEC'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > IPSec Tunnels ({0}) with static routes through tunnels".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'ipsec'
    route = 'route'

    # unlike associations, config data structures of 2 devices are independent
    #
    data_a = init_data(pre, (route,), 'PA1')
    data_b = init_data(pre, (route,), 'PA2')

    # ------------------------------------------------------------

    if 'XPATH_TPL' not in cf:
        print("pan_vpn_ike_gw: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']
    vr = cf['IPSEC_VR']

    xpath = "{0}/config/devices/entry[@name='{1}']/network/tunnel/ipsec".format(x, lhost)
    xpath_route = "{0}/config/devices/entry[@name='{1}']" \
                  "/network/virtual-router/entry[@name='{2}']/routing-table/ip/static-route".format(x, lhost, vr)

    for data in [data_a, data_b]:
        data['script'] = [
            'echo "Please be sure tunnel interfaces and IKE gatways before adding IPSec tunnels."',
        ] + data['script']
        data['dump'].append("<network><tunnel><ipsec>")
        data['xml'][0] = data['xml'][0] % xpath
        data['clean_xml'][0] = data['clean_xml'][0] % xpath
        data['xml_route'][0] = data['xml_route'][0] % xpath_route
        data['clean_xml_route'][0] = data['clean_xml_route'][0] % xpath_route

    # shared parameters: move them back to the loop when they become dynamic
    #
    # IPSec specific
    #
    ipsec_crypto_pfile = ""
    if 'IPSEC_CRYPTO_PROFILE' in cf and cf['IPSEC_CRYPTO_PROFILE'] not in ("", "default"):
        ipsec_crypto_pfile = "<ipsec-crypto-profile>{0}</ipsec-crypto-profile>".format(cf['IPSEC_CRYPTO_PROFILE'])

    anti_replay = cf['IPSEC_REPLAY_PROTECTION']

    # proxy ID specific
    #
    proxy_id_add = ('IPSEC_PROXY_ID_ADD' in cf and cf['IPSEC_PROXY_ID_ADD'])
    m = min(cf['IPSEC_PROXY_ID_LIMIT'], 250) if proxy_id_add else 0
    protocol = cf['IPSEC_PROXY_ID_PROTOCOL']

    # route specific
    #
    local_net = cf['IPSEC_IP_LOCAL'] + cf['IPSEC_IP_LOCAL_PREFIX']
    remote_net = cf['IPSEC_IP_REMOTE'] + cf['IPSEC_IP_REMOTE_PREFIX']

    if proxy_id_add:
        n_ = (n + m - 1) // m
        net_list_local = generate_net(local_net, n_)
        net_list_remote = generate_net(remote_net, n_)
        ip_list_local = generate_ip(local_net, n, m, with_prefix=False)
        ip_list_remote = generate_ip(remote_net, n, m, with_prefix=False)
    else:
        net_list_local = generate_net(local_net, n)
        net_list_remote = generate_net(remote_net, n)
        ip_list_local = generate_ip(local_net, n, 1, with_prefix=False)
        ip_list_remote = generate_ip(local_net, n, 1, with_prefix=False)

    if debug:
        print("net_list_local", net_list_local)
        print("net_list_remote", net_list_remote)
        print("ip_list_local", ip_list_local)
        print("ip_list_remote", ip_list_remote)

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    ipsec = 0

    for i in range(n):
        if ipsec >= n:
            break

        ipsec_name = cf['IPSEC_NAME'].format(i + cf['IPSEC_NAME_i'])
        tunnel_interface = cf['IPSEC_TUNNEL_INTERFACE'].format(i + cf['IPSEC_TUNNEL_INTERFACE_i'])
        ike_gateway = cf['IPSEC_IKE_GATEWAY'].format(i + cf['IPSEC_IKE_GATEWAY_i'])

        proxy_id_a, proxy_id_b = "", ""

        if proxy_id_add:
            p_a, p_b = [], []
            for j in range(m):
                if ipsec >= n:
                    break  # 1

                proxy_id_name = cf['IPSEC_PROXY_ID_NAME'] % (i + 1, j + 1)

                local = ip_list_local[ipsec]
                remote = ip_list_remote[ipsec]

                p_a.append(f"""
                  <entry name='{proxy_id_name}'>
                    <protocol>
                      <{protocol}/>
                    </protocol>
                    <local>{local}</local>
                    <remote>{remote}</remote>
                  </entry>""")

                p_b.append(f"""
                  <entry name='{proxy_id_name}'>
                    <protocol>
                      <{protocol}/>
                    </protocol>
                    <local>{remote}</local>
                    <remote>{local}</remote>
                  </entry>""")

                ipsec += 1  # 1x proxy_id counted as 1x ipsec

                time_elapsed = timeit.default_timer() - ti

                if time_elapsed > 1:
                    print('.', end="", flush=True)
                    ti = timeit.default_timer()

            proxy_id_a = "<proxy-id>{0}</proxy-id>".format("\n".join(p_a))
            proxy_id_b = "<proxy-id>{0}</proxy-id>".format("\n".join(p_b))

        element_a = f"""
            <entry name='{ipsec_name}'>
              <auto-key>
                <ike-gateway>
                  <entry name='{ike_gateway}'/>
                </ike-gateway>
                {ipsec_crypto_pfile}
                {proxy_id_a}
              </auto-key>
              <tunnel-monitor>
                <enable>no</enable>
              </tunnel-monitor>
              <tunnel-interface>{tunnel_interface}</tunnel-interface>
              <anti-replay>{anti_replay}</anti-replay>
            </entry>"""

        element_b = f"""
            <entry name='{ipsec_name}'>
              <auto-key>
                <ike-gateway>
                  <entry name='{ike_gateway}'/>
                </ike-gateway>
                {ipsec_crypto_pfile}
                {proxy_id_b}
              </auto-key>
              <tunnel-monitor>
                <enable>no</enable>
              </tunnel-monitor>
              <tunnel-interface>{tunnel_interface}</tunnel-interface>
              <anti-replay>{anti_replay}</anti-replay>
            </entry>"""

        clean_element = f"@name='{ipsec_name}' or "

        data_a['xml'].append(element_a)
        data_a['clean_xml'].append(clean_element)
        data_b['xml'].append(element_b)
        data_b['clean_xml'].append(clean_element)

        # routes
        #
        route_name = cf['IPSEC_ROUTE_NAME'].format(i + cf['IPSEC_ROUTE_i'])

        dst_a = net_list_local[i]
        dst_b = net_list_remote[i]

        route_a = f"""
                  <entry name='{route_name}'>
                    <interface>{tunnel_interface}</interface>
                    <metric>10</metric>
                    <destination>{dst_a}</destination>
                    <route-table>
                      <unicast/>
                    </route-table>
                  </entry>"""

        route_b = f"""
                  <entry name='{route_name}'>
                    <interface>{tunnel_interface}</interface>
                    <metric>10</metric>
                    <destination>{dst_b}</destination>
                    <route-table>
                      <unicast/>
                    </route-table>
                  </entry>"""

        clean_route = f"@name='{route_name}' or "

        data_a['xml_route'].append(route_a)
        data_a['clean_xml_route'].append(clean_route)
        data_b['xml_route'].append(route_b)
        data_b['clean_xml_route'].append(clean_route)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and ipsec % s == 0:
            print("{:.0%}".format(ipsec / n), end="", flush=True)

        if not proxy_id_add:
            ipsec += 1

    for data in [data_a, data_b]:
        data['clean_xml_route'].append("@name='_z']")
        data['clean_xml'].append("@name='_z']")
        data['dump'].append("</ipsec></tunnel></network>")

    write_data(data_a, target='PA1')
    write_data(data_b, target='PA2')

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_vpn_ipsec_tun()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
