"""
This module is responsible for registering the _kickbot._tcp.local. service on the local network using Zeroconf (mDNS) 
so that other devices can discover it.
"""

from time import sleep
import socket
from zeroconf import IPVersion, ServiceInfo, Zeroconf



def register_zeroconf(zc:Zeroconf) -> ServiceInfo:
    
    hostname = socket.gethostname()
    addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)

    packed_addresses = []
    string_addresses = []

    for item in addr_info:
        family = item[0]          # socket.AF_INET or socket.AF_INET6
        ip_string = item[4][0]    # The raw IP string ("192.168.1.5" or "fe80::...")
        
        # Filter out duplicate network loops if necessary
        if ip_string in string_addresses:
            continue
        string_addresses.append(ip_string)
        
        # 2. Match the exact address family with inet_pton dynamically
        packed_ip = socket.inet_pton(family, ip_string)
        packed_addresses.append(packed_ip)
    
    info = ServiceInfo(
        "_kickbot._tcp.local.",
        f"{hostname}._kickbot._tcp.local.",
        addresses=packed_addresses,
        port=5000,
        properties={},
        server="kickbot.local.",
    )
    
    zc.register_service(info)
    print("Registering service...")
    
    return info


def main():
    
    #Want to be IPV6 compatible, but also support IPV4 for now.  This is a bit of a hack, but it works.
    zc = Zeroconf(ip_version=IPVersion.All)
    
    info = register_zeroconf(zc)
    
    try:
        while True:
            sleep(0.1)  # Keep the program running to maintain the service registration, replace with 
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down Zeroconf service...")
        zc.unregister_service(info)
        zc.close()
    

if __name__ == "__main__":
    main()