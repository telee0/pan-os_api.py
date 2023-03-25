#!/usr/bin/python3

"""

pan-os_api v2.0 [20220728]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.git

"""

import timeit
from pan_data import init_data, write_data

verbose, debug = True, False


def pan_vpn_ike_gw():
    key = 'N_NET_IKE'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nNetwork > IKE Gateways ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'ike'

    # unlike associations, config data structures of 2 devices are independent
    #
    data_a = init_data(pre, target='PA1')
    data_b = init_data(pre, target='PA2')

    # ------------------------------------------------------------

    if 'XPATH_TPL' not in cf:
        print("pan_vpn_ike_gw: XPATH_TPL not set: Panorama template not specified")
        return

    x = cf['XPATH_TPL']
    lhost = cf['LHOST']

    xpath = "{0}/config/devices/entry[@name='{1}']/network/ike/gateway".format(x, lhost)

    for data in [data_a, data_b]:
        data['script'] = [
            'echo "Please be sure of the following before adding IKE gateways."',
            'echo',
            'echo "1. Local interfaces have been configured."',
            'echo "2. Peers are reachable. (routing)"',
            'echo ',
        ] + data['script']
        data['dump'].append("<ike><gateway>")
        data['xml'][0] = data['xml'][0] % xpath
        data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop when they become dynamic
    #
    ike_key = cf['IKE_PRESHARED_KEY']

    ike_crypto_pfile = ""
    if 'IKE_CRYPTO_PROFILE' in cf and cf['IKE_CRYPTO_PROFILE'] not in ("", "default"):
        ike_crypto_pfile = "<ike-crypto-profile>{0}</ike-crypto-profile>".format(cf['IKE_CRYPTO_PROFILE'])

    ike_version = ""
    if 'IKE_VERSION' in cf and cf['IKE_VERSION'].startswith('ikev2'):
        ike_version = "<version>{0}</version>".format(cf['IKE_VERSION'])

    local_prefix = cf['IKE_IP_LOCAL_PREFIX']
    peer_prefix = cf['IKE_IP_PEER_PREFIX']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    ike = 1

    for i in range(256):
        for j in range(256):
            if ike > n:
                break  # 2

            ike_name = cf['IKE_NAME'] % ike
            ike_iface = cf['IKE_INTERFACE'].format(ike)
            ip_local = cf['IKE_IP_LOCAL'].format(i, j)
            ip_peer = cf['IKE_IP_PEER'].format(i, j)

            element_a = f"""
            <entry name='{ike_name}'>
              <authentication>
                <pre-shared-key>
                  <key>{ike_key}</key>
                </pre-shared-key>
              </authentication>
              <protocol>
                <ikev1>
                  <dpd>
                    <enable>yes</enable>
                  </dpd>
                  {ike_crypto_pfile}
                </ikev1>
                <ikev2>
                  <dpd>
                    <enable>yes</enable>
                  </dpd>
                  {ike_crypto_pfile}
                </ikev2>
                {ike_version}
              </protocol>
              <protocol-common>
                <nat-traversal>
                  <enable>no</enable>
                </nat-traversal>
                <fragmentation>
                  <enable>no</enable>
                </fragmentation>
              </protocol-common>
              <local-address>
                <interface>{ike_iface}</interface>
                <ip>{ip_local}{local_prefix}</ip>
              </local-address>
              <peer-address>
                <ip>{ip_peer}</ip>
              </peer-address>
            </entry>"""

            element_b = f"""
            <entry name='{ike_name}'>
              <authentication>
                <pre-shared-key>
                  <key>{ike_key}</key>
                </pre-shared-key>
              </authentication>
              <protocol>
                <ikev1>
                  <dpd>
                    <enable>yes</enable>
                  </dpd>
                  {ike_crypto_pfile}
                </ikev1>
                <ikev2>
                  <dpd>
                    <enable>yes</enable>
                  </dpd>
                  {ike_crypto_pfile}
                </ikev2>
                {ike_version}
              </protocol>
              <protocol-common>
                <nat-traversal>
                  <enable>no</enable>
                </nat-traversal>
                <fragmentation>
                  <enable>no</enable>
                </fragmentation>
              </protocol-common>
              <local-address>
                <interface>{ike_iface}</interface>
                <ip>{ip_peer}{peer_prefix}</ip>
              </local-address>
              <peer-address>
                <ip>{ip_local}</ip>
              </peer-address>
            </entry>"""

            clean_element = "@name='{0}' or ".format(ike_name)

            data_a['xml'].append(element_a)
            data_a['clean_xml'].append(clean_element)
            data_b['xml'].append(element_b)
            data_b['clean_xml'].append(clean_element)

            time_elapsed = timeit.default_timer() - ti

            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if n > cf['LARGE_N'] and ike % s == 0:
                print("{:.0%}".format(ike / n), end="", flush=True)

            ike += 1
        else:
            continue
        break

    for data in [data_a, data_b]:
        data['clean_xml'].append("@name='_z']")
        data['dump'].append("</gateway></ike>")

    write_data(data_a, target='PA1')
    write_data(data_b, target='PA2')

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_vpn_ike_gw()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
