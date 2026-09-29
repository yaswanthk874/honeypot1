from sqlalchemy.orm import Session
from models import AttackerProfile
from datetime import datetime

class Profiler:
    # Extremely basic heuristic rules
    BOTNET_PAYLOADS = ["mass_scan", "mirai", "nessus", "nmap"]
    ADVANCED_PAYLOADS = ["' OR 1=1", "DROP TABLE", "/etc/passwd", "<script>"]
    
    @staticmethod
    def classify(total_attacks, ports_hit, payload):
        payload_lower = payload.lower()
        
        # Check for advanced SQL/LFI/XSS payloads
        for sig in Profiler.ADVANCED_PAYLOADS:
            if sig in payload_lower:
                return "advanced hacker"
                
        # Check for known scanner/botnet signatures
        for sig in Profiler.BOTNET_PAYLOADS:
            if sig in payload_lower:
                return "botnet"
                
        # High volume of attacks = likely automated scanner/botnet
        if total_attacks > 20:
             return "botnet"
             
        # Low volume, simple payloads = script kiddie or curious
        if total_attacks > 5:
            return "script kiddie"
            
        return "suspicious"

def profile_attacker(db: Session, ip: str, port: int, payload: str) -> AttackerProfile:
    profile = db.query(AttackerProfile).filter(AttackerProfile.ip_address == ip).first()
    
    if not profile:
        profile = AttackerProfile(
            ip_address=ip,
            first_seen=datetime.utcnow(),
            total_attacks=1,
            frequent_ports=str(port)
        )
        db.add(profile)
    else:
        profile.total_attacks += 1
        profile.last_seen = datetime.utcnow()
        ports = set(profile.frequent_ports.split(',')) if profile.frequent_ports else set()
        ports.add(str(port))
        profile.frequent_ports = ",".join(ports)
        
    profile.classification = Profiler.classify(profile.total_attacks, profile.frequent_ports, payload)
    
    db.commit()
    db.refresh(profile)
    return profile
