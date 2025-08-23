#!/usr/bin/env python3
"""
A/B Testing Framework for Canary Protocol Prompts
Compare different prompt approaches and measure effectiveness
"""

from openai import OpenAI
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('config/.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class PromptVariant:
    def __init__(self, name, system_prompt, temperature=0.2, max_tokens=3000):
        self.name = name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.results = []


class ABTestRunner:
    def __init__(self):
        self.variants = {}
        self.test_data = []

    def add_variant(self, variant):
        """Add a prompt variant to test"""
        self.variants[variant.name] = variant

    def add_test_case(
            self,
            headlines,
            economic_data,
            urgency_level,
            expected_characteristics=None):
        """Add test data for evaluation"""
        self.test_data.append({
            "headlines": headlines,
            "economic_data": economic_data,
            "urgency_level": urgency_level,
            "expected": expected_characteristics or {}
        })

    def run_test(self, variant_name, test_case, user_prompt):
        """Run a single test with one variant"""
        variant = self.variants[variant_name]

        try:
            start_time = time.time()

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": variant.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=variant.temperature,
                max_tokens=variant.max_tokens
            )

            end_time = time.time()

            result = {
                "response": response.choices[0].message.content,
                "response_time": end_time - start_time,
                "tokens_used": response.usage.total_tokens,
                "test_case": test_case,
                "timestamp": datetime.now().isoformat()
            }

            variant.results.append(result)
            return result

        except Exception as e:
            return {"error": str(e), "variant": variant_name}

    def evaluate_response(self, response_text, expected_characteristics):
        """Evaluate response quality based on criteria"""
        score = 0
        feedback = []

        # Word count compliance
        word_count = len(response_text.split())
        if 800 <= word_count <= 1200:  # Target range
            score += 20
            feedback.append("✅ Appropriate length")
        else:
            feedback.append(
                f"⚠️ Length: {word_count} words (target: 800-1200)")

        # Section structure
        required_sections = [
            "POLITICAL & INSTITUTIONAL",
            "ECONOMIC STABILITY",
            "SAFETY ASSESSMENT",
            "TREND ANALYSIS",
            "KEY TAKEAWAYS"
        ]

        sections_found = sum(
            1 for section in required_sections if section in response_text)
        score += (sections_found / len(required_sections)) * 20
        feedback.append(
            f"📋 Sections: {sections_found}/{len(required_sections)}")

        # Link formatting
        link_count = response_text.count("**[") + response_text.count("](")
        if link_count >= 4:  # At least 2 proper markdown links
            score += 15
            feedback.append("✅ Good source linking")
        else:
            feedback.append("⚠️ Insufficient source links")

        # Specific metrics/numbers
        import re
        numbers = len(
            re.findall(
                r'\d+(?:\.\d+)?%|\$[\d,]+|\d+(?:,\d+)*',
                response_text))
        if numbers >= 5:
            score += 15
            feedback.append("✅ Good quantitative detail")
        else:
            feedback.append("⚠️ Needs more specific metrics")

        # Safety status symbols
        status_symbols = response_text.count(
            "🟢") + response_text.count("🟠") + response_text.count("🔴")
        if status_symbols >= 4:  # One for each group
            score += 15
            feedback.append("✅ Safety assessments complete")
        else:
            feedback.append("⚠️ Missing safety status indicators")

        # Avoid problematic language
        problematic_terms = [
            "collapse",
            "chaos",
            "catastrophic",
            "civil war",
            "apocalypse"]
        problematic_found = sum(
            1 for term in problematic_terms if term.lower() in response_text.lower())
        if problematic_found == 0:
            score += 15
            feedback.append("✅ Professional tone maintained")
        else:
            score -= problematic_found * 5
            feedback.append(f"⚠️ Found {problematic_found} problematic terms")

        return {
            "score": max(0, min(100, score)),
            "feedback": feedback,
            "word_count": word_count,
            "sections_found": sections_found,
            "link_count": link_count // 2,  # Divide by 2 since each link has 2 parts
            "numbers_found": numbers,
            "status_symbols": status_symbols
        }

    def run_full_test(self):
        """Run all variants against all test cases"""
        print("🧪 STARTING A/B TEST")
        print("=" * 50)

        results_summary = {}

        for test_idx, test_case in enumerate(self.test_data):
            print(f"\nTest Case {test_idx + 1}/{len(self.test_data)}")
            print("-" * 30)

            # Create user prompt for this test case
            headlines_text = "\n".join(
                [f"{h['title']} - {h['url']}" for h in test_case["headlines"]])
            economic_context = ""
            if test_case["economic_data"]:
                high_concern = [
                    e for e in test_case["economic_data"] if e.get('concern_level') == 'high']
                if high_concern:
                    economic_context = f"\n\nEconomic concerns: {
                        ', '.join(
                            [
                                e['indicator'] + ': ' + e['status'] for e in high_concern])}"

            user_prompt = f"""Current urgency level: {
                test_case['urgency_level']}
Economic context: {economic_context}

Headlines to analyze:
{headlines_text}"""

            for variant_name in self.variants:
                print(f"Testing {variant_name}...")
                result = self.run_test(variant_name, test_case, user_prompt)

                if "error" not in result:
                    evaluation = self.evaluate_response(
                        result["response"], test_case.get("expected", {}))
                    result["evaluation"] = evaluation

                    if variant_name not in results_summary:
                        results_summary[variant_name] = []
                    results_summary[variant_name].append(evaluation)

                    print(f"  Score: {evaluation['score']}/100")
                else:
                    print(f"  Error: {result['error']}")

                time.sleep(1)  # Rate limiting

        return self.generate_report(results_summary)

    def generate_report(self, results_summary):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 A/B TEST RESULTS REPORT")
        print("=" * 60)

        for variant_name, evaluations in results_summary.items():
            if not evaluations:
                continue

            scores = [e["score"] for e in evaluations]
            avg_score = sum(scores) / len(scores)

            print(f"\n🔬 VARIANT: {variant_name}")
            print(f"Average Score: {avg_score:.1f}/100")
            print(f"Score Range: {min(scores)}-{max(scores)}")

            # Aggregate metrics
            avg_word_count = sum(e["word_count"]
                                 for e in evaluations) / len(evaluations)
            avg_sections = sum(e["sections_found"]
                               for e in evaluations) / len(evaluations)
            avg_links = sum(e["link_count"]
                            for e in evaluations) / len(evaluations)

            print(f"Avg Word Count: {avg_word_count:.0f}")
            print(f"Avg Sections: {avg_sections:.1f}/5")
            print(f"Avg Links: {avg_links:.1f}")

            # Common feedback
            all_feedback = []
            for evaluation in evaluations:
                all_feedback.extend(evaluation["feedback"])

            positive_feedback = [f for f in all_feedback if f.startswith("✅")]
            warning_feedback = [f for f in all_feedback if f.startswith("⚠️")]

            print(
                f"Positive: {
                    len(positive_feedback)} | Warnings: {
                    len(warning_feedback)}")

        # Determine winner
        if results_summary:
            best_variant = max(results_summary.keys(), key=lambda v: sum(
                e["score"] for e in results_summary[v]) / len(results_summary[v]))
            print(f"\n🏆 WINNING VARIANT: {best_variant}")
        else:
            best_variant = "No successful tests"
            print(f"\n❌ NO SUCCESSFUL TESTS COMPLETED")

        return {
            "winner": best_variant,
            "results": results_summary,
            "timestamp": datetime.now().isoformat()
        }


