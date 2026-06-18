import numpy as np
import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple

class URLClassifier:
    def __init__(self):
        # Suspicious TLDs often used for phishing
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', 
            '.top', '.club', '.work', '.date'
        ]
        
        # URL shorteners (often used to hide malicious URLs)
        self.url_shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 
            'ow.ly', 'is.gd', 'buff.ly', 'adf.ly', 'bit.do'
        ]
        
        # Suspicious keywords
        self.suspicious_keywords = [
            'login', 'signin', 'verify', 'account', 'secure',
            'update', 'confirm', 'banking', 'password', 'billing',
            'paypal', 'amazon', 'ebay', 'netflix'
        ]
        
        # Brand names commonly used in phishing
        self.brand_names = [
            'paypal', 'apple', 'amazon', 'google', 'microsoft',
            'facebook', 'instagram', 'netflix', 'bank'
        ]
        
    def predict(self, url: str) -> dict:
        url_lower = url.lower()
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Initialize scores
        scores = {
            'suspicious_tld': 0.0,
            'url_shortener': 0.0,
            'ip_address': 0.0,
            'excessive_length': 0.0,
            'special_chars': 0.0,
            'suspicious_keywords': 0.0,
            'brand_impersonation': 0.0,
            'at_symbol': 0.0,
            'multiple_subdomains': 0.0,
            'http_not_https': 0.0
        }
        
        reasons = []
        
        # Check 1: Suspicious TLD
        for tld in self.suspicious_tlds:
            if domain.endswith(tld):
                scores['suspicious_tld'] = 0.7
                reasons.append(f"Suspicious TLD: {tld}")
                break
        
        # Check 2: URL Shortener
        for shortener in self.url_shorteners:
            if shortener in domain:
                scores['url_shortener'] = 0.5
                reasons.append(f"URL shortener detected: {shortener}")
                break
        
        # Check 3: IP Address instead of domain
        ip_pattern = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.match(ip_pattern, url_lower):
            scores['ip_address'] = 0.8
            reasons.append("IP address used instead of domain name")
        
        # Check 4: URL Length
        url_length = len(url)
        if url_length > 75:
            scores['excessive_length'] = min(0.3 + (url_length - 75) * 0.01, 0.7)
            if url_length > 100:
                reasons.append(f"Unusually long URL ({url_length} characters)")
        
        # Check 5: Special Characters
        special_chars = len(re.findall(r'[@#$%^&*()\-=+\[\]{}|;:,<>?]', url))
        if special_chars > 5:
            scores['special_chars'] = min(0.2 + special_chars * 0.05, 0.6)
            if special_chars > 10:
                reasons.append(f"Excessive special characters ({special_chars})")
        
        # Check 6: Suspicious Keywords
        keyword_count = 0
        for keyword in self.suspicious_keywords:
            if keyword in url_lower:
                keyword_count += 1
        
        if keyword_count >= 2:
            scores['suspicious_keywords'] = min(0.3 + keyword_count * 0.1, 0.7)
            reasons.append(f"Multiple suspicious keywords ({keyword_count})")
        elif keyword_count == 1:
            scores['suspicious_keywords'] = 0.2
        
        # Check 7: Brand Impersonation
        path_query = (parsed.path + parsed.query).lower()
        for brand in self.brand_names:
            # Check if brand name is in domain or path but it's not the official site
            if brand in domain and not domain.endswith(f'{brand}.com'):
                scores['brand_impersonation'] = 0.9
                reasons.append(f"Potential {brand} impersonation")
                break
            elif brand in path_query:
                scores['brand_impersonation'] = 0.6
                reasons.append(f"Brand name '{brand}' in URL path")
                break
        
        # Check 8: @ Symbol (used for URL spoofing)
        if '@' in url and '://' in url:
            scores['at_symbol'] = 0.9
            reasons.append("@ symbol detected (potential URL spoofing)")
        
        # Check 9: Multiple Subdomains
        subdomain_count = domain.count('.')
        if subdomain_count > 3:
            scores['multiple_subdomains'] = 0.4
            reasons.append(f"Multiple subdomains ({subdomain_count})")
        
        # Check 10: HTTP instead of HTTPS
        if parsed.scheme == 'http' and 'localhost' not in domain and not re.match(ip_pattern, url_lower):
            scores['http_not_https'] = 0.2
            reasons.append("Using HTTP instead of HTTPS")
        
        # Calculate weighted score
        weights = {
            'suspicious_tld': 0.8,
            'url_shortener': 0.6,
            'ip_address': 0.9,
            'excessive_length': 0.4,
            'special_chars': 0.5,
            'suspicious_keywords': 0.6,
            'brand_impersonation': 0.95,
            'at_symbol': 0.95,
            'multiple_subdomains': 0.5,
            'http_not_https': 0.3
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in scores)
        final_score = min(weighted_score, 1.0)
        
        # Determine if malicious
        is_malicious = final_score > 0.3
        
        # Calculate confidence
        if is_malicious:
            confidence = final_score
        else:
            confidence = 1.0 - final_score
        
        return {
            "is_malicious": is_malicious,
            "confidence": round(confidence, 3),
            "risk_score": round(final_score, 3),
            "reasons": reasons[:5],  # Top 5 reasons
            "risk_level": self._get_risk_level(final_score)
        }
    
    def _get_risk_level(self, score: float) -> str:
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "SAFE"
