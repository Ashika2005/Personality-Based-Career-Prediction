import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import warnings
import json # <-- Import JSON library

# Suppress a common warning from the sentence_transformers library
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data")

# --- 1. CONFIGURATION ---
PERSONA_FILE = "personas.json"
SAMPLES_PER_CAREER = 200
OUTPUT_FILENAME = "career_prediction_dataset.csv"

# --- 2. LOAD EXTERNAL PERSONA MAP ---
def load_personas(filename):
    """Loads the persona definitions from an external JSON file."""
    print(f"Loading persona map from {filename}...")
    try:
        with open(filename, 'r') as f:
            persona_map = json.load(f)
        
        # Filter out any personas that are null/empty
        defined_personas = {k: v for k, v in persona_map.items() if v}
        
        if len(defined_personas) < len(persona_map):
            print("\n" + "="*30)
            print("!! ACTION REQUIRED !!")
            print("The following careers in 'personas.json' are 'null':")
            for career, p in persona_map.items():
                if not p:
                    print(f"- {career}")
            print("Will only generate data for the defined personas.")
            print("="*30 + "\n")
            
        return defined_personas
        
    except FileNotFoundError:
        print(f"ERROR: Persona file not found at {filename}")
        print("Please create 'personas.json' in the same directory.")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode {filename}. Is it valid JSON?")
        return None

# --- 3. HELPER FUNCTIONS FOR DATA GENERATION ---
def generate_likert(mean, std_dev=0.75, min_val=1, max_val=5):
    """Generates a realistic, clipped, and rounded Likert scale answer."""
    val = np.random.normal(loc=mean, scale=std_dev)
    val = np.round(val)
    val = np.clip(val, min_val, max_val)
    return int(val)

def generate_slider(mean, std_dev=1.0, min_val=1, max_val=10):
    """Generates a realistic, clipped, and rounded 1-10 slider answer."""
    val = np.random.normal(loc=mean, scale=std_dev)
    val = np.round(val)
    val = np.clip(val, min_val, max_val)
    return int(val)

def generate_one_hot(probabilities):
    """Selects one choice based on probabilities and returns a one-hot vector."""
    num_choices = len(probabilities)
    # Ensure probabilities sum to 1
    probs_normalized = np.array(probabilities) / np.sum(probabilities)
    choice_index = np.random.choice(num_choices, p=probs_normalized)
    one_hot = np.zeros(num_choices)
    one_hot[choice_index] = 1
    return list(one_hot)

def generate_multi_hot(probabilities):
    """Flips a biased coin for each choice and returns a multi-hot vector."""
    return [1 if np.random.rand() < prob else 0 for prob in probabilities]

def generate_text_embedding(project_samples, future_samples, model):
    """Randomly picks one of each text, combines, and embeds them."""
    project_text = np.random.choice(project_samples)
    future_text = np.random.choice(future_samples)
    combined_text = project_text + " " + future_text
    
    # .encode() turns the text into a 384-number vector
    embedding = model.encode(combined_text)
    return list(embedding)

# --- 4. MAIN DATA GENERATION FUNCTION ---

