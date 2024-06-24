import socket
import time
import threading
import queue
import argparse

def get_args():
   #Retrieve user input as argument
   parser = argparse.ArgumentParser()
   parser.add_argument('-t', '--target', dest='target',default=[], nargs='+', help="The IP target", required=True)
   parser.add_argument('-p', '--port', dest='port',default='', help="Port you wanna scan can specify multiple port, example: -p 22 --> scan port 22; -p 22..36 --> scan port 22 to 36; -p 22,36 --> scan port 22 and 36; -p 12..22,25..33 --> scan port 12 to 22 and 25 to 33")
   parser.add_argument('-o', '--output', dest='output',default='',help='Specify output file path')
   return parser.parse_args()

class PortScanner:
   def __init__(self, ip, port):
      self.ip = ip
      self.port = port
      self.result={}
      
   def port_scan(self):
      
      port_range = self.detect_portrange()
      result = {}
      for i in self.ip:
         print('scanning: ' + i)
         temp =[]
         for p in port_range:
            socket.setdefaulttimeout(5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
               conn = s.connect_ex((i, p))
               if(conn == 0) :
                  print ('Port %d: OPEN' % (p,))
                  temp.append(p)
               s.close()
            except:
               pass
         result[i]=temp
      self.result = result
   
   
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
    
   ps = PortScanner(args.target, args.port)

   ps.port_scan()
