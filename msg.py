import socket
import threading
import time
import re

HOST = '0.0.0.0'
PORT = 55555

clients = []


def handle_client(client_socket, addr):
    try:
        clients.append(client_socket)

        client_address = f"{addr[0]}:{addr[1]}"
        print(
            f"Client {client_address} connected. Total clients: {len(clients)}")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            timestamp = time.strftime("%H:%M:%S")

            content = parse_message(data.decode('utf-8'))
            if content:
                message = f"[{timestamp}] {client_address}: {content}\n"
                print(message)
                broadcast(message)

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        clients.remove(client_socket)
        print(
            f"Client {client_address} disconnected. Total clients: {len(clients)}")
        client_socket.close()


def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")
            clients.remove(client)


def parse_message(command):
    pattern = re.compile(r'^MSG: (.+)$', re.IGNORECASE)
    match = pattern.match(command)
    if match:
        content = match.group(1)
        return content
    else:
        return None


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, addr))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
