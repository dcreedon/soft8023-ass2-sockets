import socket

#SERVER = "127.0.0.1"
SERVER = "localhost"
PORT = 64002

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client", 'UTF-8'))
print("enter 'bye'added to leave or 'stats' to get the latest stats from the game server")

while True:
    in_data = client.recv(1024)

    out_data = input()
    client.sendall(bytes(out_data, 'UTF-8'))

    if out_data == 'bye':
        print("Disconnected from server :", in_data.decode())
        break
    else:
        print("From Server :", in_data.decode())

client.close()