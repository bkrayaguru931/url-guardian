import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
import os
from collections import Counter

class URLDataset(Dataset):
    """Custom Dataset for URL data"""
    def __init__(self, urls, labels, char_to_idx, max_len=200):
        self.urls = urls
        self.labels = labels
        self.char_to_idx = char_to_idx
        self.max_len = max_len
        
    def __len__(self):
        return len(self.urls)
    
    def __getitem__(self, idx):
        url = self.urls[idx][:self.max_len]
        label = self.labels[idx]
        
        # Convert URL to character indices
        seq = []
        for char in url:
            seq.append(self.char_to_idx.get(char, 1))  # 1 is <UNK>
        
        # Pad sequence
        while len(seq) < self.max_len:
            seq.append(0)  # 0 is <PAD>
        
        return torch.tensor(seq[:self.max_len], dtype=torch.long), torch.tensor(label, dtype=torch.float32)


class URLLSTM(nn.Module):
    """BiLSTM with Attention for URL Classification"""
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2, dropout=0.5):
        super(URLLSTM, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers, 
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # Embedding
        embedded = self.embedding(x)
        embedded = self.dropout(embedded)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Attention mechanism
        attention_weights = self.attention(lstm_out)
        attention_weights = torch.softmax(attention_weights, dim=1)
        
        # Apply attention
        context_vector = torch.sum(attention_weights * lstm_out, dim=1)
        
        # Fully connected layers
        output = self.fc(context_vector)
        
        return output.squeeze()


class PyTorchURLClassifier:
    """Complete PyTorch-based URL classifier"""
    
    def __init__(self, max_len=200, embedding_dim=128, hidden_dim=256, num_layers=2):
        self.max_len = max_len
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.char_to_idx = {'<PAD>': 0, '<UNK>': 1}
        self.vocab_size = 2
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"🖥️  Using device: {self.device}")
    
    def build_vocab(self, urls):
        """Build character vocabulary from URLs"""
        all_chars = set()
        for url in urls:
            all_chars.update(url[:self.max_len])
        
        # Add all unique characters
        for idx, char in enumerate(sorted(all_chars)):
            self.char_to_idx[char] = idx + 2  # 0=PAD, 1=UNK
        
        self.vocab_size = len(self.char_to_idx)
        print(f"📚 Vocabulary size: {self.vocab_size}")
        
    def prepare_data(self, urls, labels):
        """Prepare data loaders"""
        # Build vocabulary if not already built
        if len(self.char_to_idx) <= 2:
            self.build_vocab(urls)
        
        # Create dataset
        dataset = URLDataset(urls, labels, self.char_to_idx, self.max_len)
        
        return dataset
    
    def train(self, urls, labels, epochs=20, batch_size=64, validation_split=0.2, learning_rate=0.001):
        """Train the model"""
        # Convert to numpy arrays
        urls = np.array(urls)
        labels = np.array(labels, dtype=np.float32)
        
        # Build vocabulary first
        self.build_vocab(urls)
        
        # Split data
        indices = np.random.permutation(len(urls))
        split_idx = int(len(urls) * (1 - validation_split))
        train_indices = indices[:split_idx]
        val_indices = indices[split_idx:]
        
        # Prepare datasets
        train_dataset = URLDataset(urls[train_indices], labels[train_indices], self.char_to_idx, self.max_len)
        val_dataset = URLDataset(urls[val_indices], labels[val_indices], self.char_to_idx, self.max_len)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        self.model = URLLSTM(
            vocab_size=len(self.char_to_idx),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
        
        # Training loop
        print("\n" + "="*60)
        print("🚀 Training PyTorch BiLSTM with Attention")
        print("="*60)
        
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0
            
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                
                train_loss += loss.item()
                predicted = (outputs > 0.5).float()
                train_total += batch_y.size(0)
                train_correct += (predicted == batch_y).sum().item()
            
            avg_train_loss = train_loss / len(train_loader)
            train_accuracy = 100 * train_correct / train_total
            
            # Validation phase
            self.model.eval()
            val_loss = 0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_x)
                    loss = criterion(outputs, batch_y)
                    
                    val_loss += loss.item()
                    predicted = (outputs > 0.5).float()
                    val_total += batch_y.size(0)
                    val_correct += (predicted == batch_y).sum().item()
            
            avg_val_loss = val_loss / len(val_loader)
            val_accuracy = 100 * val_correct / val_total
            
            # Learning rate scheduling
            scheduler.step(avg_val_loss)
            
            # Save history
            history['train_loss'].append(avg_train_loss)
            history['val_loss'].append(avg_val_loss)
            history['train_acc'].append(train_accuracy)
            history['val_acc'].append(val_accuracy)
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                os.makedirs('models', exist_ok=True)
                torch.save(self.model.state_dict(), 'models/best_pytorch_model.pth')
            
            # Print progress
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"Epoch [{epoch+1}/{epochs}] "
                      f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_accuracy:.2f}% | "
                      f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_accuracy:.2f}%")
        
        # Load best model
        self.model.load_state_dict(torch.load('models/best_pytorch_model.pth'))
        print("\n✅ Training complete!")
        
        return history
    
    def predict(self, url):
        """Predict single URL"""
        if isinstance(url, list):
            return self.predict_batch(url)
        
        self.model.eval()
        
        # Convert URL to sequence
        seq = []
        for char in url[:self.max_len]:
            seq.append(self.char_to_idx.get(char, 1))
        
        # Pad sequence
        while len(seq) < self.max_len:
            seq.append(0)
        
        # Convert to tensor
        x = torch.tensor([seq[:self.max_len]], dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            prediction = self.model(x).item()
        
        is_malicious = prediction > 0.5
        confidence = prediction if is_malicious else 1 - prediction
        
        return {
            "url": url,
            "is_malicious": bool(is_malicious),
            "confidence": round(float(confidence), 4),
            "raw_score": float(prediction),
            "risk_level": self._get_risk_level(prediction)
        }
    
    def predict_batch(self, urls):
        """Predict multiple URLs"""
        self.model.eval()
        
        results = []
        for url in urls:
            results.append(self.predict(url))
        
        return results
    
    def _get_risk_level(self, score):
        """Get risk level from score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "SAFE"
    
    def save(self, path="models/pytorch_model"):
        """Save model and vocabulary"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # Save model state
        if self.model:
            torch.save(self.model.state_dict(), f"{path}_state.pth")
        
        # Save vocabulary and config
        config = {
            'char_to_idx': self.char_to_idx,
            'max_len': self.max_len,
            'embedding_dim': self.embedding_dim,
            'hidden_dim': self.hidden_dim,
            'num_layers': self.num_layers,
            'vocab_size': self.vocab_size
        }
        
        with open(f"{path}_config.pkl", 'wb') as f:
            pickle.dump(config, f)
        
        print(f"💾 Model saved to {path}")
    
    def load(self, path="models/pytorch_model"):
        """Load model and vocabulary"""
        # Load config
        with open(f"{path}_config.pkl", 'rb') as f:
            config = pickle.load(f)
        
        self.char_to_idx = config['char_to_idx']
        self.max_len = config['max_len']
        self.embedding_dim = config['embedding_dim']
        self.hidden_dim = config['hidden_dim']
        self.num_layers = config['num_layers']
        self.vocab_size = config['vocab_size']
        
        # Initialize model
        self.model = URLLSTM(
            vocab_size=self.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers
        ).to(self.device)
        
        # Load state dict
        self.model.load_state_dict(torch.load(f"{path}_state.pth", map_location=self.device))
        self.model.eval()
        
        print(f"📂 Model loaded from {path}")