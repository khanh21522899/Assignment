import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("192.168.2.205", 3306))
s.settimeout(10)

request = "GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"

s.sendall(request.encode())

response = s.recv(1024)  # Adjust buffer size as needed

text = str(response.decode())
print(text.split("<!DOCTYPE")[0])
