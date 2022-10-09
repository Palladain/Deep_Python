import telnetlib #библиотека для подключений

print("connecting...")
tn = telnetlib.Telnet("www.python.org", '80')
msg = "GET / HTTP/1.1\nHost:www.python.org\n\n".encode('ascii')
tn.write(msg)
print(tn.read_until(b"\r"))
print("response received")
tn.close()
