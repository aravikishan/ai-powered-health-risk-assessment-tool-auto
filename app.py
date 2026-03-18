from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI()

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = "sqlite:///./health_assessment.db"

def init_db():
    conn = sqlite3.connect('health_assessment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserProfile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            lifestyle TEXT NOT NULL,
            family_history TEXT NOT NULL,
            health_metrics TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HealthAssessment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            risk_score REAL NOT NULL,
            recommendations TEXT NOT NULL,
            FOREIGN KEY(profile_id) REFERENCES UserProfile(id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Data models
class UserProfile(BaseModel):
    id: int
    age: int
    lifestyle: str
    family_history: str
    health_metrics: Dict[str, float]

class HealthAssessment(BaseModel):
    id: int
    profile_id: int
    risk_score: float
    recommendations: List[str]

# Seed data
seed_profiles = [
    UserProfile(id=1, age=30, lifestyle="active", family_history="none", health_metrics={"bmi": 22.5, "blood_pressure": 120}),
    UserProfile(id=2, age=45, lifestyle="sedentary", family_history="heart disease", health_metrics={"bmi": 28.0, "blood_pressure": 140})
]

seed_assessments = [
    HealthAssessment(id=1, profile_id=1, risk_score=0.1, recommendations=["Maintain current lifestyle", "Regular check-ups"]),
    HealthAssessment(id=2, profile_id=2, risk_score=0.7, recommendations=["Increase physical activity", "Monitor blood pressure"])
]

# Insert seed data into database
conn = sqlite3.connect('health_assessment.db')
cursor = conn.cursor()
for profile in seed_profiles:
    cursor.execute('''
        INSERT OR IGNORE INTO UserProfile (id, age, lifestyle, family_history, health_metrics)
        VALUES (?, ?, ?, ?, ?)
    ''', (profile.id, profile.age, profile.lifestyle, profile.family_history, str(profile.health_metrics)))

for assessment in seed_assessments:
    cursor.execute('''
        INSERT OR IGNORE INTO HealthAssessment (id, profile_id, risk_score, recommendations)
        VALUES (?, ?, ?, ?)
    ''', (assessment.id, assessment.profile_id, assessment.risk_score, str(assessment.recommendations)))

conn.commit()
conn.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/profile", response_class=HTMLResponse)
async def read_profile():
    return templates.TemplateResponse("profile.html", {"request": {}})

@app.get("/assessment", response_class=HTMLResponse)
async def read_assessment():
    return templates.TemplateResponse("assessment.html", {"request": {}})

@app.get("/api-docs", response_class=HTMLResponse)
async def read_api_docs():
    return templates.TemplateResponse("api_docs.html", {"request": {}})

@app.get("/about", response_class=HTMLResponse)
async def read_about():
    return templates.TemplateResponse("about.html", {"request": {}})

@app.get("/api/profiles", response_model=List[UserProfile])
async def get_profiles():
    conn = sqlite3.connect('health_assessment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserProfile")
    rows = cursor.fetchall()
    conn.close()
    return [UserProfile(id=row[0], age=row[1], lifestyle=row[2], family_history=row[3], health_metrics=eval(row[4])) for row in rows]

@app.post("/api/profiles", response_model=UserProfile)
async def create_profile(profile: UserProfile):
    conn = sqlite3.connect('health_assessment.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO UserProfile (age, lifestyle, family_history, health_metrics)
        VALUES (?, ?, ?, ?)
    ''', (profile.age, profile.lifestyle, profile.family_history, str(profile.health_metrics)))
    conn.commit()
    profile.id = cursor.lastrowid
    conn.close()
    return profile

@app.get("/api/assessments/{profile_id}", response_model=HealthAssessment)
async def get_assessment(profile_id: int):
    conn = sqlite3.connect('health_assessment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM HealthAssessment WHERE profile_id = ?", (profile_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return HealthAssessment(id=row[0], profile_id=row[1], risk_score=row[2], recommendations=eval(row[3]))
    raise HTTPException(status_code=404, detail="Assessment not found")

@app.post("/api/assessments", response_model=HealthAssessment)
async def create_assessment(assessment: HealthAssessment):
    conn = sqlite3.connect('health_assessment.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO HealthAssessment (profile_id, risk_score, recommendations)
        VALUES (?, ?, ?)
    ''', (assessment.profile_id, assessment.risk_score, str(assessment.recommendations)))
    conn.commit()
    assessment.id = cursor.lastrowid
    conn.close()
    return assessment
