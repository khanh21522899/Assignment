from scapy.all import srp, Ether, ARP

ether = Ether(dst="ff:ff:ff:ff:ff:ff")

arp = ARP(pdst="192.168.1.0/24")


ans, unans = srp(ether/arp, timeout=1)

ans.res[0].answer.json
