
import argparse
from scapy.all import srp, Ether, ARP, sr, IP, ICMP, TCP, UDP
import time

def get_args():
    #Take user input as argument
    #The type determine which kind of scan user choose to do,
    #Some network filter out ICMP for security purpose so user can choose to do ARP scan or UDP, TCP
    #since these kind of scan will take more time to run
    parser = argparse.ArgumentParser()
    parser.add_argument('-T', '--type', dest='type', default='icmp', help='Specify Scan type: -t arp for arp scan, -t icmp for icmp, -t tcp for tcp ping, -t udp for udp ping')
    parser.add_argument('-n', '--network', dest='network',default='192.168.1.0/24', help="Specify the network, template 192.168.1.0/24", required=True)
    parser.add_argument('-t', '--timeout', dest='timeout', default=10, help='Specify the timeout after the last packet was send, set it longer for tcp and udp scan', required=True)
    parser.add_argument('-o', '--output', dest='output',default='',help='Specify output file path')
    return parser.parse_args()



class PingSweeper:
    def __init__(self, network, output, timeout):
        self.network = network
        self.output = output
        self.timeout = int(timeout)

    
    def arp_scan(self):
        #Ping with ARP incase the ICMP was filtered out
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=self.network), timeout=self.timeout)

        for res in ans.res: 
            
                content = res.answer.src + ' ' + res.answer.payload.psrc
                print(content)
                if(self.output != ''):
                    self.write_output(content + '\n')
        
                

    def tcp_scan(self):
        #Ping with TCP with a random port
        ans, unans = sr( IP(dst=self.network)/TCP(dport=80,flags="S"), chainCC=True, timeout=self.timeout )

        for res in ans.res: 
            
                content = res.answer.src + ' is alive and reachable'
                print(content)
                if(self.output != ''):
                    self.write_output(res.answer.src + '\n')
    
    def udp_scan(self):
        #Ping with UDP
        ans, unans = sr( IP(dst=self.network)/UDP(dport=0), timeout=self.timeout, chainCC=True )

        for res in ans.res: 
            
                content = res.answer.src + ' is alive and reachable'
                print(content)
                if(self.output != ''):
                    self.write_output(res.answer.src + '\n')
    
    def icmp_scan(self):
        #Ping with ICMP as normal
        ans, unans = sr(IP(dst=self.network)/ICMP(), timeout=self.timeout, chainCC=True)

        for res in ans.res: 
            
                content = res.answer.src + ' is alive and reachable'
                print(content)
                if(self.output != ''):
                    self.write_output(res.answer.src + '\n')

    def write_output(self, content):
            with open(self.output, 'a') as file:
                file.write(content)
        


        

if __name__ == "__main__":
    args = get_args()

    ps = PingSweeper(args.network, args.output, args.timeout)
    start_time = time.time()
    print("The scan start: ")

    match args.type:
        case 'arp':
            ps.arp_scan()
        case 'tcp':
            ps.tcp_scan()
        case 'udp':
            ps.udp_scan()
        case default:
            ps.icmp_scan()

    end_time = time.time()
    duration = end_time - start_time
    print("Scan end, it take " + str(duration) + " for the scan to run")

    
    
    