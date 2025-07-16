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


def pan_obj_url(dg=None, seq=0):
    url_cats, url_entries = 0, 0

    if 'N_OBJ_URL_CATS' in cf:
        url_cats = cf['N_OBJ_URL_CATS']
    if 'N_OBJ_URL_ENTRIES' in cf:
        url_entries = cf['N_OBJ_URL_ENTRIES']

    if url_cats <= 0 or url_entries <= 0:
        return

    n, m = url_cats, url_entries

    print("\nObjects > Custom URL Category with url.txt ({0} x {1})".format(n, m), end=" ", flush=True)

    t0 = timeit.default_timer()
    ti = t0

    data = init_data("url", seq=seq)
    data['dump'].append("<profiles><custom-url-category>")

    shared = 'URL_SHARED'
    local_path = 'profiles/custom-url-category'

    xpath = gen_xpath(shared, local_path, dg)

    data['xml'][0] = data['xml'][0] % xpath
    data['clean_xml'][0] = data['clean_xml'][0] % xpath
    data['url'] = []

    # static parameters: move them back to the loop when they become dynamic
    #
    url_type = cf['URL_TYPE']
    name_i = cf['URL_CAT_NAME_i']
    entry_j = cf['URL_ENTRY_j']

    # static variables in the loop
    #
    s = n // 10  # increment per slice: 10%, 20%, etc..
    suf = f"-{seq}" if seq > 0 else ''

    categories = 1

    for i in range(n):
        url_category = (cf['URL_CAT_NAME'] + suf).format(i + name_i)
        members = []

        for j in range(m):
            site = cf['URL_ENTRY'].format(j + entry_j, i + name_i)
            members.append("<member>{0}</member>".format(site))
            data['url'].append("http://{0}".format(site))

        element = "<entry name='{0}'><list>{1}</list><type>{2}</type></entry>"\
            .format(url_category, "\n".join(members), url_type)
        clean_element = "@name='{0}' or ".format(url_category)

        data['xml'].append(element)
        data['clean_xml'].append(clean_element)
        data['dump'].append(element)

        time_elapsed = timeit.default_timer() - ti

        if time_elapsed > 1:
            print('.', end="", flush=True)
            ti = timeit.default_timer()

        if n > cf['LARGE_N'] and categories % s == 0:
            print("{:.0%}".format(categories / n), end="", flush=True)

        categories += 1

    data['clean_xml'].append("@name='_z']")
    data['dump'].append("</custom-url-category></profiles>")

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
    shared = 'URL_SHARED'
    if 'XPATH_DG' in cf and 'XPATH_DG_DEFAULT' not in cf:
        if shared not in cf or not cf[shared]:
            for i in range(1, cf['N_PAN_DG'] + 1):
                dg = cf['DG_NAME'] % i
                pan_obj_url(dg, i)
            return

    pan_obj_url()


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
