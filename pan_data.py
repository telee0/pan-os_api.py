#!/usr/bin/python3

"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import json
from os import makedirs

import requests
import timeit

verbose, debug = False, False


def init_data(pre, associations=(), target='PA1', seq=0):
    global cf
    
    if target not in cf:
        print("init_data: {}: target not found. Please review config file {}.".format(target, cf['CF_PATH']))
        exit(1)

    d, f, e, p = ('_dirs', '_files', '_ext', '_push')

    data = {
        f: {},
        p: {},
    }

    c = 'clean_'

    script = 'script'
    names = set(cf[f][e].keys())  # script, xml, out, log, etc.
    names.remove(script)
    name = script

    # scripts are at the top level directory
    #
    subdir = cf[d][name]
    data[name] = []
    data[c + name] = []
    data[f][name] = "{0}/{1}{2}".format(subdir, pre, cf[f][name])
    data[f][c + name] = "{0}/{1}{2}".format(subdir, pre, cf[f][c + name])
    for asso in associations:
        name_asso = f"{name}_{asso}"
        data[name_asso] = []
        data[c + name_asso] = []
        data[f][name_asso] = data[f][name]
        data[f][c + name_asso] = data[f][c + name]
        # data[f][name_asso] = "{0}/{1}-{2}{3}".format(subdir, pre, asso, cf[f][name])
        # data[f][c + name_asso] = "{0}/{1}-{2}{3}".format(subdir, pre, asso, cf[f][c + name])

    suf = f"-{seq}" if seq > 0 else ''

    for name in names:
        subdir = cf[d][name]
        data[name] = []
        data[c + name] = []
        data[f][name] = "{0}/{1}{2}{3}".format(subdir, pre, suf, cf[f][name])
        data[f][c + name] = "{0}/{1}{2}{3}".format(subdir, pre, suf, cf[f][c + name])
        for asso in associations:
            name_asso = f"{name}_{asso}"
            data[name_asso] = []
            data[c + name_asso] = []
            data[f][name_asso] = "{0}/{1}{2}-{3}{4}".format(subdir, pre, suf, asso, cf[f][name])
            data[f][c + name_asso] = "{0}/{1}{2}-{3}{4}".format(subdir, pre, suf, asso, cf[f][c + name])

    cmd = "{0} --post-file={1} --no-check-certificate --output-document={2} --append-output={3} '{4}'\n"
    wget = cf['_cmds']['wget']
    url = cf[target]['URL']

    if pre == "uid":  # UID is exceptional
        api_set = "type=user-id&key={0}&cmd="
    else:
        api_set = "type=config&action=set&key={0}&{1}&element="
    api_del_entry = "type=config&action=delete&key={0}&{1}/entry["
    api_del_member = "type=config&action=delete&key={0}&{1}/member["
    api_key = cf[target]['KEY']

    data[p] = {  # data structure for config push
        'target': target,
        'url': url,
        'cfg_list': [],
        'pth_list': {},
    }

    for asso in ("",) + associations:
        a = "" if asso == "" else "_" + asso
        data['script'+a].append(cmd.format(wget, data[f]['xml'+a], data[f]['out'+a], data[f]['log'+a], url))
        data['xml'+a].append(api_set.format(api_key, "%s"))  # %s for xpath
        data[c+'script'+a].append(cmd.format(wget, data[f][c+'xml'+a], data[f][c+'out'+a], data[f][c+'log'+a], url))
        if asso in ('vsys', 'zone', 'vr'):
            data[c+'xml'+a].append(api_del_member.format(api_key, "%s"))  # %s for xpath
        else:
            data[c + 'xml' + a].append(api_del_entry.format(api_key, "%s"))  # %s for xpath
        #
        name = pre + a
        data[p]['cfg_list'].append(name)
        data[p]['pth_list'][name] = {
            'xml': data[f]['xml'+a],
            'out': data[f]['out'+a],
            'log': data[f]['log'+a]
        }

    for name in ('dump',):
        data[f][name] = 'data.' + name
        data[name] = []

    if debug:
        print(json.dumps(data, indent=4))

    return data


