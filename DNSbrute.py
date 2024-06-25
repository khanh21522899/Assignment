#Import libary to perform DNS query
import dns.zone as dz
import dns.query as dq
import dns.resolver as dr
import argparse

#The defaut value for Asia if none of the record found in DNS server
APNIC = '125.235.4.59'

def get_args():
   #Retrieve user input as argument
   parser = argparse.ArgumentParser()
   parser.add_argument('-d', '--domain_name', dest='domain_name',default='', help="Domain name target of the query", required=True)
   parser.add_argument('-s', '--name_server', dest='name_server',default='8.8.8.8', help="Specify name server")
   parser.add_argument('-T', '--type', dest='type',default='A', help="Specify type of interact with DNS server")
   parser.add_argument('-w', '--subdomain', dest='subdomain', default='', help='Choosing subdomain wordlist, incase doing bruteforce')
   parser.add_argument('-o', '--output', dest='output',default='',help='Specify output file path')
   return parser.parse_args()


class DNSRetriever:
    #Init the attribute of the class contain everything we need to perform dns scan
    def __init__(self, domain_name , output, input_raw_ns, subdomainlist):
        self.domain_name = domain_name
        self.output = output
        self.resolver = dr.Resolver()
        self.resolver.nameservers = self.get_nameserver(input_raw_ns)
        self.subdomainlist = self.get_subdomainlist(subdomainlist)
        self.subdomain_rs = []
    
    def read_file (self, path):
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
                lines = [line.replace('\n','') for line in lines]
                return lines
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")
            return []

    def get_nameserver(self, input_raw_ns):
        result = []
        if('/' in input_raw_ns):
            paths = input_raw_ns.split(',')
            for path in paths:
                result.extend(self.read_file(path))
        else:
            result = input_raw_ns.split(',')

        return result
    
    def get_subdomainlist(self, raw_input):
        result = []
        if (raw_input == ''):
            return
        paths = raw_input.split(',')
        for path in paths:
            result.extend(self.read_file(path))

        return result
    
    def query (self,name, type):
        resolver = self.resolver
        try:
            # Perform the DNS query
            answers = resolver.resolve(name, type)

            # Print the results
            if(answers[0]==APNIC):
                print(f"Error: Domain name '{name}' does not exist.")
                return
            else:
                print(answers.rrset.to_text())
                if (self.output != ''):
                    self.write_output(answers.rrset.to_text()+'\n')
                return answers.rrset.to_text()
            
        except Exception as e:
            print(f"An error occurred: {e}")


    def write_output(self, content):
            try:
                with open(self.output, 'a') as file:
                    file.write(content)
            except Exception:
                print(Exception)
                return

    def AXFR (self):
        result =[]
        for nameserver in self.resolver.nameservers:

            try:
                axfr = dz.from_xfr(dq.xfr(nameserver, self.domain_name))

                if axfr:
                    print('[*] Successful Zone Transfer from {}'.format(nameserver))
                    for record in axfr.iterate_rdatasets():
                        result.append('{}.{}    {}'.format(record[0], self.domain_name, record[1]))
                        print('{}.{}    {}'.format(record[0], self.domain_name, record[1]))
                        if(self.output != ''):
                            self.write_output('{}.{}    {}\n'.format(record[0], self.domain_name, record[1]))

            except Exception as error:
                print(error)
                pass
    
    def brute (self):
        self.AXFR()
        self.query(self.domain_name, 'TXT')
        self.query(self.domain_name, 'MX')

        for subdomain in self.subdomainlist:
            name = '{}.{}'.format(subdomain, self.domain_name)
            self.query(name, 'A')
            self.query(name, 'AAAA')




if __name__ == "__main__":
    args = get_args()
    
    dns = DNSRetriever(domain_name=args.domain_name, output=args.output, input_raw_ns=args.name_server, subdomainlist=args.subdomain)

    if (args.type != 'brute'):
        if args.type == 'axfr':
           dns.AXFR()
        else:
           dns.query(args.domain_name,args.type)
    else:
        dns.brute()

       