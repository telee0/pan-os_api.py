#!/usr/bin/python3

"""

pan-os_api v2.1 [20230417]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

from pan_data import init_data, write_data
from pan_data import gen_xpath
import timeit

verbose, debug = True, False


def pan_rules_nat(dg=None, seq=0):
    key = 'N_RULES_NAT'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nPolicies > NAT ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'nat'
    suf = f"-{seq}" if seq > 0 else ''

    data = init_data(pre, seq=seq)
    data['dump'].append("<nat><rules>")
    data['script'] = [f'echo "Adding rules {pre}{suf} ({n}).."'] + data['script']
    data['clean_script'] = [f'echo "Deleting rules {pre}{suf} ({n}).."'] + data['clean_script']

    shared = 'NAT_SHARED'
    local_path = (
        "{}/nat/rules".format(cf['NAT_RULEBASE']),
        "rulebase/nat/rules",
    )

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static parameters: move them back to the loop if they are dynamic
    #
    dst_zone = cf['NAT_DST_ZONE']
    src_zone = cf['NAT_SRC_ZONE']
    service = cf['NAT_SERVICE']
    # action = cf['NAT_ACTION']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    rules = 1

    for i in range(256):
        for j in range(256):
            if rules > n:
                break  # 2

            rule_name = (cf['NAT_NAME'] + suf) % rules
            src = cf['NAT_SOURCE'] % (i, j)
            dst = cf['NAT_DESTINATION'] % (i, j)

            element = f"""
                <entry name='{rule_name}'>
                  <to>
                    <member>{dst_zone}</member>
                  </to>
                  <from>
                    <member>{src_zone}</member>
                  </from>
                  <source>
                    <member>{src}</member>
                  </source>
                  <destination>
                    <member>{dst}</member>
                  </destination>
                  <service>{service}</service>
                </entry>"""  # .format(rule_name, dst_zone, src_zone, src, dst, service)

            clean_element = f"@name='{rule_name}' or "

            data['xml'].append(element)
            data['clean_xml'].append(clean_element)
            data['dump'].append(element)

            time_elapsed = timeit.default_timer() - ti

            if time_elapsed > 1:
                print('.', end="", flush=True)
                ti = timeit.default_timer()

            if n > cf['LARGE_N'] and rules % s == 0:
                print("{:.0%}".format(rules / n), end="", flush=True)

            rules += 1
        else:
            continue
        break

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</rules></nat>")

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
    shared = 'NAT_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_rules_nat(dg, i)
            return

    pan_rules_nat()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