def write_data(data, target='PA1'):
    global verbose, debug

    if target not in cf:
        print("write_data: {}: target not found. Please review config file {}.".format(target, cf['CF_PATH']))
        exit(1)

    # additional directory for non-default target
    #
    target_dir = ''
    if target != 'PA1':
        target_dir = target + '/'
        makedirs(target_dir, exist_ok=True)
        for subdir in cf['_dirs'].values():
            if len(subdir) > 1:
                makedirs(target_dir + subdir, exist_ok=True)

    if debug:
        print(json.dumps(data, indent=4))

    files, script, scripts = '_files', 'script', '_scripts'

    keys_fwd, keys_bwd = [], []
    for k in data[files].keys():
        if k.startswith('clean_script'):
            keys_bwd.append(k)
        else:
            keys_fwd.append(k)
    keys_ordered = keys_fwd + keys_bwd[::-1]  # clean scripts have commands in reversed order

    for k in keys_ordered:
        if len(data[k]) > 0:  # file content has positive line count
            file = target_dir + data[files][k]
            with open(file, 'a') as f:
                f.write("\n".join(data[k]))
                if debug:
                    print("{0}: file generated".format(file))
            data[k].clear()  # list cleared once data written to the associated file

    if script in data[files]:
        path = target_dir + data[files][script]
        if len(cf[scripts]) == 0 or cf[scripts][-1] != path:  # check if the script is already there in the master
            cf[scripts].append(path)

    if debug:
        print(json.dumps(data, indent=4))

    cf['_push'].append(data['_push'])


def gen_xpath(shared, local_path, dg=None):

    # check for multiple choices (in case local_path needs dependency check here)
    #
    if isinstance(local_path, tuple):
        local_path_0, local_path_1 = local_path
    else:
        local_path_0 = local_path_1 = local_path

    if 'XPATH_DG' in cf:
        if shared in cf and cf[shared]:
            x = "xpath=/config/shared"
        elif dg is not None:
            x = cf['XPATH_DG'].format(dg)
        else:
            x = cf['XPATH_DG_DEFAULT']  # default to DG in config file
        xpath = "{0}/{1}".format(x, local_path_0)
    else:
        xpath = "{0}/{1}".format(cf['XPATH'], local_path_1)

    return xpath


def push_data():
    global cf
    global verbose, debug

    t0 = timeit.default_timer()
    ti = t0

    for p in cf['_push']:
        url = p['url']
        target = p['target']
        prefix = "PA2/" if target == "PA2" else ""
        status = 'ok'
        for cfg in p['cfg_list']:
            print(f"\nPushing {cfg} to {target}..", end=" ", flush=True)
            paths = p['pth_list'][cfg]
            xml_path = prefix + paths['xml']  # xml/uid.xml
            out_path = prefix + paths['out']  # logs/uid.out.xml
            log_path = prefix + paths['log']  # logs/uid.log
            try:
                with open(xml_path, 'r', encoding="utf-8") as f:
                    lines = f.readlines()
                params_line = lines[0].strip()

                from urllib.parse import parse_qsl
                params = dict(parse_qsl(params_line))

                if params['key'] == 'None':
                    status = 'skip'
                    if verbose:
                        print("API key invalid ", end="")
                    break

                xml_data = ''.join(lines[1:]).strip()

                data_key = "element" if cfg != "uid" else "cmd"
                post_data = {**params, data_key: xml_data}

                if debug:
                    print(json.dumps(post_data, indent=4))

                response = requests.post(
                    url,
                    data=post_data,
                    verify=False,  # equivalent to --no-check-certificate
                    timeout=cf['PUSH_TIMEOUT'],
                )
                with open(out_path, 'ab') as f:
                    f.write(response.content + b"\n")
                with open(log_path, 'a') as log_file:
                    log_file.write(f"{response.status_code} {response.reason}\n")
            except requests.RequestException as e:
                with open(log_path, 'a') as log_file:
                    log_file.write(f"Request failed: {e}\n")

        print(cf['_msgs'][status] % (timeit.default_timer() - ti), end="")
        ti = timeit.default_timer()


def go():
    pass


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
