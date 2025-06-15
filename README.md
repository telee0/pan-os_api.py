# pan-os_api.py

Scripts rewritten in Python to generate PAN XML config and apply it through REST API

```
python3 pan.py -c conf/pa.py -h 192.168.1.1 -u admin -v
```

Supported config as follows.

* Device > Local users
* Network > Interfaces > Ethernet   (with vsys, zone and vr assignment)
* Network > Interfaces > Loopback   (with vsys, zone and vr assignment)
* Network > Interfaces > Tunnel     (with vsys, zone and vr assignment)
* Network > Zones
* Network > DNS Proxy
* Network > IKE Gateways
* Network > IPSec Tunnels (with static routes through tunnels)
* Objects > Addresses
* Objects > Address Groups
* Objects > Services
* Objects > Service Groups
* Objects > Custom URL Category with url.txt
* Policies > Security
* Policies > NAT
* Policies > PBF
* Network > VR > Static Routes
* Network > VR > BGP peer groups x peers

* User-ID mapping

(Panorama only)
* Panorama > Device Groups
* Panorama > Templates

---
