import socket
import argparse

def get_args():
   #Retrieve user input as argument
   parser = argparse.ArgumentParser()
   parser.add_argument('-t', '--target', dest='target',default=[], nargs='+', help="The IP target", required=True)
   parser.add_argument('-p', '--port', dest='port',default='', help="Port you wanna scan can specify multiple port, example: -p 22 --> scan port 22; -p 22..36 --> scan port 22 to 36; -p 22,36 --> scan port 22 and 36; -p 12..22,25..33 --> scan port 12 to 22 and 25 to 33")
   parser.add_argument('-o', '--output', dest='output',default='',help='Specify output file path')
   parser.add_argument('-sV', action='store_true', dest='sV', default=False, help='Banner Grabbling')
   return parser.parse_args()

class PortScanner:
   def __init__(self, ip, port, banner_grabbling):
      self.ip = ip
      self.banner_grabbling = banner_grabbling
      self.port = port
      self.result=''
      
   def port_scan(self):
      
      port_range = self.detect_portrange()
      
      for i in self.ip:
         print('scanning: ' + i)
         
         for p in port_range:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
               conn = s.connect_ex((i, p))
               if(conn == 0) :
                  print ('Port %d: OPEN' % (p,))
                  self.result.join('Port %d: OPEN' % (p,) + '\n')
                  if(self.banner_grabbling == True):
                     print(self.tcp_banner(i,p))
                     self.result.join(self.tcp_banner(p)+ '\n')
               s.close()
            except:
               pass
      
   
   def tcp_banner(self,ip, port):
      try:
         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         s.settimeout(5)
         s.connect((ip, port))
         request = "GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"
         s.sendall(request.encode())
         response = s.recv(1024)
         result = str(response.decode())
         return result.split("\n")[0]
      except s.timeout:
         return
   


   def detect_portrange(self):
      #Specified the port range that user want the tool to scan
      port_range = []
      raw_input = self.port
      if raw_input == '':
         # If nothing was specified the tool will scan all port
         return list(range(1,65535+1))
      #If port range was specified by the comma it will seperate port sequence
      seqs = raw_input.split(',')
      for seq in seqs:
         #the .. mean from to
         if '..' in seq:
            try:
               start, end = map(int, seq.split(".."))
               if start > end:
                  raise ValueError(f"Start value ({start}) cannot be greater than end value ({end})")
               port_range.extend(list(range(start,end+1)))
            except ValueError as e:
               raise argparse.ArgumentError(None, f"Invalid range format: {range}.") from e
         else:
            port_range.append(int(seq))
      
      port_range = list(set(port_range))
      return port_range


      

if __name__ == "__main__":
   args = get_args()
    
   ps = PortScanner(args.target, args.port, args.sV)

   ps.port_scan()
