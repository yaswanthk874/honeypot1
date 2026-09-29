import socket
import threading
import time
from database import SessionLocal
from models import AttackLog
from profiling_engine import profile_attacker

class FakeService:
    def __init__(self, port, name, banner=None, response_logic=None):
        self.port = port
        self.name = name
        self.banner = banner
        self.response_logic = response_logic
        self.running = False
        self.server_socket = None

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(5)
            print(f"[*] Honeypot Service '{self.name}' listening on port {self.port}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, addr = self.server_socket.accept()
                    threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection on port {self.port}: {e}")
        except PermissionError:
             print(f"[!] Permission denied to bind port {self.port}. Try running as Administrator/Root or use higher ports.")
             self.running = False
        finally:
            if self.server_socket:
                self.server_socket.close()

    def stop(self):
        self.running = False

    def handle_client(self, client_socket, addr):
        ip = addr[0]
        print(f"[{self.name}] Connection from {ip}")
        payload_data = b""
        
        try:
            client_socket.settimeout(5.0)
            if self.banner:
                client_socket.send(self.banner.encode())
            
            if self.response_logic:
                payload_data = self.response_logic(client_socket)
            else:
                # Default receive
                payload_data = client_socket.recv(1024)
                
        except Exception as e:
            pass # Client disconnected or timeout
        finally:
            client_socket.close()
            self.log_attack(ip, payload_data.decode(errors='ignore'))

    def log_attack(self, ip, payload):
        db = SessionLocal()
        try:
            # First, classify the attacker
            profile = profile_attacker(db, ip, self.port, payload)
            
            log = AttackLog(
                source_ip=ip,
                targeted_port=self.port,
                service_mimicked=self.name,
                payload=payload,
                attacker_profile=profile.classification if profile else "unknown"
            )
            db.add(log)
            db.commit()
            print(f"[*] Logged attack from {ip} on {self.name}")
        except Exception as e:
            print(f"Error logging attack: {e}")
        finally:
            db.close()


def http_response_logic(client_socket):
    request = client_socket.recv(1024)
    response = "HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\nContent-Type: text/html\r\n\r\n<html><body><h1>It works!</h1></body></html>\r\n"
    client_socket.send(response.encode())
    return request

def ssh_response_logic(client_socket):
    # Banner already sent
    client_socket.send(b"Password: ")
    password_attempt = client_socket.recv(1024)
    client_socket.send(b"Access denied\r\n")
    return password_attempt

def mysql_response_logic(client_socket):
    # Fake MySQL greeting (highly simplified)
    greeting = b"J\x00\x00\x00\x0a8.0.25\x00\x01\x00\x00\x00"
    client_socket.send(greeting)
    req = client_socket.recv(1024)
    return req

# Map real ports to safe local testing ports if not running as root
# Example: map 80 to 8080
SERVICES = [
    FakeService(port=8080, name="HTTP", response_logic=http_response_logic),
    FakeService(port=2222, name="SSH", banner="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n", response_logic=ssh_response_logic),
    FakeService(port=33060, name="MySQL", response_logic=mysql_response_logic)
]

def start_all_services():
    threads = []
    for service in SERVICES:
        t = threading.Thread(target=service.start)
        t.daemon = True
        t.start()
        threads.append(t)
    return threads
