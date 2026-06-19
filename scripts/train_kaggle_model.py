import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from app.models.pytorch_lstm import PyTorchURLClassifier
import time
import gc

def load_kaggle_dataset():
    """Load the Kaggle malicious/benign URLs dataset"""
    
    possible_paths = [
        "urldata.csv",
        "malicious-and-benign-urls/urldata.csv",
        "../urldata.csv",
        "dataset/urldata.csv",
        os.path.expanduser("~/Downloads/urldata.csv"),
        os.path.expanduser("~/Desktop/urldata.csv")
    ]
    
    # Try to find with kagglehub
    try:
        import kagglehub
        path = kagglehub.dataset_download("siddharthkumar25/malicious-and-benign-urls")
        possible_paths.insert(0, f"{path}/urldata.csv")
        print(f"📦 Found dataset via kagglehub: {path}")
    except:
        pass
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"📂 Loading dataset from: {path}")
            data = pd.read_csv(path)
            print(f"   Dataset shape: {data.shape}")
            print(f"   Columns: {data.columns.tolist()}")
            
            urls = data['url'].values
            labels = np.array([1 if label != 'benign' else 0 for label in data['label'].values])
            
            print(f"   Total URLs: {len(urls):,}")
            print(f"   Benign: {sum(labels == 0):,}")
            print(f"   Malicious: {sum(labels == 1):,}")
            print(f"   Malicious ratio: {sum(labels == 1)/len(labels):.2%}")
            
            return urls, labels
    
    print("❌ Dataset not found!")
    print("Please download from: https://www.kaggle.com/datasets/siddharthkumar25/malicious-and-benign-urls")
    print("Place urldata.csv in the project root directory")
    return None, None

def main():
    # Load data
    urls, labels = load_kaggle_dataset()
    
    if urls is None:
        return
    
    # Use a subset if dataset is too large (optional, for faster training)
    # Comment out to use full dataset
    MAX_SAMPLES = 500000  # Use 500K URLs max
    
    if len(urls) > MAX_SAMPLES:
        print(f"\n⚠️  Limiting to {MAX_SAMPLES:,} samples for faster training")
        indices = np.random.choice(len(urls), MAX_SAMPLES, replace=False)
        urls = urls[indices]
        labels = labels[indices]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        urls, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\n📊 Training set: {len(X_train):,} URLs")
    print(f"📊 Test set: {len(X_test):,} URLs")
    
    # Free memory
    del urls, labels
    gc.collect()
    
    # Configuration
    MAX_LEN = 200
    EMBEDDING_DIM = 256      # Increased for better representation
    HIDDEN_DIM = 512         # Increased for more capacity
    NUM_LAYERS = 3           # More layers for deeper learning
    EPOCHS = 10              # More epochs for real data
    BATCH_SIZE = 128         # Larger batch for faster training
    LEARNING_RATE = 0.001
    
    print(f"\n{'='*60}")
    print("🚀 Training PyTorch BiLSTM Model")
    print(f"{'='*60}")
    print(f"   Samples: {len(X_train):,}")
    print(f"   Max Length: {MAX_LEN}")
    print(f"   Embedding Dim: {EMBEDDING_DIM}")
    print(f"   Hidden Dim: {HIDDEN_DIM}")
    print(f"   LSTM Layers: {NUM_LAYERS}")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch Size: {BATCH_SIZE}")
    
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
        validation_split=0.1,
        learning_rate=LEARNING_RATE
    )
    training_time = time.time() - start_time
    
    # Evaluate
    print(f"\n{'='*60}")
    print("📈 Model Evaluation")
    print(f"{'='*60}")
    
    classifier.model.eval()
    
    # Predict on test set in batches
    batch_size = 5000
    all_predictions = []
    
    for i in range(0, len(X_test), batch_size):
        batch_urls = X_test[i:i+batch_size]
        predictions = classifier.predict_batch(batch_urls)
        all_predictions.extend(predictions)
        if i % 10000 == 0:
            print(f"   Predicted {i}/{len(X_test)}...")
    
    y_pred = np.array([1 if p['is_malicious'] else 0 for p in all_predictions])
    accuracy = np.mean(y_pred == y_test)
    
    print(f"\n✅ Test Accuracy: {accuracy:.4f}")
    print(f"⏱️  Training Time: {training_time/60:.1f} minutes")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Benign', 'Malicious']))
    
    cm = confusion_matrix(y_test, y_pred)
    print(f"📊 Confusion Matrix:")
    print(f"   True Benign: {cm[0][0]:,} | False Malicious: {cm[0][1]:,}")
    print(f"   False Benign: {cm[1][0]:,} | True Malicious: {cm[1][1]:,}")
    
    # Calculate additional metrics
    tn, fp, fn, tp = cm.ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📈 Detailed Metrics:")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    print(f"   False Positive Rate: {fp/(fp+tn):.4f}")
    print(f"   False Negative Rate: {fn/(fn+tp):.4f}")
    
    # Save model
    print(f"\n{'='*60}")
    print("💾 Saving Model")
    print(f"{'='*60}")
    
    os.makedirs("backend/models", exist_ok=True)
    classifier.save("backend/models/kaggle_model")
    print(f"\n✅ Model saved to backend/models/kaggle_model")
    
    # Test with real examples
    print(f"\n{'='*60}")
    print("🔍 Testing Example URLs")
    print(f"{'='*60}")
    
    test_urls = [
        # Legitimate
        "https://www.google.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://www.paypal.com",
        "https://www.amazon.com",
        "https://www.wikipedia.org",
        "https://www.youtube.com",
        
        # Potentially malicious
        "http://suspicious-login.tk/verify",
        "http://bit.ly/malware-download",
        "http://192.168.1.1/admin",
        "https://paypal.com.security.ml/login",
        "http://free-prize.xyz/claim",
        "http://account-verify.ga/secure",
        "https://netflix-update.cf/account"
    ]
    
    for url in test_urls:
        result = classifier.predict(url)
        emoji = "🔴" if result['is_malicious'] else "🟢"
        print(f"\n{emoji} {url}")
        print(f"   Malicious: {result['is_malicious']}, "
              f"Confidence: {result['confidence']:.4f}, "
              f"Risk: {result['risk_level']}")
    
    print(f"\n{'='*60}")
    print("🎉 Training complete! Model ready for production.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()