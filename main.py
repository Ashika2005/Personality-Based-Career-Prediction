import joblib
import torch
import torch.nn as nn
import numpy as np
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field
from enum import Enum
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. LOAD API KEY & CONFIGURE GEMINI ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# --- 2. IMPORT PYTORCH MODEL ARCHITECTURE ---
from model import CareerPredictorModel 

# --- 3. CONFIGURATION & ASSET LOADING ---
MODEL_PATH = "career_model.pth"
ENCODER_PATH = "career_label_encoder.joblib"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
INPUT_SIZE = 447
NUM_CLASSES = 10

print("Loading all models and assets...")

# Load ML model
model = CareerPredictorModel(INPUT_SIZE, NUM_CLASSES).to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval() 

# Load label encoder
label_encoder = joblib.load(ENCODER_PATH)

# Load NLP embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=DEVICE)

# Load static career data
try:
    with open("career_data.json", 'r') as f:
        career_data = json.load(f)
    # Convert to a string for the Gemini prompt
    CAREER_DATA_STRING = json.dumps(career_data)
except FileNotFoundError:
    print("WARNING: career_data.json not found. Chatbot and info endpoints will fail.")
    career_data = {}
    CAREER_DATA_STRING = "{}"

print("Assets loaded successfully. Starting server...")

