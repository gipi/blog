---
layout: post
comments: true
title: "Setup a lab for malware experimentation"
tags: [malware, virtualbox]
---

https://github.com/fireeye/flare-vm

https://oalabs.openanalysis.net/2018/07/16/oalabs_malware_analysis_virtual_machine/

https://www.malwaretech.com/2017/11/creating-a-simple-free-malware-analysis-environment.html
https://www.malwaretech.com/2015/08/creating-ultimate-tor-virtual-network.html

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
