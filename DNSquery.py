import dns.zone as dz
import dns.query as dq
import dns.resolver as dr
import dns.name as dn
import argparse




a = dn.from_text('www.google.com')

if __name__ == "__main__":
    print(a.to_text())