def generate_dataset(persona_map, num_samples_per_career, model):
    all_data = []
    
    # Get the number of text embedding dimensions from the model
    EMBEDDING_SIZE = model.get_sentence_embedding_dimension()

    for career, persona in persona_map.items():
            
        print(f"Generating {num_samples_per_career} samples for {career}...")
        
        for _ in range(num_samples_per_career):
            # 1. Generate all features based on persona
            
            # Section A (Normalized 0-1)
            f_logic = generate_likert(persona['q_logic']) / 5
            f_physical = generate_likert(persona['q_physical']) / 5
            f_data = generate_likert(persona['q_data_patterns']) / 5
            f_creative = generate_likert(persona['q_creative_visuals']) / 5
            f_impact = generate_likert(persona['q_social_impact']) / 5
            
            # Section B (One-Hot)
            f_activity = generate_one_hot(persona['q_activity_pref'])
            f_problem = generate_one_hot(persona['q_problem_type'])
            f_motivation = generate_one_hot(persona['q_motivation'])

            # Section C (Multi-Hot)
            f_work_env = generate_multi_hot(persona['q_work_env'])
            f_team_style = generate_multi_hot(persona['q_team_style'])

            # Section D (Mixed)
            f_tough_problem = generate_one_hot(persona['q_tough_problem'])
            f_comfort_coding = generate_likert(persona['q_comfort_coding']) / 5
            f_comfort_math = generate_likert(persona['q_comfort_math']) / 5
            f_comfort_design = generate_likert(persona['q_comfort_design']) / 5
            f_comfort_physics = generate_likert(persona['q_comfort_physics']) / 5
            f_comfort_comms = generate_likert(persona['q_comfort_comms']) / 5
            f_fail_action = generate_one_hot(persona['q_fail_action'])

            # Section E (One-Hot)
            f_impact_pref = generate_one_hot(persona['q_impact_pref'])
            f_project_excite = generate_one_hot(persona['q_project_excite'])
            f_subject_engage = generate_one_hot(persona['q_subject_engage'])

            # Section F (Mixed)
            f_tech_curiosity = generate_slider(persona['q_tech_curiosity']) / 10
            f_work_with = generate_one_hot(persona['q_work_with'])
            f_risk_comfort = generate_likert(persona['q_risk_comfort']) / 5

            # Section G (Text Embedding)
            f_text_embedding = generate_text_embedding(
                persona['q_project_hobby_samples'],
                persona['q_future_feel_samples'],
                model
            )
            
            # 2. Combine all features into one flat list
            features = [
                f_logic, f_physical, f_data, f_creative, f_impact,
                f_comfort_coding, f_comfort_math, f_comfort_design, f_comfort_physics, f_comfort_comms,
                f_tech_curiosity, f_risk_comfort
            ]
            features.extend(f_activity)
            features.extend(f_problem)
            features.extend(f_motivation)
            features.extend(f_work_env)
            features.extend(f_team_style)
            features.extend(f_tough_problem)
            features.extend(f_fail_action)
            features.extend(f_impact_pref)
            features.extend(f_project_excite)
            features.extend(f_subject_engage)
            features.extend(f_work_with)
            features.extend(f_text_embedding)
            
            # 3. Add the target label
            features.append(career)
            all_data.append(features)

    # 5. Create the final DataFrame
    
    # Create column names
    col_names = [
        'f_logic', 'f_physical', 'f_data', 'f_creative', 'f_impact',
        'f_comfort_coding', 'f_comfort_math', 'f_comfort_design', 'f_comfort_physics', 'f_comfort_comms',
        'f_tech_curiosity', 'f_risk_comfort'
    ]
    col_names.extend([f'f_activity_{i}' for i in range(5)])
    col_names.extend([f'f_problem_{i}' for i in range(5)])
    col_names.extend([f'f_motivation_{i}' for i in range(4)])
    col_names.extend([f'f_work_env_{i}' for i in range(5)])
    col_names.extend([f'f_team_style_{i}' for i in range(4)])
    col_names.extend([f'f_tough_problem_{i}' for i in range(4)])
    col_names.extend([f'f_fail_action_{i}' for i in range(4)])
    col_names.extend([f'f_impact_pref_{i}' for i in range(5)])
    col_names.extend([f'f_project_excite_{i}' for i in range(5)])
    col_names.extend([f'f_subject_engage_{i}' for i in range(6)])
    col_names.extend([f'f_work_with_{i}' for i in range(4)])
    col_names.extend([f'emb_{i}' for i in range(EMBEDDING_SIZE)])
    col_names.append('target_career')

    df = pd.DataFrame(all_data, columns=col_names)
    return df

# --- 5. EXECUTE THE SCRIPT ---
if __name__ == "__main__":
    
    # 1. Load Personas
    persona_map = load_personas(PERSONA_FILE)
    
    if persona_map:
        # 2. Load NLP Model
        print("Loading NLP model (this may take a moment)...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("NLP model loaded.")
        
        # 3. Generate Dataset
        final_dataset = generate_dataset(
            persona_map, 
            SAMPLES_PER_CAREER, 
            embedding_model
        )
        
        # 4. Save to file
        final_dataset.to_csv(OUTPUT_FILENAME, index=False)
        
        print("\n--- SCRIPT COMPLETE ---")
        print(f"Total samples generated: {len(final_dataset)}")
        print(f"Total features (including embeddings): {len(final_dataset.columns) - 1}")
        print(f"Dataset saved to: {OUTPUT_FILENAME}")
        print("\nSample of your new dataset:")
        print(final_dataset.head())
    else:
        print("Dataset generation cancelled due to errors.")