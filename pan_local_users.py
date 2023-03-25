#!/usr/bin/python3

"""

pan-os_api v2.0 [20220728]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.git

"""

import requests
import xml.etree.ElementTree as xml

import timeit
from pan_data import init_data, write_data

verbose, debug = True, False


def pan_local_users_phash(access, user_pass):
    data = init_data('phash')

    url = access['URL']

    req_data = {
        'type': "op",
        'key': access['KEY'],
        'cmd': "<request><password-hash><password>{0}</password></password-hash></request>".format(user_pass),
    }

    for key, value in req_data.items():
        data['xml'].append("{0}={1}".format(key, value))

    try:
        response = requests.post(url, data=req_data, verify=False)
        if debug:
            print("pan_local_users_phash: response:", response.text)
    except Exception as e:
        if verbose:
            print("pan_local_users_phash:", e)
        return None

    data['out'].append(response.text)

    result = xml.fromstring(response.content)
    phash = result.find('result/phash')

    write_data(data)

    return phash.text if phash is not None else None


def pan_local_users():
    key = 'N_USERS'

    if key not in cf or cf[key] <= 0:
        return

    n = cf[key]

    print("\nDevice > Users ({0})".format(n), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    pre = 'user'

    data = init_data(pre)
    data['dump'].append("<shared><local-user-database><user>")

    xpath = "{0}/config/shared/local-user-database/user".format(cf['XPATH_TPL'])

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..

    phash = pan_local_users_phash(cf['PA1'], cf['USER_PASS'])

    for i in range(1, n + 1):
        user_name = cf['USER_NAME'] % i

        element = "<entry name='{0}'><phash>{1}</phash></entry>".format(user_name, phash)
        clean_element = "@name='{0}' or ".format(user_name)

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
    data['dump'].append("</user></local-user-database></shared>")

    write_data(data)

    print(cf['_msgs']['ok'] % (timeit.default_timer() - t0), end="")


def go():
    pan_local_users()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
