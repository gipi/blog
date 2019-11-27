---
layout: post
comments: true
title: "Setup a lab for malware experimentation"
tags: [malware, virtualbox]
---

The setup is

 - two virtual machines (virtualbox)
   - gateway with linux where to route all the traffic with ``inetsim`` to simulate all the services
   - victim machine with Windows OS where to launch the malware
 - a closed network between the machines with static ips
 - a shared folder between the physical machine and the gateway

To share file from the gateway machine to the victime one set an entry with ``inetsim`` so to
obtain a file when requested like

```
http_fakefile   kebab   malware x-msdos-program
```

**Note:** in the gateway machine remove all the possible programs that could use the
port you need (like ``dnsmasq`` or ``apache``).

## Samples

It seems interesting the [Zoo](https://github.com/ytisf/theZoo) repository, that contains
a searchable database of malwares.

## Route all traffics through TOR

Pratically the instruction are taken from [here](https://www.howtoforge.com/how-to-set-up-a-tor-middlebox-routing-all-virtualbox-virtual-machine-traffic-over-the-tor-network)

```
# apt-get install bridge-utils dnsmasq
```

``/etc/network/interfaces``

```
# VirtualBox NAT bridge
auto vnet0
iface vnet0 inet static
 address 172.16.0.1
 netmask 255.255.255.0
 bridge_ports none
 bridge_maxwait 0
 bridge_fd 1
 
 up iptables -t nat -I POSTROUTING -s 172.16.0.0/24 -j MASQUERADE
 down iptables -t nat -D POSTROUTING -s 172.16.0.0/24 -j MASQUERADE
```

``/etc/dnsmasq.conf``

```
interface=vnet0
dhcp-range=172.16.0.2,172.16.0.254,1h
```

## Example

f1bae35d296930d2076b9d84ba0c95ea

call ``VirtualAlloc`` that returns address ``0x1c0000``, then loads at runtime
some functions and in particular it calls ``CreateThread()`` pointing inside
the allocated memory indicated before.

## Links

 - https://github.com/rshipp/awesome-malware-analysis
 - https://github.com/fireeye/flare-vm
 - https://oalabs.openanalysis.net/2018/07/16/oalabs_malware_analysis_virtual_machine/
 - https://www.malwaretech.com/2017/11/creating-a-simple-free-malware-analysis-environment.html
 - https://www.malwaretech.com/2015/08/creating-ultimate-tor-virtual-network.html
 - https://blog.christophetd.fr/malware-analysis-lab-with-virtualbox-inetsim-and-burp/
 - https://handlers.sans.org/tliston/ThwartingVMDetection_Liston_Skoudis.pdf

