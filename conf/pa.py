#!/usr/bin/python3

"""

pan-os_api v2.2 [20230717]

Scripts to generate PA/Panorama config

    by Terence LEE <telee.hk@gmail.com>

Details at https://github.com/telee0/pan-os_api.py.git

--------------------------------------------------------------------------------

Configuration

Supported config as follows.

Device > Local users
Network > Interfaces > Ethernet   (with vsys, zone and vr assignment)
Network > Interfaces > Loopback   (with vsys, zone and vr assignment)
Network > Interfaces > Tunnel     (with vsys, zone and vr assignment)
Network > Zones
Network > DNS Proxy
Network > IKE Gateways
Network > IPSec Tunnels (with static routes through tunnels)
Objects > Addresses
Objects > Address Groups
Objects > Services
Objects > Service Groups
Objects > Custom URL Category with url.txt
Policies > Security
Policies > NAT
Policies > PBF
Network > VR > Static Routes
Network > VR > BGP peer groups x peers

User-ID mapping

(Panorama only)
Panorama > Device Groups
Panorama > Templates

Features and Capacity, All PAN-OS Releases

https://loop.paloaltonetworks.com/docs/DOC-3950

"""

cf = {
    'TARGET': "PA",
    # 'TARGET': "PANORAMA",

    'PA1': {
        'HOST': "192.168.1.1",
        'USER': "admin",
        'PASS': "",           # this can be overridden with the environment variable see the next key PASSENV
        'PASSENV': 'PAPASS',  # name of the environment variable for the password
        'DESC': "main device to be configured"
    },

    'PA2': {
        'HOST': "192.168.1.2",
        'USER': "admin",
        'PASS': "",           # this can be overridden with the environment variable see the next key PASSENV
        'PASSENV': 'PAPASS',  # name of the environment variable for the password
        'DESC': "second device as the VPN peer"
    },

    'VERBOSE': False,
    'DEBUG': False,
}

cf.update({

    # Panorama default device group and template/stack
    #

    # 'PANORAMA_DEVICE_GROUP': "POC-TEST",
    'PANORAMA_TEMPLATE': "Template-001",
    'PANORAMA_TEMPLATE_STACK': "TempStack-001",

    # --------------------------------------------------------------------------------

    'CONFIG_VERSION': "9.1.0",
    'LHOST': "localhost.localdomain",
    'VSYS': "vsys1",

    # 'DEFAULT_ZONE1': "L3-Trust",
    # 'DEFAULT_ZONE2': "L3-Untrust",
    'DEFAULT_ZONE1': "L3-trust",
    'DEFAULT_ZONE2': "L3-untrust",
    'DEFAULT_ZONE3': "VPN",

    'DEFAULT_VR': "default",

    'N_NET_IF_ETHERNET': 16,  # number of subinterfaces per each physical ethernet
    'N_NET_IF_LOOPBACK': 10,
    'N_NET_IF_TUNNEL': 32,
    'N_NET_ZONES': 0,
    'N_NET_DNS_PROXY': 10,

    # IPSec VPN
    #
    'N_NET_IKE': 32,
    'N_NET_IPSEC': 32,

    # Objects
    #
    'N_OBJ_ADDRESS': 500,
    'N_OBJ_ADDRESS_GROUP': 0,
    'N_OBJ_SERVICE': 0,
    'N_OBJ_SERVICE_GROUP': 0,

    # Total custom URL entries = N_OBJ_URL_CATS x N_OBJ_URL_ENTRIES
    #
    'N_OBJ_URL_CATS': 0,
    'N_OBJ_URL_ENTRIES': 9,

    # policy rules
    #
    'N_RULES_SEC': 0,
    'N_RULES_NAT': 0,
    'N_RULES_PBF': 0,

    # virtual router config
    #
    'N_VR_STATIC': 0,
    'N_VR_BGP_PEER_GROUPS': 0,
    'N_VR_BGP_PEERS_PER_GROUP': 6,

    # total IP-user mappings = N_UID_NETS x N_UID_ENTRIES
    #
    'N_UID_NETS': 6,
    'N_UID_ENTRIES': 30,

    # Local users
    #
    'N_USERS': 0,

    # Panorama only
    #
    'N_PAN_DG': 0,  # device groups
    'N_PAN_TPL': 0,  # templates
})

# --------------------------------------------------------------------------------
#
# Detailed settings
#

