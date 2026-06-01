"""
Sample Data Generator for Therapeutic Companion.

This script generates sample therapeutic data in CSV and JSON formats
to help test the ingestion and RAG pipeline.

Run this to populate ./dataa/ with sample therapeutic exchanges.

Usage:
    python generate_sample_data.py
"""

import json
import csv
from pathlib import Path


SAMPLE_CSV_DATA = [
    {
        "instruction": "I'm feeling anxious about an upcoming presentation at work",
        "response": "Anxiety about presentations is very common. Let's break this down together. First, tell me more about what specifically makes you anxious. Is it the audience, the content, or something else? Once we identify the core concern, we can work through some grounding techniques."
    },
    {
        "instruction": "How can I manage stress in my daily life?",
        "response": "Great question. Research shows several evidence-based techniques help with daily stress management. Try starting with the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. This brings you to the present moment. Also consider brief walks, deep breathing, or short meditation sessions."
    },
    {
        "instruction": "I feel like I'm not good enough and I keep comparing myself to others",
        "response": "Social comparison is something many people struggle with. Let's gently challenge this. First, recognize that social media and comparisons often show only highlight reels, not full reality. Second, what matters is your own growth and values, not how you measure against others. What are your personal strengths that you might be overlooking?"
    },
    {
        "instruction": "I've been having trouble sleeping lately and it's affecting my mood",
        "response": "Sleep and mood are deeply connected. Let's address this together. First, establish a consistent sleep schedule. Try to go to bed and wake up at the same time daily. Avoid screens 30-60 minutes before bed. Consider the 4-7-8 breathing technique: breathe in for 4 counts, hold for 7, exhale for 8. This activates your parasympathetic nervous system. If it persists, talk to a healthcare provider."
    },
    {
        "instruction": "How do I handle rejection without feeling devastated?",
        "response": "Rejection is painful, and your feelings are valid. Here's a reframe that might help: rejection of one aspect doesn't mean rejection of your entire self. It's often about fit or timing, not your worth. Practice self-compassion. Treat yourself like a good friend would. Then, reflect on what you learned. Many successful people have experienced significant rejection. It's part of growth."
    },
    {
        "instruction": "I struggle with perfectionism and it's paralyzing me",
        "response": "Perfectionism often stems from anxiety or past experiences. Let's reframe this. Perfect doesn't exist—progress does. Try setting 'good enough' standards instead of perfect ones. Break tasks into smaller, manageable steps. Celebrate completing steps rather than waiting for perfection. Notice when perfectionism prevents action, and gently redirect toward 'done is better than perfect.'"
    },
    {
        "instruction": "I feel overwhelmed by too many responsibilities",
        "response": "Overwhelm is a signal that something needs to change. Let's simplify. First, list everything on your plate. Then, categorize by urgency and importance using the Eisenhower Matrix. Some things can be delegated, postponed, or let go. Remember, saying no to some things means saying yes to your wellbeing. What's one thing you could remove or postpone?"
    },
    {
        "instruction": "How do I process difficult emotions without suppressing them?",
        "response": "That's a healthy instinct. Suppressing emotions often makes them stronger. Instead, try this: acknowledge the emotion without judgment. Say 'I'm feeling anger/sadness/fear' rather than judging yourself for it. Sit with it briefly. Ask yourself what it's trying to tell you. Then decide on action. Journaling, talking to someone, or moving your body can help process emotions."
    },
    {
        "instruction": "I feel disconnected from people even when I'm with them",
        "response": "That disconnection often signals emotional exhaustion or a mismatch in relationships. Let's explore: Do these relationships align with your values? Are you being authentic, or performing a role? Sometimes we need to invest in deeper connections by being more vulnerable. Try sharing something real with someone safe. Quality matters more than quantity in relationships."
    },
    {
        "instruction": "How can I build more confidence in myself?",
        "response": "Confidence grows through small victories. Start by identifying past challenges you've overcome—you're stronger than you think. Then, take small actions outside your comfort zone. Each time you do something despite fear, your confidence grows. Also, practice positive self-talk. Notice your inner critic and gently redirect to encouragement. Self-compassion is the foundation of genuine confidence."
    }
]

