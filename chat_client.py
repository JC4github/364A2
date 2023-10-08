import select
import socket
import sys
import argparse
import threading
import ssl
import warnings

from utils import *
from auth_provider import *

SERVER_HOST = 'localhost'

stop_thread = False


def get_and_send(client):
    while not stop_thread:
        # data = sys.stdin.readline().strip()
        data = input(client.prompt)
        if data:
            send(client.sock, data)


class ChatClient():
    """ A command line chat client using select """

    def __init__(self, name, port, actionType, password, host=SERVER_HOST):
        self.name = name
        self.actionType = actionType
        self.password = password
        self.connected = False
        self.host = host
        self.port = port

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.set_ciphers('AES256-SHA')

        # Initial prompt
        self.prompt = f'[{name}@{socket.gethostname()}]>> '

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = self.context.wrap_socket(
                self.sock, server_hostname=host)

            self.sock.connect((host, self.port))
            print(f'\nEstablishing connection to server @ port {self.port}\n')
            self.connected = True

            # Send username, password and action to server
            message = f'NAME: {self.name}\nACTION: {str(self.actionType)}\nPASSWORD: {self.password}'
            send(self.sock, message)

            data = receive(self.sock)
            
            # process the data from server
            if 'INVALID_DATA' in data:
                print('Invalid input data, please try again.')
                sys.exit(1)

            elif 'LOGIN_FAILED' in data:
                print('Invalid username or password, please try again.')
                sys.exit(1)

            elif 'REGISTER_FAILED' in data:
                print('Username already exists, please try again.')
                sys.exit(1)

            elif 'LOGIN_SUCCESS' in data:
                print('Login successful.')
                components = data.split('\n')
                addr = components[0].split('CLIENT: ')[1]
                self.prompt = f'[{self.name}]>> '
                threading.Thread(target=get_and_send, args=(self,)).start()

            elif 'REGISTER_SUCCESS' in data:
                print('Registration successful.')
                components = data.split('\n')
                addr = components[0].split('CLIENT: ')[1]
                self.prompt = f'[{self.name}]>> '
                threading.Thread(target=get_and_send, args=(self,)).start()

        except socket.error as e:
            print(f'Failed to connect to chat server @ port {self.port}')
            sys.exit(1)

    def cleanup(self):
        """Close the connection and wait for the thread to terminate."""
        self.sock.close()

    def run(self):
        skip = True
        """ Chat client main loop """
        try:
            while self.connected:
                # skip first time to avoid double printing prompt
                if not skip:
                    sys.stdout.write(self.prompt)
                sys.stdout.flush()
                skip = False

                # Wait for input from stdin and socket
                # readable, writeable, exceptional = select.select([0, self.sock], [], [])
                readable, writeable, exceptional = select.select(
                    [self.sock], [], [])

                for sock in readable:
                    # if sock == 0:
                    #     data = sys.stdin.readline().strip()
                    #     if data:
                    #         send(self.sock, data)
                    if sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print('Client shutting down.')
                            self.connected = False
                            break
                        else:
                            print(data)
                            sys.stdout.flush()

        except KeyboardInterrupt:
                stop_thread = True
                self.cleanup()
                print('\nClient interrupted. Exiting...')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store",
                        dest="port", type=int, required=True)
    given_args = parser.parse_args()

    port = given_args.port
    # name = given_args.name

    # Enter 1 to login and 2 to register
    correct_input = False
    username = ''
    password = ''
    actionType = 0
    while not correct_input:
        choice = input('1. Login\n2. Register\nEnter your choice: ')
        if choice == '1':
            # Login
            correct_input = True
            username, password = client_login()
            actionType = 1
        elif choice == '2':
            # Register
            correct_input = True
            username, password = client_register()
            actionType = 2
        else:
            print('\nInvalid choice, try again.\n')

    client = ChatClient(name=username, port=port, actionType=actionType, password=password)
    client.run()