cf.update({

    # Panorama device groups and templates
    #
    # 'N_PAN_DG': 10,
    'DG_NAME': "DG-%04d",
    # 'N_PAN_TPL': 1,
    'TPL_NAME': "Template-%04d",

    # 'N_USERS': 0
    'USER_NAME': "user%03d",  # user001, user002, etc.
    'USER_PASS': "pass123_",  # create an authentication profile for testing

    # --------------------------------------------------------------------------------
    #
    # ethernet subinterfaces, loopback and tunnel interfaces
    #

    # 'N_NET_IF_ETHERNET': 0,
    'IF_ETHERNET_LIST': ["ethernet1/11", "ethernet1/12"],  # list of parent interfaces
    'IF_ETHERNET_TYPE': "L3",  # only L3 is assumed
    'IF_ETHERNET_TAG_i': 11,   # initial VLAN tag
    # 'IF_ETHERNET_IP': None,  # "",
    'IF_ETHERNET_IP': "11.11.0.1/30",
    # 'IF_ETHERNET_IP': "2211:11::1/126",
    'IF_ETHERNET_VR': cf['DEFAULT_VR'],
    'IF_ETHERNET_ZONE': cf['DEFAULT_ZONE2'],

    # 'N_NET_IF_LOOPBACK': 0,
    'IF_LOOPBACK_NAME_i': 10,  # i, the initial index value
    # 'IF_LOOPBACK_IP': None,  # "",
    # 'IF_LOOPBACK_IP': "100.0.0.1/32",
    'IF_LOOPBACK_IP': "2100::1/120",
    'IF_LOOPBACK_VR': cf['DEFAULT_VR'],
    'IF_LOOPBACK_ZONE': cf['DEFAULT_ZONE1'],

    # 'N_NET_IF_TUNNEL': 0,
    'IF_TUNNEL_NAME_i': 11,  # i, the initial index value
    # 'IF_TUNNEL_IP': None,  # "",
    # 'IF_TUNNEL_IP': "227.11.11.1/30",
    'IF_TUNNEL_IP': "2227::1/126",
    'IF_TUNNEL_VR': cf['DEFAULT_VR'],
    'IF_TUNNEL_ZONE': cf['DEFAULT_ZONE3'],

    # 'N_NET_ZONES': 0,
    'ZONE_NAME': "Zone-%03d",
    'ZONE_UID': True,  # True or False, True to enable User-ID

    # 'N_NET_DNS_PROXY': 0,
    'DNS_PROXY_NAME': "DNS-%d",
    'DNS_PROXY_PRIMARY': "1.1.1.1",  # primary DNS server IP
    'DNS_PROXY_SECONDARY': "8.8.8.8",  # secondary DNS server IP
    'DNS_PROXY_STATIC_ENTRIES': 100,  # number of static entries
    'DNS_PROXY_STATIC_FQDN': "h%d.poc.com",  # FQDN of static entries
    'DNS_PROXY_STATIC_ADDR': "33.33.33.33",  # IP of static entries

    # --------------------------------------------------------------------------------
    #
    # VPN configuration: IKE gateways and IPSec tunnels
    #

    # 'N_NET_IKE': 100,
    'IKE_NAME': "IKE_Gateway-{0}",
    'IKE_NAME_i': 11,  # i, the initial index value
    'IKE_VERSION': "ikev2-preferred",  # ikev1, ikev2 or ikev2-preferred
    # 'IKE_INTERFACE_LIST': [("loopback.{0}", 1, 16],    # loopback interfaces
    # 'IKE_INTERFACE_LIST': [("ethernet1/2", 1, 1)],     # ethernet/2
    # 'IKE_INTERFACE_LIST': [("ethernet1/{0}", 1, 32)],  # ethernet1/1, .., ethernet1/32
    'IKE_INTERFACE_LIST': [("ethernet1/11.{0}", 1, 16), ("ethernet1/12.{0}", 1, 16)],  # list of heterogeneous interfaces
    'IKE_IP_LOCAL': "11.11.0.1",  # prefix specified separately
    'IKE_IP_PEER': "11.11.0.2",   # prefix specified separately
    'IKE_IP_PREFIX': "/30",       # required for mirrored config
    'IKE_PRESHARED_KEY': "test123",  # -AQ==cojt0Pw//L6ToM8G41aOKFIWh7w=CVJ5/F84i6cL7ejjM15fRA==
    'IKE_CRYPTO_PROFILE': "default",

    # 'N_NET_IPSEC': 1200,
    'IPSEC_NAME': "IPSec_Tunnel-{0}",        # IPSec_Tunnel-$i
    'IPSEC_NAME_i': 11,                      # initial index value for IPSec tunnel
    'IPSEC_TUNNEL_INTERFACE': 'tunnel.{0}',  # Tunnel interface
    'IPSEC_TUNNEL_INTERFACE_i': 11,
    # 'IPSEC_IKE_GATEWAY': "IKE_Gateway",    # shared
    'IPSEC_IKE_GATEWAY': "IKE_Gateway-{0}",  # IKE_Gateway-$i
    'IPSEC_IKE_GATEWAY_i': 11,               # initial index value for IKE gateway
    'IPSEC_CRYPTO_PROFILE': "default",
    'IPSEC_REPLAY_PROTECTION': "no",
    'IPSEC_PROXY_ID_ADD': False,  # True or False, True to include proxy IDs
    'IPSEC_PROXY_ID_LIMIT': 250,  # max number of proxy IDs in an IPSec tunnel. Limit of a tunnel interface is 250
    'IPSEC_PROXY_ID_NAME': "Proxy_ID-%d.%d",  # Proxy_ID-$i.$j
    'IPSEC_PROXY_ID_PROTOCOL': "any",
    'IPSEC_IP_LOCAL': "1.1.0.1",
    'IPSEC_IP_LOCAL_PREFIX': "/24",
    'IPSEC_IP_REMOTE': "2.2.0.1",
    'IPSEC_IP_REMOTE_PREFIX': "/24",
    'IPSEC_ROUTE_ADD': True,  # True or False, whether routes should also be installed with IPSec tunnels
    'IPSEC_ROUTE_NAME': "Tunnel_Route-{0}",
    'IPSEC_ROUTE_i': 11,
    'IPSEC_VR': cf['DEFAULT_VR'],

    # --------------------------------------------------------------------------------
    #
    # Objects: addresses/groups, services/groups, URL categories
    #

    # 'N_OBJ_ADDRESS': 0,
    'ADDR_NAME': "Address-%03d",
    # --- IP Netmask
    # 'ADDR_TYPE': "ip-netmask",
    # 'ADDR_ADDRESS': "10.0.0.0/24",
    # 'ADDR_ADDRESS': "2401:b200:2000::/64",  # 2401:b200:2000:$i$j::/64, $i is hidden
    # --- IP Range
    # 'ADDR_TYPE': "ip-range",
    # 'ADDR_RANGE_SIZE': 10,
    # 'ADDR_ADDRESS': "192.168.0.8/24",
    # 'ADDR_ADDRESS': "2401:b200:2000::1/96",
    # --- FQDN
    'ADDR_TYPE': "fqdn",
    'ADDR_ADDRESS': "w{0}.poc.local",
    'ADDR_SHARED': False,

    # N_OBJ_ADDRESS_GROUP=0
    'ADDR_GROUP_NAME': "Address_Group-%03d",
    'ADDR_GROUP_MEMBER_COUNT': 5,
    'ADDR_GROUP_SHARED': False,  # make sure addresses are visible to groups

    # address objects, in case they are not set previously
    #
    # 'N_OBJ_ADDRESS': 5,  # addresses will be recycled if this number is too small
    # 'ADDR_NAME': "Address-%03d",  # in case it is not set previously

    # N_OBJ_SERVICE=0
    #
    'SERVICE_NAME': "service-%s%05d",
    'SERVICE_PROTOCOL': "both",  # "tcp" or "udp" or "both"
    'SERVICE_PORT_DST': 10000,  # initial dst port number
    'SERVICE_PORT_SRC': 0,  # non-empty value will make source port grow with the destination port
    'SERVICE_SHARED': True,

    # N_OBJ_SERVICE_GROUP=0
    'SERVICE_GROUP_NAME': "Service_Group-%03d",
    'SERVICE_GROUP_PROTOCOL': "",  # "tcp", "udp" or "both", or else use SERVICE_PROTOCOL
    # 'SERVICE_GROUP_PROTOCOL': "udp",  # "tcp", "udp" or "both", or else use SERVICE_PROTOCOL
    'SERVICE_GROUP_MEMBER_COUNT': 5,
    'SERVICE_GROUP_SHARED': False,  # make sure services are visible to groups

    # Custom URL categories
    #
    # N_OBJ_URL_CATS=4
    # N_OBJ_URL_ENTRIES=1000
    'URL_CAT_NAME': "URL_Category-%d",
    'URL_CAT_NAME_i': 1,  # i, the initial index value
    'URL_ENTRY_j': 1,  # j, the initial index value
    'URL_ENTRY': "w%d.d%d.com",
    'URL_TYPE': "URL List",
    # 'URL_SHARED': True,

    # --------------------------------------------------------------------------------
    #
    # Policy rules: security, NAT, and PBF rules
    #

    # 'N_RULES_SEC': 0,
    'SEC_RULEBASE': "pre-rulebase",  # pre-rulebase or post-rulebase for Panorama
    # 'SEC_NAME': "Rule-%5d",  # Rule-00001, Rule-00002, etc.
    'SEC_NAME': "Rule-%d",  # Rule-1, Rule-2, etc.
    'SEC_SRC_ZONE': cf['DEFAULT_ZONE1'],
    'SEC_DST_ZONE': cf['DEFAULT_ZONE2'],
    'SEC_SOURCE': "1.1.%.0s%d.0/24",  # 1.1.$j.0/24, $i is hidden
    'SEC_DESTINATION': "2.2.%.0s%d.0/24",  # 2.2.$j.0/24, $i is hidden
    # 'SEC_SOURCE': "192.0.%d.%d",  # 192.0.$i.$j
    # 'SEC_DESTINATION': "200.0.%d.%d",  # 200.0.$i.$j
    # 'SEC_SERVICE': "applicaton-default",
    'SEC_SERVICE': "any",
    'SEC_ACTION': "deny",
    # 'SEC_SHARED': True,

    # 'N_RULES_NAT': 0,
    'NAT_RULEBASE': "pre-rulebase",  # pre-rulebase or post-rulebase for Panorama
    # 'NAT_NAME': "NAT_Rule-%5d",
    'NAT_NAME': "NAT_Rule-%d",
    'NAT_SRC_ZONE': cf['DEFAULT_ZONE1'],
    'NAT_DST_ZONE': cf['DEFAULT_ZONE2'],
    'NAT_SOURCE': "1.1.%d%.0s.0/24",  # 1.1.$i.0/24, $j is hidden
    'NAT_DESTINATION': "2.2.%.0s%d.0/24",  # 2.2.$j.0/24, $i is hidden
    'NAT_SERVICE': "any",
    # 'NAT_SHARED': True,

    # 'N_RULES_PBF': 0,
    'PBF_RULEBASE': "pre-rulebase",  # pre-rulebase or post-rulesbase for Panorama
    'PBF_NAME': "PBF_Rule-%d",
    'PBF_SRC_ZONE': cf['DEFAULT_ZONE1'],
    'PBF_SOURCE': "10.%d.%d.0/24",  # 10.$i.$j.0/24
    'PBF_SERVICE': "any",
    'PBF_EGRESS_INTERFACE': "ethernet1/21",
    'PBF_NEXTHOP': "100.1.0.100",
    # 'PBF_SHARED': True,

    # --------------------------------------------------------------------------------
    #
    # VR configuration: static routes, BGP groups
    #

    # 'N_VR_STATIC': 0,
    'VR_STATIC_VR': cf['DEFAULT_VR'],
    'VR_STATIC_NAME': "Route-%d",
    # 'VR_STATIC_DESTINATION': "192.168.%d.%d",  # 192.168.$i.$j
    'VR_STATIC_DESTINATION': "192.168.%.0s%d.0/24",  # 192.168.$j.0/24, $i is hidden
    # 'VR_STATIC_INTERFACE': "ethernet1/23",
    'VR_STATIC_INTERFACE': "",
    'VR_STATIC_NEXTHOP': "100.1.0.2",

    # 'N_VR_BGP_PEER_GROUPS': 1,
    # 'N_VR_BGP_PEERS_PER_GROUP': 1000,
    #
    'VR_BGP_VR': cf['DEFAULT_VR'],
    'VR_BGP_PEER_GROUP_NAME': "Group-%d",  # Group-$i
    'VR_BGP_PEER_GROUP_TYPE': "ebgp",  # ebgp is supported at the moment
    'VR_BGP_PEER_NAME': "Peer%d-%d",  # Peer$i-$j
    'VR_BGP_PEER_AS': "200",
    'VR_BGP_PEER_LOCAL_INT': "ethernet1/13.%d",  # ethernet1/13.$i
    'VR_BGP_PEER_LOCAL_IP': "192.%d.%d.1/24",  # 192.$j.$k.1/24
    'VR_BGP_PEER_LOCAL_IP_OCTET_j': 168,
    'VR_BGP_PEER_LOCAL_IP_OCTET_k': 3,
    'VR_BGP_PEER_PEER_IP': "192.%d.%d.2",  # 192.$j.$k.2

    # --------------------------------------------------------------------------------
    #
    # IP-user mappings
    #

    # 'N_UID_NETS': 4,
    # 'N_UID_ENTRIES': 0,
    'UID_DOMAIN_i': 1,  # i, the initial index value
    'UID_USER_j': 1,  # j the initial index value
    # 'UID_USER': "domain-C{}\\user-c{}",  # domain$i\user$j
    'UID_USER': "domain-{}\\user-{}",  # domain-$i\user$j
    'UID_IP_OCTET_j': 0,  # j, the first index value in IP *.*.j.k
    'UID_IP_OCTET_k': 1,  # k, the first index value in IP *.*.j.k

    # list of UID discrete ranges of IP's
    #
    'UID_IP': [
        "1.1.0.1/16",
        "2.2.0.1/16",
        "3.3.0.1/16",
        "4.4.0.1/16",
        "5.5.0.1/16",
        "2006:6::1/116",
        "7.7.0.1/16",
        "8.8.0.1/16",
        ],
    'UID_PUSH': True,
    'UID_TIMEOUT': "600",  # timeout in mins. 600 means 600 minutes
})

# --------------------------------------------------------------------------------
