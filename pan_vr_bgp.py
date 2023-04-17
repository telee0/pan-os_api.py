#!/usr/bin/python3

"""

pan-os_api v2.1 [20230417]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
import timeit

verbose, debug = True, False


def pan_vr_bgp():
    key = 'N_VR_BGP_PEER_GROUPS'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]
    m = cf['N_VR_BGP_PEERS_PER_GROUP']
    vr = cf['VR_BGP_VR']

    print("\nNetwork > VR > {2} > BGP peer groups x peers ({0} x {1})".format(n, m, vr), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'vr_bgp'
    associations = tuple([f"peer{i}" for i in range(1, n + 1)])

    data = init_data(pre, associations)
    data['dump'].append("<protocol><bgp><peer-group>")

    if 'XPATH_TPL' not in cf:
        print("pan_vpn_ike_gw: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']
    # vr = cf['VR_BGP_VR']

    xpath = "{0}/config/devices/entry[@name='{1}']" \
        "/network/virtual-router/entry[@name='{2}']/protocol/bgp/peer-group".format(x, lhost, vr)

    data['script'] = [
        'echo "Please be sure of the following before adding peer groups."',
        'echo',
        'echo "1. Virtual router ({}) exists or is added first."'.format(cf['VR_BGP_VR']),
        'echo "2. BGP AS (e.g. 65530) has been set."',
        'echo "3. Local interfaces and IPs have been configured. Check VR_BGP_PEER_LOCAL_INT."',
        'echo "4. IP addresses are consistent with those from interface config. Check IF_ETHERNET_IP for eth."',
        'echo',
    ] + data['script']
    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move any of these back to the loop if they are dynamic
    #
    group_type = ""
    if 'VR_BGP_PEER_GROUP_TYPE' in cf and cf['VR_BGP_PEER_GROUP_TYPE'] == 'ebgp':
        group_type = """
                      <ebgp>
                        <remove-private-as>yes</remove-private-as>
                        <import-nexthop>original</import-nexthop>
                        <export-nexthop>resolve</export-nexthop>
                      </ebgp>"""

    # static variables in the loop
    #
    nm = n * m
    s = nm // 10  # increment per slice: 10%, 20%, etc..

    count = 1

    for i in range(1, n + 1):
        group_name = cf['VR_BGP_PEER_GROUP_NAME'] % i

        element = f"""
                  <entry name='{group_name}'>
                    <type>{group_type}
                    </type>
                    <aggregated-confed-as-path>yes</aggregated-confed-as-path>
                    <soft-reset-with-stored-info>no</soft-reset-with-stored-info>
                    <enable>yes</enable>
                  </entry>"""  # .format(group_name, group_type)

        clean_element = "@name='{0}' or ".format(group_name)

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        # peers of each group
        #

        xml_peer = f"xml_peer{i}"

        xpath_peer = "{0}/entry[@name='{1}']/peer".format(xpath, group_name)

        data[xml_peer][0] = data[xml_peer][0] % xpath_peer

        ip_octet_j = cf['VR_BGP_PEER_LOCAL_IP_OCTET_j']
        ip_octet_k = cf['VR_BGP_PEER_LOCAL_IP_OCTET_k']

        peers = 1

        for j in range(ip_octet_j, 256):
            for k in range(ip_octet_k, 256):
                if peers > m:
                    break  # 2

                peer_name = cf['VR_BGP_PEER_NAME'] % (i, peers)
                peer_local_interface = cf['VR_BGP_PEER_LOCAL_INT'] % peers
                peer_local_ip = cf['VR_BGP_PEER_LOCAL_IP'] % (j, k)
                peer_peer_ip = cf['VR_BGP_PEER_PEER_IP'] % (j, k)
                peer_as = cf['VR_BGP_PEER_AS']

                element = f"""
                      <entry name='{peer_name}'>
                        <connection-options>
                          <incoming-bgp-connection>
                            <remote-port>0</remote-port>
                            <allow>yes</allow>
                          </incoming-bgp-connection>
                          <outgoing-bgp-connection>
                            <local-port>0</local-port>
                            <allow>yes</allow>
                          </outgoing-bgp-connection>
                          <multihop>0</multihop>
                          <keep-alive-interval>30</keep-alive-interval>
                          <open-delay-time>0</open-delay-time>
                          <hold-time>90</hold-time>
                          <idle-hold-time>15</idle-hold-time>
                          <min-route-adv-interval>30</min-route-adv-interval>
                        </connection-options>
                        <subsequent-address-family-identifier>
                          <unicast>yes</unicast>
                          <multicast>no</multicast>
                        </subsequent-address-family-identifier>
                        <local-address>
                          <ip>{peer_local_ip}</ip>
                          <interface>{peer_local_interface}</interface>
                        </local-address>
                        <peer-address>
                          <ip>{peer_peer_ip}</ip>
                        </peer-address>
                        <bfd>
                          <profile>Inherit-vr-global-setting</profile>
                        </bfd>
                        <max-prefixes>5000</max-prefixes>
                        <enable>yes</enable>
                        <peer-as>{peer_as}</peer-as>
                        <enable-mp-bgp>no</enable-mp-bgp>
                        <address-family-identifier>ipv4</address-family-identifier>
                        <enable-sender-side-loop-detection>yes</enable-sender-side-loop-detection>
                        <reflector-client>non-client</reflector-client>
                        <peering-type>unspecified</peering-type>
                      </entry>"""  # format(peer_name, peer_local_ip, peer_local_interface, peer_peer_ip, peer_as)

                data[xml_peer].append(element)

                peers += 1

                time_elapsed = timeit.default_timer() - ti

                if time_elapsed > 1:
                    print('.', end="", flush=True)
                    ti = timeit.default_timer()

                if nm > cf['LARGE_N'] and count % s == 0:
                    print("{:.0%}".format(count / nm), end="", flush=True)

                count += 1
            else:
                ip_octet_k = 0  # normalize k for next j
                continue
            break

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</peer-group></bgp></protocol>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_vr_bgp()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
