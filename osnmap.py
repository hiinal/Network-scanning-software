from scapy.all import ARP, Ether, srp
import socket
import nmap

def scan_network(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=10, verbose=True)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = "Unknown"
    return hostname

def port_scan(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-F') 
    ports_info = []

    for proto in nm[ip].all_protocols():
        lport = nm[ip][proto].keys()
        for port in lport:
            port_info = {
                'port': port,
                'protocol': proto,
                'state': nm[ip][proto][port]['state'],
                'service': nm[ip][proto][port]['name']
            }
            ports_info.append(port_info)

    return ports_info

def get_os_info(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-O') 
    os_info = nm[ip]['osmatch'] 
    return os_info

ip_range = "192.168.203.0/24"
devices = scan_network(ip_range)

for device in devices:
    device['hostname'] = get_hostname(device['ip'])
    device['ports'] = port_scan(device['ip'])
    device['os_info'] = get_os_info(device['ip'])
    print(device)
    print()

