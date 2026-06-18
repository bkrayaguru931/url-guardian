from urllib.parse import urlparse
import re
import os
from app.db.models import URLScan
from app.db.database import SessionLocal
from datetime import datetime

class URLAnalyzer:
    def __init__(self):
        self.pytorch_model = None
        self.rule_model = None
        
        # Try to load PyTorch LSTM model first
        try:
            from app.models.pytorch_lstm import PyTorchURLClassifier
            self.pytorch_model = PyTorchURLClassifier()
            model_path = "models/pytorch_model"
            if os.path.exists(f"{model_path}_config.pkl"):
                self.pytorch_model.load(model_path)
                print("✅ PyTorch LSTM model loaded successfully")
            else:
                print("⚠️ No trained PyTorch model found. Train it first.")
                self.pytorch_model = None
        except Exception as e:
            print(f"⚠️ Could not load PyTorch model: {e}")
            self.pytorch_model = None
        
        # Initialize rule-based as fallback
        from app.models.ml_model import URLClassifier
        self.rule_model = URLClassifier()
        print("✅ Rule-based detection ready")
        
        self.model_version = "3.0.0" if self.pytorch_model else "1.0.0"
    
    def extract_features(self, url: str) -> dict:
        """Extract comprehensive URL features"""
        parsed = urlparse(url)
        
        return {
            "url_length": len(url),
            "has_https": parsed.scheme == 'https',
            "num_special_chars": len(re.findall(r'[@#$%^&*()]', url)),
            "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', parsed.netloc)),
            "path_length": len(parsed.path),
            "num_subdomains": parsed.netloc.count('.') - 1 if parsed.netloc.count('.') > 1 else 0,
            "has_suspicious_tld": any(url.endswith(tld) for tld in ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz']),
            "num_digits": sum(c.isdigit() for c in url),
        }
    
    async def analyze_url(self, url: str) -> dict:
        """Analyze URL using best available model"""
        import time
        start_time = time.time()
        
        result = None
        
        # Try PyTorch model first
        if self.pytorch_model and self.pytorch_model.model:
            try:
                torch_result = self.pytorch_model.predict(url)
                rule_result = self.rule_model.predict(url)
                
                result = {
                    "is_malicious": torch_result["is_malicious"],
                    "confidence_score": torch_result["confidence"],
                    "risk_score": torch_result["raw_score"],
                    "risk_level": torch_result["risk_level"],
                    "reasons": rule_result.get("reasons", []),
                    "model_used": "PyTorch BiLSTM + Attention",
                    "model_version": self.model_version
                }
            except Exception as e:
                print(f"PyTorch prediction failed: {e}")
                result = self._rule_based_fallback(url)
        else:
            result = self._rule_based_fallback(url)
        
        result.update({
            "url": url,
            "features": self.extract_features(url),
            "analysis_time_ms": round((time.time() - start_time) * 1000, 2),
            "analysis_timestamp": datetime.utcnow().isoformat()
        })
        
        # Save to database
        try:
            self.save_scan(url, result)
        except:
            pass
        
        return result
    
    def _rule_based_fallback(self, url):
        """Fallback to rule-based detection"""
        rule_result = self.rule_model.predict(url)
        return {
            "is_malicious": rule_result["is_malicious"],
            "confidence_score": rule_result["confidence"],
            "risk_score": rule_result.get("risk_score", 0.5 if rule_result["is_malicious"] else 0.1),
            "risk_level": rule_result.get("risk_level", "MEDIUM" if rule_result["is_malicious"] else "SAFE"),
            "reasons": rule_result.get("reasons", []),
            "model_used": "Rule-based (PyTorch model not available)",
            "model_version": "1.0.0"
        }
    
    def save_scan(self, url: str, result: dict):
        """Save scan to database"""
        db = SessionLocal()
        try:
            scan = URLScan(
                url=url,
                is_malicious=result["is_malicious"],
                confidence_score=result.get("confidence_score", 0.0),
                model_version=result.get("model_version", "1.0.0")
            )
            db.add(scan)
            db.commit()
        finally:
            db.close()