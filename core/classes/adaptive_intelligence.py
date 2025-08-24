#!/usr/bin/env python3
"""
Adaptive Intelligence Module for Canary Protocol
Implements machine learning and adaptive features for continuous improvement
"""

import sqlite3
import json
import os
import re
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from functions.utils import ensure_directory_exists
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))
    from utils import ensure_directory_exists

try:
    from .base_db_class import BaseDBClass
except ImportError:
    try:
        from base_db_class import BaseDBClass
    except ImportError:
        # Fallback for when running from different directory
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from classes.base_db_class import BaseDBClass

class AdaptiveIntelligence(BaseDBClass):
    def __init__(self, db_path="data/canary_protocol.db"):
        super().__init__(db_path)

    def init_db(self):
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

    def learn_from_individual_articles(self, digest_date=None):
        """Learn from individual article feedback - HIGHER PRIORITY than digest feedback"""
        if not digest_date:
            digest_date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get individual article feedback for this digest
        cursor.execute('''
            SELECT article_title, article_source, user_urgency_rating,
                   ai_overall_urgency, feedback_type, comments, article_url
            FROM individual_article_feedback
            WHERE digest_date = ? AND user_urgency_rating != -1
        ''', (digest_date,))

        article_feedback = cursor.fetchall()

        if not article_feedback:
            conn.close()
            return

        print(f"🧠 Learning from {len(article_feedback)} individual article ratings...")

        for title, source, user_rating, ai_rating, feedback_type, comments, url in article_feedback:
            self._process_article_feedback(
                title,
                source,
                user_rating,
                ai_rating,
                feedback_type,
                comments,
                cursor)

        # Also learn from irrelevant articles (marked as -1)
        cursor.execute('''
            SELECT article_title, article_source, article_url
            FROM individual_article_feedback
            WHERE digest_date = ? AND user_urgency_rating = -1
        ''', (digest_date,))

        irrelevant_articles = cursor.fetchall()

        if irrelevant_articles:
            print(f"🧠 Learning irrelevant patterns from {len(irrelevant_articles)} articles...")
            for title, source, url in irrelevant_articles:
                self._process_irrelevant_article(title, source, cursor)

        conn.commit()
        conn.close()

        print("✅ Individual article learning complete!")

    def _process_article_feedback(
            self,
            title,
            source,
            user_rating,
            ai_rating,
            feedback_type,
            comments,
            cursor):
        """Process individual article feedback with 2x weight vs digest feedback"""
        ARTICLE_WEIGHT_MULTIPLIER = 2.0  # Higher weight for article-specific feedback

        # Extract and weight keywords from headline
        keywords = self._extract_keywords_from_headline(title)
        for keyword in keywords:
            # Update keyword performance with higher weight
            correlation = (user_rating / 10.0) * ARTICLE_WEIGHT_MULTIPLIER

            cursor.execute('''
                INSERT OR REPLACE INTO keyword_performance
                (keyword, urgency_correlation, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(keyword) DO UPDATE SET
                urgency_correlation = (urgency_correlation + ?) / 2,
                last_seen = ?
            ''', (keyword, correlation, datetime.now().isoformat(),
                  correlation, datetime.now().isoformat()))

        # Update source reliability at article level
        domain = self._extract_domain_from_source(source)
        if domain:
            # Calculate accuracy: how well did this source's content match user
            # expectation
            source_accuracy = 1.0 - abs(user_rating - ai_rating) / 10.0
            source_accuracy *= ARTICLE_WEIGHT_MULTIPLIER  # Higher weight

            cursor.execute('''
                INSERT OR REPLACE INTO source_reliability
                (source_domain, total_articles, verified_accurate, accuracy_score)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(source_domain) DO UPDATE SET
                total_articles = total_articles + 1,
                verified_accurate = verified_accurate + ?,
                accuracy_score = (CAST(verified_accurate AS REAL) / total_articles)
            ''', (domain, source_accuracy, source_accuracy, source_accuracy))

        # Store headline patterns with high confidence
        if user_rating >= 7 or user_rating <= 2:  # Clear urgent or non-urgent
            pattern_data = {
                'headline_structure': self._analyze_headline_structure(title),
                'keywords': keywords,
                'source': domain,
                'user_rating': user_rating,
                'pattern_source': 'individual_article'
            }

            effectiveness = (user_rating / 10.0) * ARTICLE_WEIGHT_MULTIPLIER
            confidence = 0.9  # High confidence for individual article feedback

            cursor.execute('''
                INSERT INTO learning_patterns
                (pattern_type, pattern_data, effectiveness_score, confidence_level, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', ('headline_pattern', json.dumps(pattern_data), effectiveness,
                  confidence, datetime.now().isoformat()))

    def _process_irrelevant_article(self, title, source, cursor):
        """Learn from articles marked as irrelevant - important for noise reduction"""
        keywords = self._extract_keywords_from_headline(title)
        domain = self._extract_domain_from_source(source)

        # Store as negative pattern - helps reduce false positives
        pattern_data = {
            'headline_structure': self._analyze_headline_structure(title),
            'keywords': keywords,
            'source': domain,
            'pattern_source': 'irrelevant_article'
        }

        cursor.execute('''
            INSERT INTO learning_patterns
            (pattern_type, pattern_data, effectiveness_score, confidence_level, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', ('irrelevant_pattern', json.dumps(pattern_data), 0.0, 0.8,
              datetime.now().isoformat()))

        # Reduce correlation for keywords found in irrelevant articles
        for keyword in keywords:
            cursor.execute('''
                UPDATE keyword_performance
                SET urgency_correlation = urgency_correlation * 0.9
                WHERE keyword = ?
            ''', (keyword,))

    def _extract_keywords_from_headline(self, headline):
        """Extract keywords from individual headline - more targeted than digest keywords"""
        if not headline:
            return []

        # Political/economic keywords relevant to headlines
        important_terms = [
            'supreme court',
            'federal reserve',
            'inflation',
            'unemployment',
            'recession',
            'voting rights',
            'constitution',
            'emergency',
            'crisis',
            'protest',
            'violence',
            'market crash',
            'martial law',
            'shutdown',
            'investigation',
            'scandal',
            'impeach',
            'resign',
            'arrest',
            'fraud',
            'corruption',
            'breach',
            'hack',
            'attack',
            'threat',
            'warning',
            'alert',
            'surge',
            'spike',
            'collapse',
            'ban',
            'block',
            'sanction',
            'tariff',
            'trade war',
            'nuclear',
            'military']

        headline_lower = headline.lower()
        found_keywords = []

        for term in important_terms:
            if term in headline_lower:
                found_keywords.append(term)

        # Also extract action words and intensity indicators
        action_words = [
            'breaks',
            'announces',
            'reveals',
            'exposes',
            'condemns',
            'approves',
            'rejects']
        for word in action_words:
            if word in headline_lower:
                found_keywords.append(word)

        return found_keywords

    def _analyze_headline_structure(self, headline):
        """Analyze structural patterns in headlines that correlate with urgency"""
        if not headline:
            return {}

        structure = {
            'length': len(headline),
            'has_caps': any(c.isupper() for c in headline),
            'has_numbers': any(c.isdigit() for c in headline),
            'has_quotes': '"' in headline or "'" in headline,
            'has_colon': ':' in headline,
            'starts_with_caps': headline and headline[0].isupper(),
            'word_count': len(headline.split())
        }

        # Urgency indicators
        urgency_indicators = [
            'BREAKING',
            'URGENT',
            'ALERT',
            '!!!',
            'LIVE',
            'UPDATE']
        structure['urgency_indicators'] = sum(
            1 for indicator in urgency_indicators if indicator in headline.upper())

        return structure

    def _extract_domain_from_source(self, source):
        """Extract domain from source string"""
        if not source:
            return None

        # Handle different source formats
        if 'http' in source:
            return self._extract_domain(source)
        else:
            # Source might be just the name like "Fox News", "NPR", etc.
            return source.lower().replace(' ', '_')

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
        text = digest_data.get('summary', '') + ' ' + \
            str(digest_data.get('top_headlines', ''))

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
        """Enhanced urgency prediction using learned patterns - prioritizes individual article feedback"""
        base_urgency = self._calculate_base_urgency(headlines, economic_data)

        # Apply learned keyword weights (prioritize article-level learning)
        learned_weights = self.get_adaptive_urgency_weights()
        headline_text = ' '.join([h.get('title', '') for h in headlines])
        
        # Get individual article pattern boost (highest priority)
        article_pattern_boost = self._get_individual_article_pattern_boost(headline_text)
        
        # Calculate urgency boost from learned weights
        urgency_boost = 0
        for keyword, weight in learned_weights.items():
            if keyword.lower() in headline_text.lower():
                urgency_boost += weight

        # Historical digest-level pattern matching (lower priority)
        digest_pattern_boost = self._get_pattern_match_boost(
            headlines, economic_data)

        # Combine with individual article patterns having 2x weight
        final_urgency = min(10, base_urgency + urgency_boost +
                            (article_pattern_boost * 2.0) + digest_pattern_boost)

        # Store prediction for later accuracy tracking
        self._store_prediction(final_urgency, headlines, economic_data)

        return int(final_urgency), self._get_urgency_level(final_urgency)

    def _get_individual_article_pattern_boost(self, headline_text):
        """Get urgency boost based on individual article patterns - HIGH PRIORITY"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Look for headline patterns from individual article feedback
        cursor.execute('''
            SELECT pattern_data, effectiveness_score, confidence_level
            FROM learning_patterns
            WHERE pattern_type = 'headline_pattern' AND confidence_level > 0.8
            ORDER BY effectiveness_score DESC
        ''', )

        patterns = cursor.fetchall()

        # Also check for irrelevant patterns to reduce false positives
        cursor.execute('''
            SELECT pattern_data
            FROM learning_patterns
            WHERE pattern_type = 'irrelevant_pattern' AND confidence_level > 0.7
        ''')

        irrelevant_patterns = cursor.fetchall()
        conn.close()

        boost = 0

        # Check against irrelevant patterns first (reduce false positives)
        for pattern_data, in irrelevant_patterns:
            try:
                pattern = json.loads(pattern_data)
                if self._headline_matches_pattern(headline_text, pattern):
                    boost -= 1.0  # Reduce urgency for patterns marked as irrelevant
            except BaseException:
                continue

        # Check against urgent patterns
        for pattern_data, effectiveness, confidence in patterns:
            try:
                pattern = json.loads(pattern_data)
                if self._headline_matches_pattern(headline_text, pattern):
                    boost += effectiveness * confidence
            except BaseException:
                continue

        return max(-2.0, min(boost, 3.0))  # Cap the boost/reduction

    def _headline_matches_pattern(self, headline_text, pattern):
        """Check if headline matches stored pattern from individual article feedback"""
        keywords = pattern.get('keywords', [])
        headline_structure = pattern.get('headline_structure', {})

        # Keyword matching
        keyword_matches = sum(
            1 for keyword in keywords if keyword in headline_text)
        keyword_score = keyword_matches / \
            max(len(keywords), 1) if keywords else 0

        # Structure matching (length, caps, etc.)
        structure_score = 0
        if headline_structure:
            current_structure = self._analyze_headline_structure(headline_text)

            # Compare key structural elements
            if abs(
                current_structure.get(
                    'word_count',
                    0) -
                headline_structure.get(
                    'word_count',
                    0)) <= 3:
                structure_score += 0.2
            if current_structure.get(
                    'has_caps') == headline_structure.get('has_caps'):
                structure_score += 0.2
            if current_structure.get(
                    'urgency_indicators',
                    0) > 0 and headline_structure.get(
                    'urgency_indicators',
                    0) > 0:
                structure_score += 0.4

        # Pattern matches if keyword similarity > 60% or structure + some
        # keywords match
        return keyword_score > 0.6 or (
            keyword_score > 0.3 and structure_score > 0.4)

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
                if self._pattern_matches_current(
                        pattern, headlines, economic_data):
                    boost += effectiveness * confidence
            except BaseException:
                continue

        return min(boost, 2)  # Cap the boost

    def _pattern_matches_current(self, pattern, headlines, economic_data):
        """Check if stored pattern matches current situation"""
        # Simple pattern matching - can be enhanced
        pattern_keywords = pattern.get('keywords', [])
        current_text = ' '.join([h.get('title', '')
                                for h in headlines]).lower()

        matches = sum(
            1 for keyword in pattern_keywords if keyword in current_text)
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
    intelligence = AdaptiveIntelligence()

    def smart_assess_urgency(headlines, economic_data):
        return intelligence.predict_trend_urgency(headlines, economic_data)

    return smart_assess_urgency


if __name__ == "__main__":
    # Test the intelligence system
    intelligence = AdaptiveIntelligence()
    print(intelligence.get_intelligence_report())
