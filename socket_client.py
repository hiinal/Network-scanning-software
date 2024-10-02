import socket
import json
from full_info import SystemInformation
import ctypes
import sys

IP = "192.168.0.112"
PORT = 8080
FORMAT = "utf-8"
ADDR = (IP, PORT)
SIZE = 8192

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return False

def main():
    try:    
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        
        if not run_as_admin():
            return  # Exit if elevation failed
        
        info = SystemInformation()
        combined_info, file_name = info.get_combined_info()
        
        client.send(file_name.encode(FORMAT))
        print("[CLIENT] file name sent to the server.")    
        
        json_data = json.dumps(combined_info)
        data_size = len(json_data)
        client.send(str(data_size).encode(FORMAT)) 
        client.recv(SIZE)  
        
        sent_bytes = 0
        while sent_bytes < data_size:
            chunk = json_data[sent_bytes:sent_bytes+SIZE]
            client.send(chunk.encode(FORMAT))
            sent_bytes += len(chunk)

        print("[CLIENT] Sent system information to the server.")
        
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")
        
        client.close()
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()   