def create_test_variants():
    """Create different prompt variants for testing"""

    variants = []

    # Current enhanced prompt
    current_prompt = """You are an expert political and economic analyst with 20+ years experience monitoring U.S. stability. You provide objective, factual analysis for informed citizens. Your assessments are measured, evidence-based, and actionable."""

    variants.append(PromptVariant(
        name="current_enhanced",
        system_prompt=current_prompt,
        temperature=0.2,
        max_tokens=3000
    ))

    # More structured variant
    structured_prompt = """You are a senior intelligence analyst specializing in domestic stability assessment. Your role is to provide precise, quantified analysis for decision-makers.

ANALYSIS REQUIREMENTS:
- Include specific numbers, percentages, and dates
- Cite authoritative sources with proper attribution
- Maintain professional, non-alarmist tone
- Focus on actionable intelligence over opinion
- Distinguish facts from reasonable inferences"""

    variants.append(PromptVariant(
        name="structured_analyst",
        system_prompt=structured_prompt,
        temperature=0.15,
        max_tokens=3000
    ))

    # Concise variant
    concise_prompt = """You are a political risk analyst providing weekly intelligence briefings. Focus on key developments affecting U.S. stability. Be factual, specific, and concise."""

    variants.append(PromptVariant(
        name="concise_briefer",
        system_prompt=concise_prompt,
        temperature=0.25,
        max_tokens=2500
    ))

    return variants


def setup_test_data():
    """Create sample test data"""
    return [
        {
            "headlines": [
                {"title": "Supreme Court Reviews Voting Rights Case", "url": "https://example.com/1"},
                {"title": "Fed Raises Rates 0.25% Amid Inflation Concerns", "url": "https://example.com/2"},
                {"title": "State Legislature Passes Education Reform Bill", "url": "https://example.com/3"}
            ],
            "economic_data": [
                {"indicator": "VIX", "value": "25.3", "status": "ELEVATED", "concern_level": "medium"}
            ],
            "urgency_level": "MEDIUM",
            "expected_characteristics": {"min_word_count": 800, "sections": 5}
        }
    ]


if __name__ == "__main__":
    import sys

    print("🧪 CANARY PROTOCOL A/B TESTING")
    print("=" * 50)

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input(
            "Run: (1) Quick test, (2) Full analysis, (3) Setup only: ")

    tester = ABTestRunner()

    # Add variants
    for variant in create_test_variants():
        tester.add_variant(variant)

    # Add test data
    for test_case in setup_test_data():
        tester.add_test_case(**test_case)

    if choice in ["1", "2"]:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found in environment")
        else:
            print(
                "⚠️  A/B testing requires OpenAI API calls and may use significant credits")
            print(
                "🧪 This is a demonstration framework - customize test cases for production use")

            if choice == "1":
                print("📝 Quick test shows framework capabilities without full execution")
                print("✅ A/B testing framework ready for customization")
            else:
                print("🚀 Running full A/B test analysis...")
                report = tester.run_full_test()

                # Save detailed report
                with open(f"ab_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                    json.dump(report, f, indent=2)
                print("\n💾 Detailed report saved to file")

    print("\n✅ A/B testing framework ready!")
    print("💡 Add more variants and test cases to improve analysis quality")
