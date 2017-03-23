# -*- coding:utf-8 -*-
import socket
host = "192.168.2.70"
port = 8765
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

#with open('app/pokemon.txt', 'r') as f:
#    while True:
#        name = f.readline()
#        if not name:
#            client.close()
#            break
#        client.send("{}".format(name.rstrip()).encode("utf8"))
#        response = client.recv(4096)
#        print(response.decode("utf8"))
#client.close()


#
#    for line in f:
#        name = line.rstrip()
#        client.send("{}".format(name).encode("utf8"))
#        response = client.recv(4096)
#        print(response.decode("utf8"))
#    client.close()

for i in range(0, 10000):
    client.send("{}".format(i).encode("utf8"))
    response = client.recv(4096)
    print(response)

client.close()
