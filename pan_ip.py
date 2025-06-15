"""

pan-os_api v2.3 [20250607]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import ipaddress

verbose, debug = False, True


def generate_loopback(ip_format, ip_n, with_prefix=False):
    ip_iface = ipaddress.ip_interface(ip_format)
    prefix_len = ip_iface.network.prefixlen
    ip_int = int(ip_iface.ip)

    if debug:
        print("generate_loopback")
        print("ip_iface", ip_iface)
        print("prefix_len", prefix_len)
        print("ip_int", ip_int)

    prefix = ""
    if with_prefix:
        prefix = f"/{prefix_len}"

    ip_list = []
    i, n  = 0, ip_n

    for i in range(n):
        ip = ipaddress.ip_address(ip_int)
        ip_list.append(f"{ip}{prefix}")
        ip_int += 1

    return ip_list


def generate_ip(ip_format, ip_n, ip_size, with_prefix=True, reset_offset=False):
    def_name = "generate_ip"

    ip_iface = ipaddress.ip_interface(ip_format)
    prefix_len = ip_iface.network.prefixlen
    ip_int = int(ip_iface.ip)
    net_int = int(ip_iface.network.network_address)
    offset_init = max(1, ip_int - net_int)  # this should never be 0
    net_step = 2 ** (ip_iface.max_prefixlen - prefix_len)

    if debug:
        print(def_name)
        for v in ['ip_iface', 'prefix_len', 'ip_int', 'net_int', 'offset_init', 'net_step']:
            print(f"{v}: {locals()[v]}")

    prefix = ""
    if with_prefix:
        prefix = f"/{prefix_len}"

    ip_list = []
    i, n  = 0, ip_n

    while i < n:
        net = ipaddress.ip_network((net_int, prefix_len), strict=True)
        broadcast_int = int(net.broadcast_address)
        for offset in range(offset_init, ip_size + offset_init):
            ip_int = net_int + offset
            if ip_int >= broadcast_int:
                print(f"{def_name}: subnet overflow with ip_int {ip_int} ({ipaddress.ip_address(ip_int)})")
            try:
                ip = ipaddress.ip_address(ip_int)
                ip_list.append(f"{ip}{prefix}")
                i += 1
            except Exception as e:
                print(f"{def_name}: {ip_int}: {e}")
                return []
        if reset_offset:
            offset_init = 1
        net_int += net_step

    return ip_list


def generate_ip_ranges(ip_format, range_n, range_size, with_prefix=False):
    def_name = "generate_ip_ranges"

    ip_iface = ipaddress.ip_interface(ip_format)
    prefix_len = ip_iface.network.prefixlen
    ip_int = int(ip_iface.ip)
    net_int = int(ip_iface.network.network_address)
    offset = max(1, range_size)  # this should never be 0
    net_step = 2 ** (ip_iface.max_prefixlen - prefix_len)

    if debug:
        print(def_name)
        for v in ['ip_iface', 'prefix_len', 'ip_int', 'net_int', 'offset_init', 'net_step']:
            print(f"{v}: {locals()[v]}")

    prefix = ""
    if with_prefix:
        prefix = f"/{prefix_len}"

    ip_range_list = []
    n  = range_n

    for i in range(n):
        ip_int_last = ip_int + offset - 1
        ip_first = ipaddress.ip_address(ip_int)
        ip_last = ipaddress.ip_address(ip_int_last)
        ip_range_list.append(f"{ip_first}{prefix}-{ip_last}{prefix}")
        ip_int += net_step

    return ip_range_list


def generate_net(ip_format, net_n, with_prefix=True):
    def_name = "generate_net"

    ip_iface = ipaddress.ip_interface(ip_format)
    prefix_len = ip_iface.network.prefixlen
    net_int = int(ip_iface.network.network_address)
    net_step = 2 ** (ip_iface.max_prefixlen - prefix_len)

    if debug:
        print(def_name)
        for v in ['ip_iface', 'prefix_len', 'net_int', 'net_step']:
            print(f"{v}: {locals()[v]}")

    prefix = ""
    if with_prefix:
        prefix = f"/{prefix_len}"

    net_list = []

    for i in range(net_n):
        ip = ipaddress.ip_address(net_int)
        net_list.append(f"{ip}{prefix}")
        net_int += net_step

    return net_list


def ip_version(ip_format):
    ip_iface = ipaddress.ip_interface(ip_format)
    return 4 if ip_iface.version == 4 else 6


def go():
    # samples
    #
    print(generate_net("192.168.0.1/24", 10), "\n")
    print(generate_loopback("127.0.0.1", 10), "\n")
    print(generate_ip("10.0.0.1/30", 10, 2), "\n")


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
