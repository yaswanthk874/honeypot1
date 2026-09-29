from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import init_db, get_db
from models import AttackLog, AttackerProfile
from services import SERVICES
import threading
import time

app = FastAPI(title="AI-Enhanced Honeypot API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start Honeypot Services in the background
def run_services():
    for service in SERVICES:
        t = threading.Thread(target=service.start)
        t.daemon = True
        t.start()
        
@app.on_event("startup")
def on_startup():
    init_db()
    
    # Start honey services asynchronously
    run_services()
    print("[+] All Honeypot simulated services started.")


@app.get("/")
def read_root():
    return {"status": "Honeypot Core Running"}

@app.get("/api/logs")
def get_attack_logs(db: Session = Depends(get_db), limit: int = 50):
    db.expire_all() # Force refresh from DB
    logs = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).limit(limit).all()
    # Serialize manually for simplicity since we aren't using Pydantic schemas yet
    return [
       {
           "id": l.id,
           "timestamp": l.timestamp.isoformat(),
           "source_ip": l.source_ip,
           "targeted_port": l.targeted_port,
           "service_mimicked": l.service_mimicked,
           "payload": l.payload[:100] + "..." if l.payload and len(l.payload) > 100 else l.payload,
           "attacker_profile": l.attacker_profile
       } for l in logs
    ]

@app.get("/api/profiles")
def get_attacker_profiles(db: Session = Depends(get_db)):
    db.expire_all() # Force refresh from DB
    profiles = db.query(AttackerProfile).order_by(AttackerProfile.last_seen.desc()).all()
    return [
        {
           "id": p.id,
           "ip_address": p.ip_address,
           "first_seen": p.first_seen.isoformat(),
           "last_seen": p.last_seen.isoformat(),
           "total_attacks": p.total_attacks,
           "classification": p.classification,
           "frequent_ports": p.frequent_ports
        } for p in profiles
    ]
