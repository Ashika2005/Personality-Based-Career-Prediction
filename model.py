import torch
import torch.nn as nn

# --- 1. DEFINE THE MODEL ARCHITECTURE ---

class CareerPredictorModel(nn.Module):
    """
    A Multi-Layer Perceptron (MLP) for career prediction.

    This model is designed to take our 447-feature vector (63 form features + 
    384 text embedding features) and predict one of the 10 career classes.
    """
    def __init__(self, input_size, num_classes):
        """
        Initializes the layers of the network.
        
        Args:
            input_size (int): The number of input features (e.g., 447).
            num_classes (int): The number of output classes (e.g., 10 careers).
        """
        super(CareerPredictorModel, self).__init__()
        
        self.layers = nn.Sequential(
            # Input Layer (447 features)
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.4),  # Dropout helps prevent overfitting
            
            # Hidden Layer 1
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.4),
            
            # Hidden Layer 2
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Output Layer (10 careers)
            # We output raw "logits". CrossEntropyLoss will handle the softmax.
            nn.Linear(64, num_classes) 
        )

    def forward(self, x):
        """
        Defines the "forward pass" of the model.
        How data flows through the layers.
        """
        return self.layers(x)

if __name__ == "__main__":
    print("Testing model architecture...")
    
    INPUT_FEATURES = 447
    NUM_CAREERS = 10
    
    # (batch_size=5, num_features=447)
    input = torch.randn(5, INPUT_FEATURES)
    
    # Instantiate the model
    model = CareerPredictorModel(input_size=INPUT_FEATURES, num_classes=NUM_CAREERS)
    
    output = model(input)
    
    print(f"Input shape: {input.shape}")
    print(f"Output shape: {output.shape}")
    print("Model architecture test passed!")