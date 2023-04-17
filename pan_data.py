#!/usr/bin/python3

"""

pan-os_api v2.1 [20230417]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import json
from os import makedirs

verbose, debug = True, False


def init_data(pre, associations=(), target='PA1', seq=0):
    if target not in cf:
        print("init_data: {}: target not found. Please review config file {}.".format(target, cf['CF_PATH']))
        exit(1)

    d, f, e = ('_dirs', '_files', '_ext')

    data = {
        f: {}
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

    api_set = "type=config&action=set&key={0}&{1}&element="
    api_del = "type=config&action=delete&key={0}&{1}/entry["
    api_key = cf[target]['KEY']

    for asso in ("",) + associations:
        a = "" if asso == "" else "_" + asso
        data['script'+a].append(cmd.format(wget, data[f]['xml'+a], data[f]['out'+a], data[f]['log'+a], url))
        data['xml'+a].append(api_set.format(api_key, "%s"))  # %s for xpath
        data[c+'script'+a].append(cmd.format(wget, data[f][c+'xml'+a], data[f][c+'out'+a], data[f][c+'log'+a], url))
        data[c+'xml'+a].append(api_del.format(api_key, "%s"))  # %s for xpath

    for name in ('dump',):
        data[f][name] = 'data.' + name
        data[name] = []

    if debug:
        print(json.dumps(data, indent=4))

    return data


def write_data(data, target='PA1'):
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

    if verbose:
        print(json.dumps(data, indent=4))
        pass

    files, script, scripts = '_files', 'script', '_scripts'

    for k in data[files].keys():
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

    if verbose:
        # print(json.dumps(data, indent=4))
        pass


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


def go():
    pass


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
