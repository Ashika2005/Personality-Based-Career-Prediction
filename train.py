import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib  # For saving the label encoder
import numpy as np

# --- 1. IMPORT THE MODEL ---
from model import CareerPredictorModel

# --- 2. CONFIGURATION & HYPERPARAMETERS ---
DATA_FILE = "career_prediction_dataset.csv"
MODEL_SAVE_PATH = "career_model.pth"
ENCODER_SAVE_PATH = "career_label_encoder.joblib"

# Model parameters
INPUT_SIZE = 447  # 63 form features + 384 embedding features
NUM_CLASSES = 10  # We are starting with 10 careers

# Training parameters
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EPOCHS = 50       # You can increase this if the model is still learning

# --- 3. PYTORCH DATASET CLASS ---
class CareerDataset(Dataset):
    """Custom PyTorch Dataset for loading the career data."""
    def __init__(self, features, labels):
        # Convert to float32, the standard for model inputs
        self.features = torch.tensor(features, dtype=torch.float32)

        # Convert to long, the standard for CrossEntropyLoss labels
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        # Returns the total number of samples
        return len(self.labels)

    def __getitem__(self, idx):
        # Returns one sample (features, label) at the given index
        return self.features[idx], self.labels[idx]

# --- 4. MAIN TRAINING SCRIPT ---
if __name__ == "__main__":
    
    # --- Step 1: Load and Preprocess Data ---
    print(f"Loading data from {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"ERROR: {DATA_FILE} not found. Did you run the generator?")
        exit()

    X = df.drop('target_career', axis=1).values
    y_str = df['target_career'].values

    print("Encoding labels...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_str)
    
    joblib.dump(label_encoder, ENCODER_SAVE_PATH)
    print(f"Label encoder saved to {ENCODER_SAVE_PATH}")
    print(f"Found {len(label_encoder.classes_)} classes: {label_encoder.classes_}")

    # --- Step 2: Create Train/Validation Split ---
    print("Splitting data into train and validation sets (80/20)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # --- Step 3: Create Datasets and DataLoaders ---
    train_dataset = CareerDataset(X_train, y_train)
    val_dataset = CareerDataset(X_val, y_val)
    
    train_loader = DataLoader(
        dataset=train_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True  # Shuffle training data
    )
    
    val_loader = DataLoader(
        dataset=val_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=False # No need to shuffle validation
    )
    
    print(f"Total samples: {len(df)}")
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # --- Step 4: Initialize Model, Loss, and Optimizer ---
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = CareerPredictorModel(INPUT_SIZE, NUM_CLASSES).to(device)
    
    # CrossEntropyLoss is perfect for multi-class classification
    criterion = nn.CrossEntropyLoss()
    
    # Adam is a great, all-purpose optimizer
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # --- Step 5: The Training Loop ---
    print("\n--- STARTING TRAINING ---")
    
    best_val_accuracy = 0.0 # To save the best model

    for epoch in range(EPOCHS):
        # --- Training Phase ---
        model.train()  # Set model to training mode (enables dropout)
        total_train_loss = 0.0
        
        for features, labels in train_loader:
            # Move data to the device (e.g., GPU)
            features = features.to(device)
            labels = labels.to(device)
            
            # 1. Forward pass
            outputs = model(features)
            loss = criterion(outputs, labels)
            
            # 2. Backward pass and optimization
            optimizer.zero_grad()  # Clear old gradients
            loss.backward()        # Calculate new gradients
            optimizer.step()       # Update model weights
            
            total_train_loss += loss.item()

        # --- Validation Phase ---
        model.eval()   # Set model to evaluation mode (disables dropout)
        total_val_loss = 0.0
        correct_predictions = 0
        total_samples = 0
        
        with torch.no_grad(): # Disable gradient calculations
            for features, labels in val_loader:
                features = features.to(device)
                labels = labels.to(device)
                
                outputs = model(features)
                loss = criterion(outputs, labels)
                total_val_loss += loss.item()
                
                # Calculate accuracy
                # Get the index of the max log-probability (our prediction)
                _, predicted = torch.max(outputs.data, 1)
                
                total_samples += labels.size(0)
                correct_predictions += (predicted == labels).sum().item()

        # --- Log Results for this Epoch ---
        avg_train_loss = total_train_loss / len(train_loader)
        avg_val_loss = total_val_loss / len(val_loader)
        val_accuracy = 100 * correct_predictions / total_samples
        
        print(f"Epoch [{epoch+1}/{EPOCHS}] | "
              f"Train Loss: {avg_train_loss:.4f} | "
              f"Val Loss: {avg_val_loss:.4f} | "
              f"Val Accuracy: {val_accuracy:.2f}%")
        
        # --- Save the Best Model ---
        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  -> New best model saved to {MODEL_SAVE_PATH} (Accuracy: {val_accuracy:.2f}%)")

    print("--- TRAINING COMPLETE ---")
    print(f"Final best validation accuracy: {best_val_accuracy:.2f}%")
    print(f"Trained model saved to: {MODEL_SAVE_PATH}")