#!/usr/bin/python3

"""

pan-os_api v2.4 [20260509]
pan-os_api v2.3 [20250607]
pan-os_api v2.2 [20230717]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_data import gen_xpath
from pan_ip import generate_net
import timeit

verbose, debug = True, False


def pan_rules_dec(dg=None, seq=0):
    key = 'N_RULES_DEC'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nPolicies > Decryption ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'dec'
    suf = f"-{seq}" if seq > 0 else ''

    data = init_data(pre)
    data['dump'].append("<decryption><rules>")
    data['script'] = [f'echo "Adding rules {pre}{suf} ({n}).."'] + data['script']
    data['clean_script'] = [f'echo "Deleting rules {pre}{suf} ({n}).."'] + data['clean_script']

    shared = 'DEC_SHARED'
    local_path = (
        "{}/decryption/rules".format(cf['DEC_RULEBASE']),
        "rulebase/decryption/rules",
    )

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    net_list_src = generate_net(cf['DEC_SOURCE'], n, with_prefix=True)
    if 'DEC_DESTINATION' in cf and cf['DEC_DESTINATION'] != "any":
        net_list_dst = generate_net(cf['DEC_DESTINATION'], n, with_prefix=True)
    else:
        net_list_dst = ['any'] * n

    # static parameters: move them back to the loop if they are dynamic
    #
    src_zone = cf['DEC_SRC_ZONE']
    dst_zone = cf['DEC_DST_ZONE']
    service = cf['DEC_SERVICE']

    type_dec = cf['DEC_TYPE']
    if cf['DEC_TYPE'] == 'ssl-inbound-inspection':
        cert_list = []
        for cert in cf['DEC_CERTIFICATES']:
            cert_list.append(f"<member>{cert}</member>")
        type_dec = f"""
                    <{type_dec}>
                      <certificates>{"\n".join(cert_list)}</certificates>
                    </{type_dec}>"""
    else:
        type_dec = f"<{type_dec}/>"

    action = cf['DEC_ACTION']
    profile = cf['DEC_PROFILE']
    disabled = cf['DEC_DISABLED']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    for i in range(n):
        rule_name = (cf['DEC_NAME'] + suf).format(i + cf['DEC_NAME_i'])
        src, dst = net_list_src[i], net_list_dst[i]

        element = f"""
                <entry name='{rule_name}'>
                  <category>
                    <member>any</member>
                  </category>
                  <service>
                    <member>{service}</member>
                  </service>
                  <type>{type_dec}</type>
                  <from>
                    <member>{src_zone}</member>
                  </from>
                  <to>
                    <member>{dst_zone}</member>
                  </to>
                  <source>
                    <member>{src}</member>
                  </source>
                  <destination>
                    <member>{dst}</member>
                  </destination>
                  <source-user>
                    <member>any</member>
                  </source-user>
                  <action>{action}</action>
                  <profile>{profile}</profile>
                  <disabled>{disabled}</disabled>
                  <source-hip>
                    <member>any</member>
                  </source-hip>
                  <destination-hip>
                    <member>any</member>
                  </destination-hip>
                </entry>"""

        clean_element = f"@name='{rule_name}' or "

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
    data['dump'].append("</rules></decryption>")

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
    shared = 'PBF_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_rules_dec(dg, i)
            return

    pan_rules_dec()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