# --- 4. PYDANTIC MODELS (ENUMS) ---
class ActivityPref(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"; E = "E"
class ProblemType(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"; E = "E"
class Motivation(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"
class WorkEnv(str, Enum):
    solo = "Solo work with deep focus"; team = "Collaborative team projects"
    fieldwork = "Fieldwork / hands-on experimentation"; client = "Client interaction and presentations"
    creative = "Creative and flexible workspace"
class TeamStyle(str, Enum):
    lead = "I like leading and organizing teams"; translate = "I’m good at translating complex ideas to simple terms"
    technical = "I prefer technical contributions over social interactions"; brainstorm = "I enjoy brainstorming and creative collaboration"
class ToughProblem(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"
class FailAction(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"
class ImpactPref(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"; E = "E"
class ProjectExcite(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"; E = "E"
class SubjectEngage(str, Enum):
    math = "Mathematics / Logic"; physics = "Physics / Mechanics"
    compsci = "Computer Science / AI"; design = "Design / Art"
    env = "Environment / Biology"; business = "Business / Economics"
class WorkWith(str, Enum):
    A = "A"; B = "B"; C = "C"; D = "D"

# --- 5. PYDANTIC MODELS (API I/O) ---
class CareerQuery(BaseModel):
    q_logic: int = Field(..., ge=1, le=5); q_physical: int = Field(..., ge=1, le=5)
    q_data_patterns: int = Field(..., ge=1, le=5); q_creative_visuals: int = Field(..., ge=1, le=5)
    q_social_impact: int = Field(..., ge=1, le=5); q_activity_pref: ActivityPref
    q_problem_type: ProblemType; q_motivation: Motivation; q_work_env: List[WorkEnv]
    q_team_style: List[TeamStyle]; q_tough_problem: ToughProblem
    q_comfort_coding: int = Field(..., ge=1, le=5); q_comfort_math: int = Field(..., ge=1, le=5)
    q_comfort_design: int = Field(..., ge=1, le=5); q_comfort_physics: int = Field(..., ge=1, le=5)
    q_comfort_comms: int = Field(..., ge=1, le=5); q_fail_action: FailAction
    q_impact_pref: ImpactPref; q_project_excite: ProjectExcite
    q_subject_engage: List[SubjectEngage]; q_tech_curiosity: int = Field(..., ge=1, le=10)
    q_work_with: WorkWith; q_risk_comfort: int = Field(..., ge=1, le=5)
    q_project_hobby: str; q_future_feel: str

class PredictionResponse(BaseModel):
    predicted_career: str
    confidence_score: float
    all_scores: Dict[str, float]

class ChatQuery(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# --- 6. DATA PROCESSING HELPER ---
def process_input(query: CareerQuery) -> torch.Tensor:
    """Converts a CareerQuery object into a 447-feature tensor."""
    scalar_features = [
        query.q_logic / 5, query.q_physical / 5, query.q_data_patterns / 5,
        query.q_creative_visuals / 5, query.q_social_impact / 5,
        query.q_comfort_coding / 5, query.q_comfort_math / 5,
        query.q_comfort_design / 5, query.q_comfort_physics / 5,
        query.q_comfort_comms / 5, query.q_tech_curiosity / 10,
        query.q_risk_comfort / 5
    ]
    def to_one_hot(val, enum_map):
        vec = [0.0] * len(enum_map)
        if val in enum_map: vec[enum_map.index(val)] = 1.0
        return vec
    def to_multi_hot(val_list, enum_map):
        vec = [0.0] * len(enum_map)
        for val in val_list:
            if val in enum_map: vec[enum_map.index(val)] = 1.0
        return vec
    
    activity_map = [e.value for e in ActivityPref]; problem_map = [e.value for e in ProblemType]
    motivation_map = [e.value for e in Motivation]; work_env_map = [e.value for e in WorkEnv]
    team_style_map = [e.value for e in TeamStyle]; tough_problem_map = [e.value for e in ToughProblem]
    fail_action_map = [e.value for e in FailAction]; impact_map = [e.value for e in ImpactPref]
    project_map = [e.value for e in ProjectExcite]; subject_map = [e.value for e in SubjectEngage]
    work_with_map = [e.value for e in WorkWith]

    encoded_features = []
    encoded_features.extend(to_one_hot(query.q_activity_pref, activity_map))
    encoded_features.extend(to_one_hot(query.q_problem_type, problem_map))
    encoded_features.extend(to_one_hot(query.q_motivation, motivation_map))
    encoded_features.extend(to_multi_hot(query.q_work_env, work_env_map))
    encoded_features.extend(to_multi_hot(query.q_team_style, team_style_map))
    encoded_features.extend(to_one_hot(query.q_tough_problem, tough_problem_map))
    encoded_features.extend(to_one_hot(query.q_fail_action, fail_action_map))
    encoded_features.extend(to_one_hot(query.q_impact_pref, impact_map))
    encoded_features.extend(to_one_hot(query.q_project_excite, project_map))
    encoded_features.extend(to_multi_hot(query.q_subject_engage, subject_map))
    encoded_features.extend(to_one_hot(query.q_work_with, work_with_map))
    
    combined_text = query.q_project_hobby + " " + query.q_future_feel
    embedding = embedding_model.encode(combined_text)
    embedding_features = list(embedding)
    
    final_features = scalar_features + encoded_features + embedding_features
    return torch.tensor(final_features, dtype=torch.float32).unsqueeze(0).to(DEVICE)

# --- 7. FASTAPI APP & ENDPOINTS ---
app = FastAPI(
    title="AI Career Predictor API",
    description="An API to predict engineering careers and provide chat."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "AI Career Predictor API is running. Go to /docs."}

@app.post("/predict", response_model=PredictionResponse)
def predict_career(query: CareerQuery):
    """Takes the 21-question form input and returns a career prediction."""
    try:
        input_tensor = process_input(query)
        
        with torch.no_grad():
            logits = model(input_tensor)
            probabilities = torch.softmax(logits, dim=1).squeeze()
            
        confidence, predicted_idx = torch.max(probabilities, 0)
        predicted_idx_item = predicted_idx.item()
        
        predicted_career = label_encoder.inverse_transform([predicted_idx_item])[0]
        confidence_score = confidence.item()
        
        all_scores = {
            label_encoder.inverse_transform([i])[0]: prob.item() 
            for i, prob in enumerate(probabilities)
        }

        return PredictionResponse(
            predicted_career=predicted_career,
            confidence_score=confidence_score,
            all_scores=all_scores
        )
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Error processing prediction.")

@app.get("/careers")
def get_all_careers():
    """Returns a list of all available careers and their descriptions."""
    try:
        career_list = [
            {"name": name, "description": data["description"]}
            for name, data in career_data.items()
        ]
        return career_list
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not load career data.")

@app.get("/learning-path/{career_name}")
def get_learning_path(career_name: str):
    """Returns the learning path for a specific career."""
    if career_name not in career_data:
        raise HTTPException(status_code=404, detail="Career not found")
    
    return {
        "career": career_name,
        "path": career_data[career_name].get("learning_path", [])
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_mentor(query: ChatQuery):
    """New chatbot endpoint powered by the Gemini API."""
    
    system_prompt = f"""
    You are an expert AI Career Mentor for engineering students.
    Your tone is helpful, encouraging, and professional.
    You MUST use the following JSON data as your *only* source of truth 
    to answer questions about careers and learning paths.
    Do not make up information. If the data isn't in this JSON, 
    say you don't have that specific information.

    Here is your data:
    {CAREER_DATA_STRING}
    """
    
    full_prompt = f"{system_prompt}\n\nUser Question: {query.message}"

    try:
        response = await gemini_model.generate_content_async(full_prompt)
        return ChatResponse(response=response.text)

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # **FIXED**: Raise an HTTPException so the frontend knows there was an error
        raise HTTPException(status_code=500, detail="Error communicating with AI model.")

# --- 8. RUN THE SERVER ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)