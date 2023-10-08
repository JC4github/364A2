import select
import socket
import sys
import signal
import argparse
import ssl
import warnings

from utils import *
from auth_provider import *

SERVER_HOST = 'localhost'

class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # list output sockets

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
        self.context.load_verify_locations('cert.pem')
        self.context.set_ciphers('AES256-SHA')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)                
        self.server = self.context.wrap_socket(self.server, server_side=True)

        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.close)

        print(f'Server listening to port: {port} ...')

    def close(self, signum, frame):
        """ Clean up client outputs"""
        print('\nShutting down server...\n')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        name = info[1]
        return name

    def run(self):
        # inputs = [self.server, sys.stdin]
        inputs = [self.server]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, [])
            except select.error as e:
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()

                    print(
                        f'Chat server: got connection {client.fileno()} from {address}')
                    
                    cname = ''
                    password = ''
                    actionType = ''
                    success = False

                    data = receive(client)
                    components = data.split('\n')

                    if len(components) == 3:
                        cname = components[0].split('NAME: ')[1]
                        password = components[2].split('PASSWORD: ')[1]
                        actionType = components[1].split('ACTION: ')[1]
                    else:
                        print('\nInvalid data received from client\n')
                        # remove client from inputs list
                        inputs.remove(client)

                        # info client of invalid data
                        send(client, 'INVALID_DATA')

                    if actionType == '1':
                        # client login
                        if validate_client(cname, password):
                            success = True
                            response_msg = 'LOGIN_SUCCESS'
                        else:
                            response_msg = 'LOGIN_FAILED'
                    elif actionType == '2':
                        # client register
                        if register_client(cname, password):
                            success = True
                            response_msg = 'REGISTER_SUCCESS'
                        else:
                            response_msg = 'REGISTER_FAILED'
                    else:
                        # client action not supported
                        print('\nInvalid action received from client\n')
                    
                    if success:
                        # Compute client name and send back
                        self.clients += 1
                        send(client, f'CLIENT: {str(address[0])}\n{response_msg}')
                        inputs.append(client)

                        self.clientmap[client] = (address, cname)
                        # Send joining information to other clients
                        msg = f'\n({self.get_client_name(client)} has joined the chat room! ({self.clients}))'
                        for output in self.outputs:
                            send(output, msg)
                        self.outputs.append(client)
                    else:
                        send(client, response_msg)
                        client.close()

                # elif sock == sys.stdin:
                #     # didn't test sys.stdin on windows system
                #     # handle standard input
                #     cmd = sys.stdin.readline().strip()
                #     if cmd == 'list':
                #         print(self.clientmap.values())
                #     elif cmd == 'quit':
                #         running = False
                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            # Send as new client's message...
                            msg = f'\n[{self.get_client_name(sock)}]>> {data}'

                            # Send data to all except ourself
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            # Sending client leaving information to others
                            msg = f'\n({self.get_client_name(sock)} has left the chat room. ({self.clients}))'

                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        # Remove
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        
        self.server.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Socket Server Example with Select')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name

    server = ChatServer(port)
    server.run()
