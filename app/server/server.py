import socket
import threading
import pika
import json

#LOCALHOST = "127.0.0.1"
LOCALHOST = "0.0.0.0"           # to allow docker to bind to external port
PORT = 64002

RABBITHOST = 'host.docker.internal'     # to allow docker to communicate with local rabbit mq installation
#RABBITHOST = "127.0.0.1"

# Message Queue Setup
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITHOST))
channel = connection.channel()
queue_name = 'mid-game-stats'
channel.queue_declare(queue=queue_name)

game_stats= {}  # dictionary to hold game stats, keyed on unique game id

class RabbitThread(threading.Thread):

    def __init__(self, channel):
        threading.Thread.__init__(self)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def run(self):
        channel.start_consuming()

class ClientThread(threading.Thread):

    def __init__(self, client_address, client_socket, identity):
        threading.Thread.__init__(self)
        self.c_socket = client_socket
        print("Connection no. " + str(identity))
        print("New connection added: ", client_address)

    def run(self):

        while True:
            data = self.c_socket.recv(2048)
            msg = data.decode()
            print("From client: ", msg)
            if msg == 'bye':
                print("Bye..Client Disconnecting")
                break
            elif msg == 'stats':
                print("Client requested stats")
                self.c_socket.send(bytes(json.dumps(game_stats), 'UTF-8'))

            self.c_socket.send(bytes(msg, 'UTF-8'))
        print("Client disconnected...")

def callback(ch, method, properties, body):
    temp_stats = body.decode("utf-8")
    print(temp_stats)
    temp_dict = json.loads(body.decode("utf-8"))
    game_stats.update(temp_dict)


def serve():

    # Socket Server Setup
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")

    # Start consuming messages from RabbbitMQ queue

    queue_thread = RabbitThread(channel)
    queue_thread.start()

    counter = 0

    while True:
        server.listen(1)
        my_socket, clientAddress = server.accept()
        counter = counter + 1
        new_thread = ClientThread(clientAddress, my_socket, counter)
        new_thread.start()


if __name__ == '__main__':
    print("Launching Socket Server...")
    serve()