SAMPLE_JSON_DATA = [
    {
        "context": "User experiencing social anxiety",
        "response": "Social anxiety is your mind trying to protect you, but it's being overprotective. Remember, most people are focused on themselves, not judging you. Try one small social interaction today. Notice what actually happens versus what you feared. Often, reality is much better than our anxious predictions."
    },
    {
        "context": "User struggling with self-worth",
        "response": "Your worth is inherent, not earned through achievements. You don't need to 'deserve' love and respect—you already have it as a human being. When your inner critic gets loud, pause and ask: Would I talk to a friend this way? Likely not. Extend that same kindness to yourself."
    },
    {
        "context": "User feeling lonely and isolated",
        "response": "Loneliness is painful, and reaching out is brave. Remember that connection doesn't need to be perfect to be meaningful. Start with one person—maybe a quick text or call. Vulnerability invites connection. Also consider communities around your interests. You're not alone, even when it feels that way."
    },
    {
        "context": "User experiencing grief",
        "response": "Grief isn't something to 'get over'—it's something to integrate. There's no timeline. Some days will be harder than others, and that's okay. Honor your feelings by journaling, talking, or creating something. Consider how this person or loss changed you. Grief is a reflection of love."
    },
    {
        "context": "User struggling with work-life balance",
        "response": "Balance isn't about perfect 50/50 splits; it's about alignment with your values. What matters most to you right now? Use that to make decisions about your time and energy. Setting boundaries isn't selfish—it's essential. Your wellbeing fuels your ability to show up for others."
    },
    {
        "context": "User feeling unmotivated and stuck",
        "response": "Stuck feeling often signals a need for change or rest. First, check: Are you physically taking care of yourself? Sleep, movement, and nutrition significantly impact motivation. If basics are covered, maybe something needs to change—your environment, goals, or approach. Small changes create momentum."
    },
    {
        "context": "User dealing with intrusive thoughts",
        "response": "Intrusive thoughts are your brain trying to problem-solve, often about things you care about. They're not predictions or desires. The more you fight them, the stronger they become. Instead, notice them like clouds passing in the sky. 'I'm having the thought that...' then let it pass. Acceptance paradoxically reduces their power."
    },
    {
        "context": "User processing past trauma",
        "response": "Healing from trauma takes time, and what you're feeling is a normal response to abnormal events. Consider professional trauma-informed therapy (EMDR, CPT, or Somatic Experiencing). In the meantime, grounding techniques help: notice 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste. Safety comes first."
    },
    {
        "context": "User experiencing imposter syndrome",
        "response": "Imposter syndrome is common among high achievers. Here's the truth: you earned your position. Your accomplishments are real. Imposter feelings don't make you a fraud—they often mean you care about excellence. Name two recent achievements where you added value. You belong here."
    },
    {
        "context": "User in relationship conflict",
        "response": "Conflict is normal in relationships. What matters is how you handle it. Try this: Use 'I' statements: 'I felt hurt when...' rather than 'You always...' Listen to understand, not to win. Take breaks if things escalate. Sometimes a third party (therapist) helps. Strong relationships weather storms."
    }
]


def generate_sample_csv():
    """Generate sample therapeutic data in CSV format."""
    output_path = Path("./dataa/sample_therapeutic_conversations.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['instruction', 'response'])
        writer.writeheader()
        writer.writerows(SAMPLE_CSV_DATA)

    print(f"✅ Created {output_path} with {len(SAMPLE_CSV_DATA)} entries")


def generate_sample_json():
    """Generate sample therapeutic data in JSON format."""
    output_path = Path("./dataa/sample_therapeutic_responses.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_JSON_DATA, f, indent=2, ensure_ascii=False)

    print(f"✅ Created {output_path} with {len(SAMPLE_JSON_DATA)} entries")


def main():
    """Generate all sample data."""
    print("=" * 80)
    print("GENERATING SAMPLE THERAPEUTIC DATA")
    print("=" * 80)

    generate_sample_csv()
    generate_sample_json()

    print("\n" + "=" * 80)
    print("SAMPLE DATA READY")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run: python ingest.py")
    print("2. Start app: streamlit run app.py")
    print("3. Test chat with therapeutic questions")
    print("\nYou can add more data files to ./dataa/ and re-run ingest.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
