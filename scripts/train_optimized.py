import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from app.models.pytorch_lstm import PyTorchURLClassifier
import time
import torch

print("📂 Loading dataset...")
data = pd.read_csv("urldata.csv")
urls = data['url'].values
labels = np.array([1 if label != 'benign' else 0 for label in data['label'].values])

print(f"   Total: {len(urls):,} URLs")
print(f"   Benign: {sum(labels == 0):,}")
print(f"   Malicious: {sum(labels == 1):,}")

# Use a balanced subset for faster training
# Take 100K total (50K benign + 50K malicious)
print("\n⚡ Creating balanced subset for faster training...")
benign_idx = np.where(labels == 0)[0]
malicious_idx = np.where(labels == 1)[0]

# Take 50K from each
sample_size = min(50000, len(malicious_idx))
benign_sample = np.random.choice(benign_idx, sample_size, replace=False)
malicious_sample = np.random.choice(malicious_idx, sample_size, replace=False)

all_indices = np.concatenate([benign_sample, malicious_sample])
np.random.shuffle(all_indices)

urls = urls[all_indices]
labels = labels[all_indices]

print(f"   Balanced dataset: {len(urls):,} URLs (50% benign, 50% malicious)")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    urls, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")

# Use smaller model for CPU training
classifier = PyTorchURLClassifier(
    max_len=150,        # Reduced from 200
    embedding_dim=64,   # Reduced from 256
    hidden_dim=128,     # Reduced from 512
    num_layers=2        # Reduced from 3
)

print(f"\n{'='*60}")
print("🚀 Training (Optimized for CPU)")
print(f"{'='*60}")
print(f"   Max Length: 150")
print(f"   Embedding: 64")
print(f"   Hidden: 128")
print(f"   Layers: 2")
print(f"   Epochs: 5")
print(f"   Batch: 64")

# Train with fewer epochs
start_time = time.time()
history = classifier.train(
    X_train, y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.1,
    learning_rate=0.001
)
training_time = time.time() - start_time

# Evaluate on test set (sample for speed)
print(f"\n📊 Evaluating...")
test_sample_size = min(5000, len(X_test))
test_indices = np.random.choice(len(X_test), test_sample_size, replace=False)
X_test_sample = X_test[test_indices]
y_test_sample = y_test[test_indices]

predictions = classifier.predict_batch(X_test_sample)
y_pred = np.array([1 if p['is_malicious'] else 0 for p in predictions])
accuracy = np.mean(y_pred == y_test_sample)

print(f"\n✅ Test Accuracy: {accuracy:.4f}")
print(f"⏱️  Training Time: {training_time/60:.1f} minutes")

print(f"\n📊 Classification Report:")
print(classification_report(y_test_sample, y_pred, target_names=['Benign', 'Malicious']))

cm = confusion_matrix(y_test_sample, y_pred)
print(f"Confusion Matrix:")
print(f"   True Benign: {cm[0][0]} | False Malicious: {cm[0][1]}")
print(f"   False Benign: {cm[1][0]} | True Malicious: {cm[1][1]}")

# Calculate metrics
tn, fp, fn, tp = cm.ravel()
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print(f"\n📈 Metrics:")
print(f"   Precision: {precision:.4f}")
print(f"   Recall: {recall:.4f}")
print(f"   F1-Score: {f1:.4f}")

# Save model
os.makedirs("backend/models", exist_ok=True)
classifier.save("backend/models/kaggle_model")
print(f"\n✅ Model saved!")
print(f"⏱️  Total time: {training_time/60:.1f} minutes")

# Test examples
print(f"\n{'='*60}")
print("🔍 Testing Examples")
print(f"{'='*60}")

test_urls = [
    "https://www.google.com",
    "https://github.com",
    "https://www.paypal.com",
    "http://suspicious-login.tk/verify",
    "http://bit.ly/malware-link",
    "https://paypal.com.security.ml/login"
]

for url in test_urls:
    result = classifier.predict(url)
    emoji = "🔴" if result['is_malicious'] else "🟢"
    print(f"{emoji} {result['risk_level']:8s} | {url[:60]}")
    print(f"   Score: {result['raw_score']:.4f}, Confidence: {result['confidence']:.4f}")

print(f"\n🎉 Done! Ready for production!")