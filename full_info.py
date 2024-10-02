
import socket
import threading
import json

IP = '192.168.0.112'
PORT = 8080
ADDR = (IP, PORT)
FORMAT = 'utf-8'
SIZE = 8192

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:

        file_name = conn.recv(SIZE).decode(FORMAT)
        print(f"[{addr}] File name received: {file_name}")

        json_size = int(conn.recv(SIZE).decode(FORMAT))
        print(f"[{addr}] JSON data size: {json_size}")

        conn.send("OK".encode(FORMAT))

        json_data = b""
        received_bytes = 0
        while received_bytes < json_size:
            chunk = conn.recv(min(SIZE, json_size - received_bytes))
            if not chunk:
                break
            json_data += chunk
            received_bytes += len(chunk)

        print(f"[{addr}] JSON data received.")

        try:
            data = json.loads(json_data)
            #print("Received JSON data:", data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return

        with open(file_name, 'w') as file:
            json.dump(data, file)
            print(f"[{addr}] JSON data saved to file: {file_name}")

        response = "Data received and saved successfully."
        conn.send(response.encode(FORMAT))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        print(f"[{addr}] Closing connection.")
        conn.close()

def main():
    print("[STARTING] IP is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on [{IP}:{PORT}]")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if  __name__ == "__main__":
    main()




