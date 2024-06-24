#!/usr/bin/env python3

# Dependencies:
# python3-dnspython

import dns.zone as dz
import dns.query as dq
import dns.resolver as dr
import argparse

#axfr = dz.from_xfr(dq.xfr(nameserver, domain))
#Init resolver class
NS = dr.Resolver()

Subdomains = []

#Define axfr function
def AXFR (domain, nameserver):
    try:
        #Perform zone transfer utilize zone transfer for given domain name and server
        axfr = dz.from_xfr(dq.xfr(nameserver, domain))

        #Sucessful
        if axfr:
            print('[*] Successful Zone Transfer from {}'.format(nameserver))
            #Add subdomain to domain list
            for dnsrecord in axfr:
                Subdomains.append('{}.{}'.format(dnsrecord.to_text(), domain))

    #Fail: print out something
    except Exception as error:
        print(error)
        pass


    
if __name__ == "__main__":

    #Argparser
    parser = argparse.ArgumentParser(prog="dnsenum.py", epilog="DNS enumeration", usage="./dnsenum.py [options] -d <Domain>", prefix_chars='-', add_help=True)
    
    #Argument
    parser.add_argument('-d', action='store', metavar='Domain', type=str, help='Target Domain.\tExample: inlanefreight.htb', required=True)
    parser.add_argument('-n', action='store', metavar='Nameserver', type=str, help='Nameservers separated by a comma.\tExample: ns1.inlanefreight.htb,ns2.inlanefreight.htb')
    parser.add_argument('-v', action='version', version='dnsenum - v0.1', help='Prints the version of dnsenum.py')
    
    # Assign given arguments
    args = parser.parse_args()

    #Variable
    Domain = args.d
    NS.nameservers = list(args.n.split(","))


    #Checking if URL is given
    if not args.d:
        print('[!] You must specify target Domain.\n')
        print(parser.print_help())
        exit()
    
    if not args.n:
        print('[!] You must specify target nameservers.\n')
        print(parser.print_help())
        exit()

    #for each given name server
    for nameserver in NS.nameservers:

        #perform axfr
        AXFR(Domain, nameserver)

    #print result
    if Subdomains is not None:

        
        print('------Found Subdomains:')
        #Print each subdomain
        for subdomain in Subdomains:
            print('{}'.format(subdomain))
    
    else:
        print('No subdomains found')
        exit()