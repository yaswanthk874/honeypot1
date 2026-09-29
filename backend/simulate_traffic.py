import random
import time
from datetime import datetime, timedelta
from database import SessionLocal
from models import AttackLog, AttackerProfile
from profiling_engine import profile_attacker

def generate_random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def generate_mock_traffic(num_attacks=50):
    db = SessionLocal()
    print(f"[*] Generating {num_attacks} simulated attacks from random global IPs...")
    
    ports_services = [
        (8080, "HTTP"),
        (2222, "SSH"),
        (33060, "MySQL")
    ]
    
    # Generate some persistent botnet IPs
    botnet_ips = [generate_random_ip() for _ in range(3)]
    advanced_ips = [generate_random_ip() for _ in range(2)]
    
    payloads = {
        "botnet": ["GET / HTTP/1.1\\r\\nUser-Agent: mass_scan", "GET / HTTP/1.1\\r\\nUser-Agent: mirai", "CONNECT ssh"],
        "advanced hacker": ["GET /?id=1' OR 1=1-- HTTP/1.1", "POST /login (admin / ' OR '1'='1)", "DROP TABLE users;"],
        "script kiddie": ["GET /wp-admin.php HTTP/1.1", "GET /phpmyadmin/ HTTP/1.1", "SSH pwd '123456'"]
    }
    
    try:
        for i in range(num_attacks):
            # Decide attacker type
            attacker_type = random.choices(
                ["random", "botnet", "advanced hacker"], 
                weights=[0.6, 0.3, 0.1]
            )[0]
            
            if attacker_type == "botnet":
                ip = random.choice(botnet_ips)
                payload = random.choice(payloads["botnet"])
            elif attacker_type == "advanced hacker":
                ip = random.choice(advanced_ips)
                payload = random.choice(payloads["advanced hacker"])
            else:
                ip = generate_random_ip()
                payload = random.choice(payloads["script kiddie"])
                
            port, service = random.choice(ports_services)
            
            # Profile the attacker
            profile = profile_attacker(db, ip, port, payload)
            
            # Log the attack with a slightly randomized timestamp in the past
            past_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 120))
            
            log = AttackLog(
                timestamp=past_time,
                source_ip=ip,
                targeted_port=port,
                service_mimicked=service,
                payload=payload,
                attacker_profile=profile.classification if profile else "unknown"
            )
            db.add(log)
            print(f"  -> Injected attack from {ip} on port {port}")
            
        db.commit()
        print("[+] Finished injecting simulated traffic. Check your React dashboard!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_mock_traffic(50)
