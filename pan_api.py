#!/usr/bin/python3

"""

pan-os_api v2.1 [20230417]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import requests
import xml.etree.ElementTree as xml

verbose, debug = True, False


def pan_api(access):
    requests.packages.urllib3.disable_warnings()

    host, user, password = access

    url = "https://{0}/api/?type=keygen".format(host)

    try:
        response = requests.post(url, data={'user': user, 'password': password}, verify=False)
        if debug:
            print("pan_api: response: ", response.text)
    except Exception as e:
        if verbose:
            print("pan_api: {0}: {1}".format(host, e))
        return None

    result = xml.fromstring(response.content)
    api_key = result.find('result/key')

    return api_key.text if api_key is not None else None


def go():
    for pa in ['PA1', 'PA2']:
        if pa in cf:
            desc = ""
            if 'DESC' in cf[pa] and len(cf[pa]['DESC']) > 0:
                desc = " ({0})".format(cf[pa]['DESC'])
            print("{0} = {1}{2}".format(pa, cf[pa]['HOST'], desc))
            api_key = pan_api([cf[pa]['HOST'], cf[pa]['USER'], cf[pa]['PASS']])
            if api_key is not None and len(api_key) > 0:
                cf[pa]['KEY'] = api_key
                cf[pa]['URL'] = "https://{0}/api".format(cf[pa]['HOST'])
            else:
                print("{0}: API key not set. Please check {1} in {2}.".format(cf[pa]['HOST'], pa, cf['CF_PATH']))


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
