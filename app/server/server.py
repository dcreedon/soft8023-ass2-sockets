import socket
import threading
import pika

#LOCALHOST = "127.0.0.1"
LOCALHOST = "0.0.0.0"           # to allow docker to bind to external port
PORT = 64002

RABBITHOST = "rabbitmq"

class ClientThread(threading.Thread):

    def __init__(self, client_address, client_socket, identity):
        threading.Thread.__init__(self)
        self.c_socket = client_socket
        print("Connection no. " + str(identity))
        print("New connection added: ", client_address)

    def callback(self, ch, method, properties, body):
        print(" [x] %r" % body)
        self.c_socket.send(bytes(str(body), 'UTF-8'))

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
                # Message Queue Setup
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITHOST))
                channel = connection.channel()
                queue_name = 'mid-game-stats'
                channel.queue_declare(queue=queue_name)
                channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
                channel.start_consuming()

            self.c_socket.send(bytes(msg, 'UTF-8'))
        print("Client disconnected...")


def serve():

    # Socket Server Setup
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("Server started")
    print("Waiting for client request..")

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