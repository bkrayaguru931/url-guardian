import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from app.models.pytorch_lstm import PyTorchURLClassifier
import time

def load_dataset(filepath):
    """Load and preprocess the dataset"""
    print(f"📂 Loading dataset from {filepath}...")
    
    try:
        data = pd.read_csv(filepath)
        print(f"   Dataset shape: {data.shape}")
        
        urls = data['url'].values
        labels = np.array([1 if label != 'benign' else 0 for label in data['label'].values])
        
        print(f"   Total URLs: {len(urls)}")
        print(f"   Benign: {sum(labels == 0)}")
        print(f"   Malicious: {sum(labels == 1)}")
        
        return urls, labels
    except FileNotFoundError:
        print(f"❌ Dataset not found at {filepath}")
        print("Please ensure urldata.csv is in the project root directory")
        return None, None
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None, None

def main():
    # Configuration
    DATA_PATH = "urldata.csv"  # Update if dataset is elsewhere
    
    # Check if dataset exists in parent directory
    if not os.path.exists(DATA_PATH):
        # Try looking in current directory and parent
        possible_paths = [
            "urldata.csv",
            "../urldata.csv",
            "backend/urldata.csv",
            "data/urldata.csv"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                DATA_PATH = path
                break
    
    MODEL_SAVE_PATH = "models/pytorch_model"
    
    # Hyperparameters
    MAX_LEN = 200
    EMBEDDING_DIM = 128
    HIDDEN_DIM = 256
    NUM_LAYERS = 2
    EPOCHS = 20
    BATCH_SIZE = 64
    LEARNING_RATE = 0.001
    
    # Load data
    urls, labels = load_dataset(DATA_PATH)
    
    if urls is None:
        print("\n⚠️ Using sample data for demonstration...")
        # Sample data if dataset not found
        benign_urls = [
            "https://www.google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://www.python.org",
            "https://www.wikipedia.org",
            "https://www.reddit.com",
            "https://www.youtube.com",
            "https://www.amazon.com",
            "https://www.microsoft.com",
            "https://www.apple.com",
            "https://www.netflix.com",
            "https://www.spotify.com",
            "https://www.linkedin.com",
            "https://www.twitter.com",
            "https://www.instagram.com"
        ]
        
        malicious_urls = [
            "http://suspicious-login.tk/verify",
            "http://bit.ly/malware-link",
            "http://192.168.1.1/admin",
            "https://paypal.com.security.tk/login",
            "http://free-money.xyz/claim",
            "http://account-verify-ml.ga/secure",
            "https://banking-update.cf/login",
            "http://prize-winner.gq/claim",
            "https://secure-login.tk/amazon/verify",
            "http://update-payment.xyz/account",
            "http://tinyurl.com/phishing-site",
            "http://goo.gl/malware-download",
            "https://apple-id.verify.tk/login",
            "http://netflix-account.cf/update",
            "http://instagram-verify.ml/secure"
        ]
        
        # Repeat to have more data
        urls = np.array((benign_urls + malicious_urls) * 50)
        labels = np.array(([0]*len(benign_urls) + [1]*len(malicious_urls)) * 50)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        urls, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\n📊 Training set: {len(X_train)} URLs")
    print(f"📊 Test set: {len(X_test)} URLs")
    
    # Create and train model
    print("\n" + "="*60)
    print("🚀 Initializing PyTorch LSTM Model")
    print("="*60)
    print(f"   Max Length: {MAX_LEN}")
    print(f"   Embedding Dim: {EMBEDDING_DIM}")
    print(f"   Hidden Dim: {HIDDEN_DIM}")
    print(f"   LSTM Layers: {NUM_LAYERS}")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch Size: {BATCH_SIZE}")
    print(f"   Learning Rate: {LEARNING_RATE}")
    
    classifier = PyTorchURLClassifier(
        max_len=MAX_LEN,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_layers=NUM_LAYERS
    )
    
    # Train
    start_time = time.time()
    history = classifier.train(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        learning_rate=LEARNING_RATE
    )
    training_time = time.time() - start_time
    
    # Evaluate on test set
    print("\n" + "="*60)
    print("📈 Model Evaluation")
    print("="*60)
    
    classifier.model.eval()
    predictions = classifier.predict_batch(X_test)
    
    y_pred = np.array([1 if p['is_malicious'] else 0 for p in predictions])
    accuracy = np.mean(y_pred == y_test)
    
    # Calculate metrics
    from sklearn.metrics import classification_report, confusion_matrix
    
    print(f"\n✅ Test Accuracy: {accuracy:.4f}")
    print(f"⏱️  Training Time: {training_time:.2f} seconds")
    
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Benign', 'Malicious']))
    
    print("📊 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Benign: {cm[0][0]} | False Malicious: {cm[0][1]}")
    print(f"   False Benign: {cm[1][0]} | True Malicious: {cm[1][1]}")
    
    # Save model
    print("\n" + "="*60)
    print("💾 Saving Model")
    print("="*60)
    
    # Create models directory in backend
    os.makedirs("backend/models", exist_ok=True)
    classifier.save(MODEL_SAVE_PATH)
    print(f"\n✅ Model saved to {MODEL_SAVE_PATH}")
    print("✨ Ready to use in your API!")
    
    # Test with example URLs
    print("\n" + "="*60)
    print("🔍 Testing Example URLs")
    print("="*60)
    
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "http://suspicious-login.tk/verify",
        "http://paypal.com.security.tk/login",
        "https://stackoverflow.com/questions",
        "http://bit.ly/suspicious"
    ]
    
    for url in test_urls:
        result = classifier.predict(url)
        emoji = "🔴" if result['is_malicious'] else "🟢"
        print(f"{emoji} {url}")
        print(f"   Malicious: {result['is_malicious']}, "
              f"Confidence: {result['confidence']:.4f}, "
              f"Risk: {result['risk_level']}\n")

if __name__ == "__main__":
    main()