#!/usr/bin/python3

"""

pan-os_api v2.2 [20230717]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime
from os import makedirs
from os.path import exists

verbose, debug = True, False


def init():
    cf['CF_PATH'] = args.conf

    if 'TARGET' not in cf:
        print("init: TARGET not set. Please review config file {}.".format(cf['CF_PATH']))
        exit(1)

    # pass from environment variables
    #
    e, p = 'PASSENV', 'PASS'

    for pa in ['PA1', 'PA2']:
        pass_ = os.getenv(cf[pa][e]) if e in cf[pa] else None
        if pass_ is not None and len(pass_) > 0:
            cf[pa][p] = pass_

    # parameters defined in code to just save config effort
    #
    cf['LARGE_N'] = 9999  # n large enough to display progress in % (10%, 20%, etc.)

    # preset xpaths
    #
    # XPATH / XPATH_DG / XPATH_DG_DEFAULT / XPATH_TPL
    #
    target = cf['TARGET']
    lhost = cf['LHOST']
    vsys = cf['VSYS']

    if target == 'PA':
        cf['XPATH'] = "xpath=/config/devices/entry[@name='{0}']/vsys/entry[@name='{1}']".format(lhost, vsys)
        cf['XPATH_TPL'] = "xpath="
    elif target == 'PANORAMA':
        cf['XPATH_DG'] = "xpath=/config/devices/entry[@name='{0}']" \
            "/device-group/entry[@name='{1}']".format(lhost, '{}')
        if 'PANORAMA_DEVICE_GROUP' in cf and len(cf['PANORAMA_DEVICE_GROUP']) > 0:
            cf['XPATH_DG_DEFAULT'] = "xpath=/config/devices/entry[@name='{0}']" \
                "/device-group/entry[@name='{1}']".format(lhost, cf['PANORAMA_DEVICE_GROUP'])
        if 'PANORAMA_TEMPLATE' in cf:
            cf['XPATH_TPL'] = "xpath=/config/devices/entry[@name='{0}']" \
                "/template/entry[@name='{1}']".format(lhost, cf['PANORAMA_TEMPLATE'])
        elif 'PANORAMA_TEMPLATE_STACK' in cf:
            cf['XPATH_TPL'] = "xpath=/config/devices/entry[@name='{0}']" \
                "/template-stack/entry[@name='{1}']".format(lhost, cf['PANORAMA_TEMPLATE_STACK'])
    else:
        print("init: {}: unknown TARGET. Please review config file {}.".format(target, cf['CF_PATH']))
        exit(1)

    c, d, f, e, m, s = ('_cmds', '_dirs', '_files', '_ext', '_msgs', '_scripts')

    cf.update({
        c: {  # commands
            # 'wget': "wget --tries=2 --timeout=10 --dns-timeout=10 --connect-timeout=10",
            'wget': "wget --tries=2 --timeout=5",
        },
        d: {  # directories
            'script': '.',
            'xml': 'xml',
            'out': 'logs',
            'log': 'logs',
        },
        f: {  # files and file extensions
            e: {
                'script': '.sh',
                'xml': '.xml',
                'out': '.out.xml',
                'log': '.log',
            },
        },
        m: {
            'ok': 'OK (%.2fs)'
        },
        s: [],
    })

    for name, ext in cf[f][e].items():
        cf[f][name] = ext
        cf[f]['clean_' + name] = '-clean' + ext

    t = datetime.now().strftime('%Y%m%d%H%M')
    ddhhmm = t[6:12]
    job_dir = "job-{0}".format(ddhhmm)

    # prepare the directory structure for job files
    #
    makedirs(job_dir, exist_ok=True)
    os.chdir(job_dir)

    for subdir in cf[d].values():
        if len(subdir) > 1:
            makedirs(subdir, exist_ok=True)


def read_conf(cf_path):
    if not exists(cf_path):
        print("{0}: file not found".format(cf_path))
        exit(1)
    name = "conf"
    spec = importlib.util.spec_from_file_location(name, cf_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def write_job_files():
    with open('pan.conf', 'a') as f:
        f.write(json.dumps(cf, indent=4))

    with open('config.sh', 'a') as f:
        for script in cf['_scripts']:
            f.write("sh {}\n".format(script))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pan.py', description='Script to generate PA/Panorama config.')
    parser.add_argument('-c', '--conf', nargs='?', type=str, default="conf/pa.py", help="config file")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose mode")
    parser.add_argument('password', nargs='?')
    parser.print_help()

    args = parser.parse_args()

    if debug:
        print()
        print("args == {0}".format(args))

    read_conf(args.conf)
    from conf import cf

    init()

    import pan_api
    import pan_device_groups
    import pan_templates
    import pan_obj_addr
    import pan_obj_addr_groups
    import pan_obj_svc
    import pan_obj_svc_groups
    import pan_obj_url
    import pan_net_zones
    import pan_net_if_eth
    import pan_net_if_lo
    import pan_net_if_tun
    import pan_net_dns_proxy
    import pan_rules_sec
    import pan_rules_nat
    import pan_rules_pbf
    import pan_vpn_ike_gw
    import pan_vpn_ipsec_tun
    import pan_vr_static
    import pan_vr_bgp
    import pan_local_users
    import pan_uid

    pan_api.go()
    pan_device_groups.go()
    pan_templates.go()
    pan_obj_addr.go()
    pan_obj_addr_groups.go()
    pan_obj_svc.go()
    pan_obj_svc_groups.go()
    pan_obj_url.go()
    pan_net_zones.go()
    pan_net_if_eth.go()
    pan_net_if_lo.go()
    pan_net_if_tun.go()
    pan_net_dns_proxy.go()
    pan_rules_sec.go()
    pan_rules_nat.go()
    pan_rules_pbf.go()
    pan_vpn_ike_gw.go()
    pan_vpn_ipsec_tun.go()
    pan_vr_static.go()
    pan_vr_bgp.go()
    pan_local_users.go()
    pan_uid.go()

    if verbose:
        print()
        # print(json.dumps(cf, indent=4))

    write_job_files()
