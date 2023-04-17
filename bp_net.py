#!/usr/bin/python3

"""

pan-os_api v2.1 [20230417]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

"""

import datetime
# import timeit

verbose, debug = True, False

network_name = "Network-POC14253-200"


# a handy function to generate BP network neighborhood config in XML
#
def bp_net_config():
    swconfig = "version:9.22.116.103 build number:434726 strikebuild:452772"
    serialno = "XGS12-G0471034"
    schemaver = "434726.452772"
    author = "telee"
    time_zone = "SGT"

    interfaces = 8
    interface_mac = "02:1A:C5:{0:X}:00:00"

    client_server_pairs = 200

    gw1 = "1.1.11.253"
    gw2 = "2.2.22.253"

    netmask = 16  # netmask shared among all client and server network ranges
    count = 250   # number of IP's from each of the network ranges

    elements = []

    for i in range(1, client_server_pairs + 1):
        element = f"""
    <domain name="Client{i}" external="false" interface="1" mtu="1500" ignorepause="false">
      <subnet behind_snapt="false" proxy="true" l2="02:1A:C5:01:00:00" netaddr="1.1.0.0" netmask="16" gateway="{gw1}" \
ip_v="4" type="hosts" isipsec="false" enable_stats="false" mac_count="250">
        <range min="1.1.{i}.1" max="1.1.{i}.250"/>
        <params/>
        <composition>
          <stack type="ip_static_hosts" id="Client{i}"/>
          <stack type="interface" id="Interface 1"/>
        </composition>
        <createdFrom>Client{i}</createdFrom>
      </subnet>
      <tag id="Client{i}"/>
      <endpoints>Client{i}</endpoints>
    </domain>
    <domain name="Server{i}" external="false" interface="2" mtu="1500" ignorepause="false">
      <subnet behind_snapt="false" proxy="true" l2="02:1A:C5:02:00:00" netaddr="2.2.0.0" netmask="16" gateway="{gw2}" \
ip_v="4" type="hosts" isipsec="false" enable_stats="false" mac_count="250">
        <range min="2.2.{i}.1" max="2.2.{i}.250"/>
        <params/>
        <composition>
          <stack type="ip_static_hosts" id="Server{i}"/>
          <stack type="interface" id="Interface 2"/>
        </composition>
        <createdFrom>Server{i}</createdFrom>
      </subnet>
      <tag id="Server{i}"/>
      <endpoints>Server{i}</endpoints>
    </domain>"""

        elements.append(element)

    domains = "".join(elements)

    elements = []

    for i in range(1, client_server_pairs + 1):
        element = f"""
      <connection type="path_basic">
        <subnet domain="Client{i}" interface="1" external="false" vlan="0"/>
        <subnet domain="Server{i}" interface="2" external="false" vlan="0"/>
        <string id="id">path_basic_{i}</string>
        <reference id="source_container">Client{i}</reference>
        <reference id="destination_container">Server{i}</reference>
      </connection>"""

        elements.append(element)

    connections = "<connections>" + "".join(elements) + "</connections>"

    elements = []

    for i in range(1, interfaces + 1):

        mac_address = interface_mac.format(i)

        element = f"""
      <element type="interface">
        <string id="id">Interface {i}</string>
        <int id="number">{i}</int>
        <int id="mtu">1500</int>
        <boolean id="duplicate_mac_address">false</boolean>
        <boolean id="use_vnic_mac_address">true</boolean>
        <boolean id="ignore_pause_frames">false</boolean>
        <mac_address id="mac_address">{mac_address}</mac_address>
        <enum id="vlan_key">outer_vlan</enum>
      </element>"""

        elements.append(element)

    for i in range(1, client_server_pairs + 1):
        element = f"""
      <element type="ip_static_hosts">
        <string id="id">Client{i}</string>
        <ip_address id="ip_address">1.1.{i}.1</ip_address>
        <ip_address id="gateway_ip_address">{gw1}</ip_address>
        <int id="netmask">{netmask}</int>
        <int id="count">{count}</int>
        <int id="psn_netmask">8</int>
        <int id="maxmbps_per_host"/>
        <reference id="default_container">Interface 1</reference>
        <boolean id="behind_snapt">false</boolean>
        <boolean id="enable_stats">false</boolean>
        <boolean id="proxy">true</boolean>
        <enum id="ip_selection_type">sequential_ip</enum>
        <tags id="tags">
          <tag id="Client{i}"/>
        </tags>
      </element>
      <element type="ip_static_hosts">
        <string id="id">Server{i}</string>
        <ip_address id="ip_address">2.2.{i}.1</ip_address>
        <ip_address id="gateway_ip_address">{gw2}</ip_address>
        <int id="netmask">{netmask}</int>
        <int id="count">{count}</int>
        <int id="psn_netmask">8</int>
        <int id="maxmbps_per_host"/>
        <reference id="default_container">Interface 2</reference>
        <boolean id="behind_snapt">false</boolean>
        <boolean id="enable_stats">false</boolean>
        <boolean id="proxy">true</boolean>
        <enum id="ip_selection_type">sequential_ip</enum>
        <tags id="tags">
          <tag id="Server{i}"/>
        </tags>
      </element>"""

        elements.append(element)

    network_model = "<networkModel>" + "".join(elements) + connections + "</networkModel>"

    # output the config
    #
    timestamp = datetime.datetime.now().astimezone().strftime(
        f"%Y-%m-%dT%H:%M:%S {time_zone}")  # "%Y-%m-%dT%H:%M:%S %Z")

    return f"""
<?xml version="1.0"?>
<modelExport swconfig="{swconfig}" serialno="{serialno}" schemaver="{schemaver}">
  <network name="{network_name}" schemaver="{schemaver}" author="{author}" createdBy="{author}" \
createdOn="{timestamp}" timestamp="{timestamp}" class="custom" revision="9" saved="true" canSave="true" namechanged="false">
    <tpid interface="1" vlan_key="outer_vlan">8100</tpid>
    <tpid interface="2" vlan_key="outer_vlan">8100</tpid>
{domains}
{network_model}
    <params/>
    <label>
      <string>{network_name}</string>
    </label>
  </network>
</modelExport>"""


# write the BP network neighborhood config
#
def bp_net_print(output):
    if debug:
        print(output)
    file = network_name + '.bpt'
    with open(file, 'a') as f:
        f.write(output)
        print("{0}: file generated".format(file))


def go():
    bp_net_print(
        bp_net_config()
    )


if __name__ == '__main__':
    cf = {}
    go()
else:
    from __main__ import cf
    verbose = cf['VERBOSE']
    debug = cf['DEBUG']
