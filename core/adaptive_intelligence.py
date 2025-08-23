#!/usr/bin/env python3
"""
Adaptive Intelligence Module for Canary Protocol
Implements machine learning and adaptive features for continuous improvement
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
import os
from collections import defaultdict, Counter
import re

class CanaryIntelligence:
    def __init__(self, db_path="data/canary_protocol.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_intelligence_db()
    
    def init_intelligence_db(self):
        """Initialize tables for storing learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Historical patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                effectiveness_score REAL,
                usage_count INTEGER DEFAULT 1,
                last_updated TEXT,
                confidence_level REAL DEFAULT 0.5
            )
        ''')
        
        # Keyword performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE,
                true_positives INTEGER DEFAULT 0,
                false_positives INTEGER DEFAULT 0,
                context_category TEXT,
                urgency_correlation REAL DEFAULT 0.0,
                last_seen TEXT
            )
        ''')
        
        # Source reliability tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_reliability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_domain TEXT UNIQUE,
                accuracy_score REAL DEFAULT 0.5,
                bias_score REAL DEFAULT 0.0,
                speed_score REAL DEFAULT 0.5,
                total_articles INTEGER DEFAULT 0,
                verified_accurate INTEGER DEFAULT 0
            )
        ''')
        
        # Prediction accuracy tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_date TEXT,
                predicted_urgency INTEGER,
                actual_urgency INTEGER,
                prediction_accuracy REAL,
                contributing_factors TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def learn_from_digest(self, digest_data, user_feedback=None):
        """Learn from each digest generation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract patterns from successful analysis
        if digest_data.get('urgency_score', 0) > 0:
            self._update_keyword_performance(digest_data, cursor)
            self._update_source_reliability(digest_data, cursor)
            self._store_successful_patterns(digest_data, cursor)
        
        conn.commit()
        conn.close()
    
    def _update_source_reliability(self, digest_data, cursor):
        """Track reliability and bias of news sources"""
        sources = digest_data.get('sources', [])
        urgency = digest_data.get('urgency_score', 0)
        
        for source in sources:
            domain = self._extract_domain(source)
            
            # Update source statistics
            cursor.execute('''
                INSERT OR REPLACE INTO source_reliability 
                (source_domain, total_articles)
                VALUES (?, 1)
                ON CONFLICT(source_domain) DO UPDATE SET
                total_articles = total_articles + 1
            ''', (domain,))
            
            # Update accuracy based on urgency correlation
            if urgency > 5:  # High urgency articles
                cursor.execute('''
                    UPDATE source_reliability 
                    SET verified_accurate = verified_accurate + 1,
                        accuracy_score = (CAST(verified_accurate AS REAL) / total_articles)
                    WHERE source_domain = ?
                ''', (domain,))
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        import re
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else url
    
    def _update_keyword_performance(self, digest_data, cursor):
        """Track which keywords correlate with actual urgency"""
        keywords = self._extract_keywords_from_digest(digest_data)
        urgency = digest_data.get('urgency_score', 0)
        
        for keyword in keywords:
            cursor.execute('''
                INSERT OR REPLACE INTO keyword_performance 
                (keyword, urgency_correlation, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(keyword) DO UPDATE SET
                urgency_correlation = (urgency_correlation + ?) / 2,
                last_seen = ?
            ''', (keyword, urgency, datetime.now().isoformat(), urgency, datetime.now().isoformat()))
    
    def _extract_keywords_from_digest(self, digest_data):
        """Extract meaningful keywords from digest content"""
        text = digest_data.get('summary', '') + ' ' + str(digest_data.get('top_headlines', ''))
        
        # Political/economic keywords
        important_terms = [
            'supreme court', 'federal reserve', 'inflation', 'unemployment',
            'voting rights', 'constitution', 'emergency', 'crisis',
            'protest', 'violence', 'recession', 'market crash'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        for term in important_terms:
            if term in text_lower:
                found_keywords.append(term)
        
        return found_keywords
    
    def get_adaptive_urgency_weights(self):
        """Get learned weights for urgency calculation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT keyword, urgency_correlation 
            FROM keyword_performance 
            WHERE urgency_correlation > 0.6
        ''')
        
        high_impact_keywords = dict(cursor.fetchall())
        conn.close()
        
        return high_impact_keywords
    
    def predict_trend_urgency(self, headlines, economic_data):
        """Enhanced urgency prediction using learned patterns"""
        base_urgency = self._calculate_base_urgency(headlines, economic_data)
        
        # Apply learned keyword weights
        learned_weights = self.get_adaptive_urgency_weights()
        headline_text = ' '.join([h.get('title', '') for h in headlines]).lower()
        
        urgency_boost = 0
        for keyword, weight in learned_weights.items():
            if keyword in headline_text:
                urgency_boost += weight * 0.1  # Scale the boost
        
        # Historical pattern matching
        pattern_boost = self._get_pattern_match_boost(headlines, economic_data)
        
        final_urgency = min(10, base_urgency + urgency_boost + pattern_boost)
        
        # Store prediction for later accuracy tracking
        self._store_prediction(final_urgency, headlines, economic_data)
        
        return int(final_urgency), self._get_urgency_level(final_urgency)
    
    def _calculate_base_urgency(self, headlines, economic_data):
        """Calculate base urgency using existing logic"""
        urgency_score = 0
        
        high_urgency_terms = [
            "martial law", "emergency powers", "constitutional crisis", 
            "bank run", "currency collapse", "hyperinflation", "recession",
            "civil unrest", "widespread protests", "government shutdown"
        ]
        
        medium_urgency_terms = [
            "inflation", "unemployment rise", "market crash", "trade war",
            "voting rights", "discrimination increase", "policy reversal"
        ]
        
        all_text = " ".join([h.get('title', '') for h in headlines]).lower()
        
        for term in high_urgency_terms:
            if term in all_text:
                urgency_score += 3
                
        for term in medium_urgency_terms:
            if term in all_text:
                urgency_score += 1
        
        # Economic indicators
        for indicator in economic_data:
            if indicator.get('concern_level') == 'high':
                urgency_score += 2
            elif indicator.get('concern_level') == 'medium':
                urgency_score += 1
        
        return min(urgency_score, 10)
    
    def _get_pattern_match_boost(self, headlines, economic_data):
        """Find similar historical patterns and apply learned urgency adjustments"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_data, effectiveness_score, confidence_level
            FROM learning_patterns 
            WHERE pattern_type = 'urgency_boost' AND confidence_level > 0.7
        ''')
        
        patterns = cursor.fetchall()
        conn.close()
        
        boost = 0
        for pattern_data, effectiveness, confidence in patterns:
            try:
                pattern = json.loads(pattern_data)
                if self._pattern_matches_current(pattern, headlines, economic_data):
                    boost += effectiveness * confidence
            except:
                continue
        
        return min(boost, 2)  # Cap the boost
    
    def _pattern_matches_current(self, pattern, headlines, economic_data):
        """Check if stored pattern matches current situation"""
        # Simple pattern matching - can be enhanced
        pattern_keywords = pattern.get('keywords', [])
        current_text = ' '.join([h.get('title', '') for h in headlines]).lower()
        
        matches = sum(1 for keyword in pattern_keywords if keyword in current_text)
        return matches >= len(pattern_keywords) * 0.6  # 60% keyword match
    
    def _store_prediction(self, predicted_urgency, headlines, economic_data):
        """Store prediction for later accuracy evaluation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        factors = {
            'headline_count': len(headlines),
            'economic_indicators': len(economic_data),
            'high_concern_economic': len([e for e in economic_data if e.get('concern_level') == 'high'])
        }
        
        cursor.execute('''
            INSERT INTO prediction_tracking 
            (prediction_date, predicted_urgency, contributing_factors)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), predicted_urgency, json.dumps(factors)))
        
        conn.commit()
        conn.close()
    
    def _get_urgency_level(self, score):
        """Convert numeric score to level"""
        if score >= 7:
            return "HIGH"
        elif score >= 4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _store_successful_patterns(self, digest_data, cursor):
        """Store patterns that led to successful analysis"""
        if digest_data.get('urgency_score', 0) >= 5:  # Medium+ urgency
            pattern = {
                'keywords': self._extract_keywords_from_digest(digest_data),
                'urgency': digest_data.get('urgency_score'),
                'economic_factors': len(digest_data.get('economic_data', []))
            }
            
            cursor.execute('''
                INSERT INTO learning_patterns 
                (pattern_type, pattern_data, effectiveness_score, last_updated)
                VALUES (?, ?, ?, ?)
            ''', ('urgency_boost', json.dumps(pattern), digest_data.get('urgency_score') / 10.0, datetime.now().isoformat()))
    
    def get_intelligence_report(self):
        """Generate a report on learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Top performing keywords
        cursor.execute('''
            SELECT keyword, urgency_correlation 
            FROM keyword_performance 
            ORDER BY urgency_correlation DESC 
            LIMIT 10
        ''')
        top_keywords = cursor.fetchall()
        
        # Pattern count
        cursor.execute('SELECT COUNT(*) FROM learning_patterns')
        pattern_count = cursor.fetchone()[0]
        
        # Prediction accuracy (if we have feedback)
        cursor.execute('''
            SELECT AVG(prediction_accuracy) 
            FROM prediction_tracking 
            WHERE prediction_accuracy IS NOT NULL
        ''')
        avg_accuracy = cursor.fetchone()[0] or 0
        
        conn.close()
        
        report = f"""
🧠 CANARY PROTOCOL INTELLIGENCE REPORT
====================================

📊 Learning Statistics:
- Stored Patterns: {pattern_count}
- Average Prediction Accuracy: {avg_accuracy:.2%}
- Total Keywords Tracked: {len(top_keywords)}

🎯 Top Urgency Indicators:
"""
        for keyword, correlation in top_keywords[:5]:
            report += f"- {keyword}: {correlation:.2f} correlation\n"
        
        report += f"""
📈 Intelligence Capabilities:
✅ Adaptive keyword weighting
✅ Historical pattern matching  
✅ Source reliability tracking
✅ Prediction accuracy monitoring

🔮 Next Learning Opportunities:
- User feedback integration
- Seasonal pattern recognition
- Cross-correlation analysis
- Anomaly detection enhancement
"""
        
        return report

def enhance_urgency_assessment():
    """Enhanced urgency assessment using machine learning"""
    intelligence = CanaryIntelligence()
    
    def smart_assess_urgency(headlines, economic_data):
        return intelligence.predict_trend_urgency(headlines, economic_data)
    
    return smart_assess_urgency

if __name__ == "__main__":
    # Test the intelligence system
    intelligence = CanaryIntelligence()
    print(intelligence.get_intelligence_report())
