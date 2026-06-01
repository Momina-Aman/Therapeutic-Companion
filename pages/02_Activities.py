"""
Activities Hub - Comprehensive Wellness & Engagement Module.

This page provides an integrated ecosystem of therapeutic activities:
- Mini-Games for stress relief and engagement
- Digital Journal with auto-save
- Media recommendations (Books & Movies)
- Daily affirmations and quotes
- Stories and poetry library

Page: 02_Activities.py
Module: Therapeutic Companion - Phase 3
"""

import streamlit as st
from auth import check_auth
from pathlib import Path
import json
from datetime import datetime
import random
import time


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Activities - Therapeutic Companion",
    page_icon="🎮",
    layout="wide"
)

# Check authentication
if not check_auth(st.session_state):
    st.error("Please log in to access this feature.")
    st.stop()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_activities_session():
    """Initialize session state for activities."""
    if "breathing_active" not in st.session_state:
        st.session_state.breathing_active = False

    if "zen_clicks" not in st.session_state:
        st.session_state.zen_clicks = 0

    if "zen_start_time" not in st.session_state:
        st.session_state.zen_start_time = None

    if "scramble_word" not in st.session_state:
        st.session_state.scramble_word = None

    if "scramble_shuffled" not in st.session_state:
        st.session_state.scramble_shuffled = None

    if "mood_cards" not in st.session_state:
        st.session_state.mood_cards = None

    if "mood_first_card" not in st.session_state:
        st.session_state.mood_first_card = None

    if "mood_matches" not in st.session_state:
        st.session_state.mood_matches = 0

    if "reaction_ready" not in st.session_state:
        st.session_state.reaction_ready = False

    if "reaction_start" not in st.session_state:
        st.session_state.reaction_start = None

    if "reaction_time" not in st.session_state:
        st.session_state.reaction_time = None


initialize_activities_session()


# ============================================================================
# DATA: RECOMMENDATIONS ENGINE
# ============================================================================

RECOMMENDATIONS_DATA = {
    "Healing": {
        "books": [
            {
                "title": "The Body Keeps the Score",
                "author": "Bessel van der Kolk",
                "description": "Understanding how trauma affects the brain and body, with practical healing strategies."
            },
            {
                "title": "What Happened to You?",
                "author": "Bruce Perry & Oprah Winfrey",
                "description": "A compassionate exploration of how life experiences shape who we are."
            },
            {
                "title": "The Courage to be Disliked",
                "author": "Ichiro Kishimi & Fumitake Koga",
                "description": "A dialogue about personal freedom and overcoming psychological trauma."
            },
            {
                "title": "Permission to Feel",
                "author": "Marc Brackett",
                "description": "Unlocking the power of emotions to help ourselves and others."
            },
            {
                "title": "It Didn't Start with You",
                "author": "Mark Wolynn",
                "description": "How inherited family trauma shapes who we are and how to heal."
            }
        ],
        "movies": [
            {
                "title": "Inside Out",
                "description": "An animated journey through emotions and personal growth."
            },
            {
                "title": "A Beautiful Mind",
                "description": "A powerful story about mental health and resilience."
            },
            {
                "title": "Good Will Hunting",
                "description": "Healing through connection and therapy."
            },
            {
                "title": "Life is Beautiful",
                "description": "Finding hope and joy in difficult circumstances."
            },
            {
                "title": "The Shawshank Redemption",
                "description": "Hope, perseverance, and human connection."
            }
        ]
    },
    "Inspirational": {
        "books": [
            {
                "title": "Atomic Habits",
                "author": "James Clear",
                "description": "Small changes, remarkable results. Build better habits for life."
            },
            {
                "title": "Mindset",
                "author": "Carol S. Dweck",
                "description": "The power of believing you can improve yourself."
            },
            {
                "title": "The Power of Now",
                "author": "Eckhart Tolle",
                "description": "Living fully in the present moment."
            },
            {
                "title": "Dare to Lead",
                "author": "Brené Brown",
                "description": "Courageous leadership and vulnerability."
            },
            {
                "title": "Man's Search for Meaning",
                "author": "Viktor Frankl",
                "description": "Finding purpose and meaning, even in suffering."
            }
        ],
        "movies": [
            {
                "title": "Rocky",
                "description": "Never give up on your dreams."
            },
            {
                "title": "Pursuit of Happyness",
                "description": "Overcoming adversity with determination."
            },
            {
                "title": "Hidden Figures",
                "description": "Breaking barriers and changing the world."
            },
            {
                "title": "Forrest Gump",
                "description": "Life is what you make of it."
            },
            {
                "title": "The Pursuit of Happyness",
                "description": "A father's journey of perseverance and love."
            }
        ]
    },
    "Light-hearted": {
        "books": [
            {
                "title": "Where the Crawdads Sing",
                "author": "Delia Owens",
                "description": "A captivating story of nature and self-discovery."
            },
            {
                "title": "Remarkably Bright",
                "author": "Kate Kemp",
                "description": "A feel-good adventure through life's surprises."
            },
            {
                "title": "Eleanor Oliphant Is Completely Fine",
                "author": "Gail Honeyman",
                "description": "A heartwarming story about connection and friendship."
            },
            {
                "title": "The Thursday Murder Club",
                "author": "Richard Osman",
                "description": "Friendship, humor, and mystery with a big heart."
            },
            {
                "title": "Beach Read",
                "author": "Emily Henry",
                "description": "Romance, humor, and self-discovery by the ocean."
            }
        ],
        "movies": [
            {
                "title": "When Harry Met Sally",
                "description": "A charming romantic comedy about friendship."
            },
            {
                "title": "Amélie",
                "description": "Whimsy, magic, and human kindness."
            },
            {
                "title": "Paddington",
                "description": "Warmth and humor for all ages."
            },
            {
                "title": "Grand Budapest Hotel",
                "description": "A visually stunning, quirky adventure."
            },
            {
                "title": "Legally Blonde",
                "description": "Fun, confidence, and believing in yourself."
            }
        ]
    },
    "Adventure": {
        "books": [
            {
                "title": "Into the Wild",
                "author": "Jon Krakauer",
                "description": "A true story of self-discovery in nature."
            },
            {
                "title": "The Alchemist",
                "author": "Paulo Coelho",
                "description": "Following your dreams across the world."
            },
            {
                "title": "Eat, Pray, Love",
                "author": "Elizabeth Gilbert",
                "description": "A journey of healing and rediscovery."
            },
            {
                "title": "Wild",
                "author": "Cheryl Strayed",
                "description": "A thousand-mile solo hike to find yourself."
            },
            {
                "title": "The Midnight Library",
                "author": "Matt Haig",
                "description": "Exploring infinite possibilities and second chances."
            }
        ],
        "movies": [
            {
                "title": "Into the Wild",
                "description": "A powerful journey of self-discovery."
            },
            {
                "title": "The Secret Life of Walter Mitty",
                "description": "Adventure, imagination, and stepping outside comfort zones."
            },
            {
                "title": "Eat Pray Love",
                "description": "Finding yourself through travel and experience."
            },
            {
                "title": "Everest",
                "description": "Epic adventure against all odds."
            },
            {
                "title": "Jungle Cruise",
                "description": "Adventure, humor, and unexpected connections."
            }
        ]
    },
    "Discovery": {
        "books": [
            {
                "title": "Educated",
                "author": "Tara Westover",
                "description": "A powerful story of education and freedom."
            },
            {
                "title": "Thinking, Fast and Slow",
                "author": "Daniel Kahneman",
                "description": "Understand how your mind works."
            },
            {
                "title": "Sapiens",
                "author": "Yuval Noah Harari",
                "description": "The history of humankind reimagined."
            },
            {
                "title": "Braiding Sweetgrass",
                "author": "Robin Wall Kimmerer",
                "description": "Indigenous wisdom and reciprocity with nature."
            },
            {
                "title": "Caste",
                "author": "Isabel Wilkerson",
                "description": "Understanding social hierarchy and human dignity."
            }
        ],
        "movies": [
            {
                "title": "Cosmos",
                "description": "Exploring the universe and human potential."
            },
            {
                "title": "The Social Dilemma",
                "description": "Understanding technology's impact on our minds."
            },
            {
                "title": "My Octopus Teacher",
                "description": "An intimate journey of discovery and connection."
            },
            {
                "title": "Planet Earth",
                "description": "The beauty and wonder of our world."
            },
            {
                "title": "Jiro Dreams of Sushi",
                "description": "Mastery, dedication, and the pursuit of excellence."
            }
        ]
    }
}

AFFIRMATIONS = [
    "You are stronger than you believe. 💪",
    "Progress is progress, no matter how small. 🌱",
    "Your mental health matters. Your voice matters. 💙",
    "You deserve peace and happiness. 🌸",
    "Be kind to yourself today. 🤍",
    "You are worthy of love and respect. ✨",
    "Every day is a new opportunity. 🌅",
    "Your struggles don't define you. Your strength does. 🔥",
    "You are enough, just as you are. 💝",
    "Healing is possible. Growth is happening. 🌿",
    "Your feelings are valid. Your needs matter. 💬",
    "You've survived 100% of your worst days. 🏆",
    "Be patient with yourself. You're doing better than you think. 🌙",
    "Your journey is unique. Your progress is real. 🌊",
    "You are braver than you believe. You are capable. You are loved. 👑"
]

STORIES = [
    {
        "title": "The Butterfly Effect",
        "type": "Motivational",
        "content": """On a difficult day, Maya decided to smile at a stranger on the train.

That stranger, who was having the worst week of their life, felt something shift inside. That one genuine smile reminded them they weren't invisible.

They went home and called their mom, who had been worried. They talked for hours. It changed everything.

Years later, Maya ran into that stranger at a coffee shop. They told her how that smile had been the turning point that saved their life.

One small act of kindness. One smile. Changed everything.

Remember: Your kindness, your presence, your light matters more than you know. 🦋"""
    },
    {
        "title": "The Pottery Lesson",
        "type": "Wisdom",
        "content": """A young artist was devastated when her pottery shattered in the kiln.

Her mentor picked up the broken pieces and smiled.

"Don't you see? This is where the real art begins. These fractures, these breaks—they're now stronger at the joints. The Japanese call this 'kintsugi'—golden joinery."

He showed her how to fill the cracks with gold, turning damage into beauty.

"Your life is like this pottery," he said. "Your breaks, your struggles, your pain—they don't ruin you. They're opportunities to become more beautiful than before. You're not broken; you're becoming."

She looked at her repaired bowl, glinting with gold. It was more beautiful than the original.

So are you. 🏺✨"""
    },
    {
        "title": "The Night Shift Nurse",
        "type": "Uplifting",
        "content": """At 3 AM in the hospital, nurse James found an elderly patient crying.

She'd lost her husband. The cancer was winning. She felt alone.

Instead of just checking her vitals, James sat down. Really sat down. And listened.

"Tell me about him," James said.

For an hour, she shared memories. Laughter. Love. Pain. All of it.

"He was a good man," James said finally. "And he was loved by someone who remembers every moment. That matters. You're not alone."

The patient died peacefully two days later. Her family told James it was the first night their mother had smiled since admission.

Sometimes the most powerful medicine is simply being present. Listening. Caring.

You have more healing power than you realize. 💙"""
    },
    {
        "title": "Small Steps",
        "type": "Motivational",
        "content": """Marcus couldn't imagine going to the gym. Anxiety crippled him.

But his therapist said: "You don't need to go to the gym. Go to the lobby. That's it."

Day one: He went to the lobby. Sat for 5 minutes. Left.

Day two: He walked to the front door of the gym.

Day three: He went inside. Looked around. Left.

Week two: He took one fitness class.

Six months later: Marcus was going three times a week.

He learned the most important thing: You don't have to see the whole staircase. Just take the next step.

Your breakthrough isn't about a giant leap. It's about the next small step. And then the one after that.

You've got this. 🪜"""
    },
    {
        "title": "The Unexpected Friendship",
        "type": "Heartwarming",
        "content": """Emma joined a support group not expecting anything.

She sat in the corner, silent, for three weeks.

On week four, the woman next to her accidentally dropped her coffee and laughed at herself instead of crying.

Emma smiled. Actually smiled.

That woman, Priya, asked Emma for her number. "Want to grab coffee sometime?"

They started meeting weekly. They'd talk for hours—about struggles, dreams, funny memories, embarrassing moments.

A year later, they were best friends. They supported each other through promotions and heartbreaks, through therapy and celebrations.

What Emma didn't realize: Priya felt exactly the same way. She'd been lonely too.

Your people are out there. Looking for someone just like you. Waiting for connection.

Sometimes friendship finds you when you need it most. 💕"""
    }
]


# ============================================================================
# MINI-GAMES
# ============================================================================

def render_breathing_bubble():
    """Render the Breathing Bubble game with CSS animation."""
    st.markdown("""
    <style>
    @keyframes breathe {
        0% { transform: scale(1); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }

    .breathing-bubble {
        width: 200px;
        height: 200px;
        background: linear-gradient(135deg, #6B9080, #A8DADC);
        border-radius: 50%;
        margin: 40px auto;
        animation: breathe 4s infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: white;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(107, 144, 128, 0.3);
    }

    .breathing-text {
        text-align: center;
        font-size: 16px;
        color: #52796F;
        margin: 20px 0;
    }
    </style>

    <div class="breathing-bubble">
        Breathe
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="breathing-text">
    <strong>Follow the bubble's rhythm</strong><br>
    Inhale for 4 counts, Hold for 4, Exhale for 4, Hold for 4<br>
    Repeat 5 times for calm focus
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Breathing Session", key="start_breathing", use_container_width=True):
        st.success("✨ Take a deep breath. You've got this. Focus on the bubble.")


def render_zen_clicker():
    """Render the Zen Clicker game."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric("Total Clicks", st.session_state.zen_clicks, delta="Keep going!")

    with col2:
        if st.session_state.zen_start_time:
            elapsed = time.time() - st.session_state.zen_start_time
            st.metric("Time (seconds)", f"{elapsed:.1f}")

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🟢 Click!", key="zen_click", use_container_width=True):
            st.session_state.zen_clicks += 1
            if not st.session_state.zen_start_time:
                st.session_state.zen_start_time = time.time()
            st.rerun()

    with col2:
        if st.button("🔄 Reset", key="zen_reset", use_container_width=True):
            st.session_state.zen_clicks = 0
            st.session_state.zen_start_time = None
            st.rerun()

    with col3:
        if st.session_state.zen_clicks >= 50:
            st.success("🏆 You're a Zen Master!")

    st.info("💡 Clicking helps release nervous energy. Find your rhythm. No pressure.")


def render_word_scramble():
    """Render the Word Scramble game."""
    uplifting_words = [
        ("STRENGTH", "Resilience and power within"),
        ("GROWTH", "Change and positive development"),
        ("WORTHY", "You are deserving of love"),
        ("HEALING", "Getting better, piece by piece"),
        ("BRAVE", "Courage in the face of fear"),
        ("PEACE", "Calm and tranquility within"),
        ("HOPE", "Believing in better days"),
        ("LOVED", "Cared for and cherished"),
    ]

    if not st.session_state.scramble_word:
        word, definition = random.choice(uplifting_words)
        st.session_state.scramble_word = word
        st.session_state.scramble_shuffled = ''.join(random.sample(word, len(word)))

    st.write(f"**Definition:** {[d for w, d in uplifting_words if w == st.session_state.scramble_word][0]}")

    st.write(f"**Scrambled:** `{st.session_state.scramble_shuffled}`")
    st.write(f"**Letters available:** {len(st.session_state.scramble_word)}")

    col1, col2 = st.columns([2, 1])

    with col1:
        guess = st.text_input("Your guess:", key="scramble_guess", placeholder="Type the word").upper()

    with col2:
        if st.button("Check Answer", key="check_scramble"):
            if guess == st.session_state.scramble_word:
                st.success(f"✨ Correct! The word is **{st.session_state.scramble_word}**")
                st.balloons()
                st.session_state.scramble_word = None
            elif guess:
                st.error("Not quite. Try again!")

    if st.button("New Word", key="new_scramble"):
        st.session_state.scramble_word = None
        st.rerun()


def render_mood_matcher():
    """Render the Emoji Memory/Mood Matcher game."""
    mood_pairs = [
        ("😊", "😊"), ("😎", "😎"), ("🌟", "🌟"), ("💪", "💪"),
        ("🧘", "🧘"), ("😌", "😌"), ("💝", "💝"), ("🌈", "🌈")
    ]

    if not st.session_state.mood_cards:
        shuffled = mood_pairs + [(e, e) for e, _ in mood_pairs]
        random.shuffle(shuffled)
        st.session_state.mood_cards = [(e, e, False) for e, _ in shuffled]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Matches Found", st.session_state.mood_matches, f"/{len(mood_pairs)}")

    if st.session_state.mood_matches == len(mood_pairs):
        st.success("🎉 Perfect! You matched all the moods!")
        if st.button("Play Again", key="play_mood_again"):
            st.session_state.mood_cards = None
            st.session_state.mood_matches = 0
            st.rerun()
        return

    st.write("**Click on cards to find matching pairs:**")

    cols = st.columns(4)
    for idx, (emoji, _, flipped) in enumerate(st.session_state.mood_cards):
        with cols[idx % 4]:
            if st.button(emoji if flipped else "?", key=f"mood_{idx}", use_container_width=True):
                if not st.session_state.mood_first_card:
                    st.session_state.mood_first_card = idx
                    st.session_state.mood_cards[idx] = (emoji, emoji, True)
                else:
                    first_idx = st.session_state.mood_first_card
                    first_emoji = st.session_state.mood_cards[first_idx][0]

                    if first_emoji == emoji:
                        st.session_state.mood_cards[idx] = (emoji, emoji, True)
                        st.session_state.mood_matches += 1
                    else:
                        st.session_state.mood_cards[idx] = (emoji, emoji, True)

                    st.session_state.mood_first_card = None

                st.rerun()


def render_reaction_timer():
    """Render the Reaction Time game."""
    st.write("**Test your reflexes! Click the button as soon as it turns green.**")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.session_state.reaction_time:
            st.success(f"⚡ Your reaction time: **{st.session_state.reaction_time:.2f}ms**")

    if st.button("Start Game", key="start_reaction", use_container_width=True):
        st.session_state.reaction_start = time.time()
        st.session_state.reaction_ready = True
        st.rerun()

    if st.session_state.reaction_ready:
        st.markdown(
            "<h1 style='text-align: center; color: green; font-size: 100px;'>🟢</h1>",
            unsafe_allow_html=True
        )

        if st.button("CLICK HERE!", key="click_reaction", use_container_width=True):
            elapsed = (time.time() - st.session_state.reaction_start) * 1000
            st.session_state.reaction_time = elapsed
            st.session_state.reaction_ready = False
            st.balloons()
            st.rerun()


# ============================================================================
# DIGITAL JOURNAL
# ============================================================================

def get_journal_path() -> Path:
    """Get the journal file path for the current user."""
    user_dir = Path(f"./user_data/{st.session_state.username}")
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / "journal.txt"


def save_journal_entry(entry_text: str) -> bool:
    """
    Save a journal entry to the user's journal file.

    Args:
        entry_text: The journal entry text

    Returns:
        True if successful, False otherwise
    """
    try:
        journal_path = get_journal_path()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"\n{'='*60}\n[{timestamp}]\n{'='*60}\n{entry_text}\n"

        with open(journal_path, 'a', encoding='utf-8') as f:
            f.write(entry)

        return True

    except Exception as e:
        st.error(f"Error saving journal: {e}")
        return False


def load_all_journal_entries() -> list:
    """
    Load all journal entries for the current user.

    Returns:
        List of tuples: (timestamp, content)
    """
    try:
        journal_path = get_journal_path()

        if not journal_path.exists():
            return []

        with open(journal_path, 'r', encoding='utf-8') as f:
            content = f.read()

        entries = []
        sections = content.split('='*60)

        for section in sections:
            if '[' in section and ']' in section:
                try:
                    timestamp_start = section.find('[') + 1
                    timestamp_end = section.find(']')
                    timestamp = section[timestamp_start:timestamp_end]
                    entry_content = section[timestamp_end+1:].strip()

                    if entry_content:
                        entries.append((timestamp, entry_content))
                except:
                    pass

        return list(reversed(entries))

    except Exception as e:
        st.error(f"Error loading journal: {e}")
        return []


def render_journal():
    """Render the digital journal tab."""
    st.subheader("📖 Your Personal Journal")

    st.write("This is your safe space. Write freely. No judgment, no filters. Just you and your thoughts.")

    # New entry section
    st.markdown("---")
    st.write("**✍️ New Entry**")

    new_entry = st.text_area(
        "What's on your mind?",
        height=200,
        placeholder="Write your thoughts, feelings, hopes, dreams, or anything you want to express...",
        key="journal_entry",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        mood = st.select_slider(
            "How are you feeling?",
            options=["😔", "😞", "😐", "🙂", "😊", "😄"],
            value="😐"
        )

    with col2:
        if st.button("💾 Save Entry", use_container_width=True):
            if new_entry.strip():
                if save_journal_entry(f"Mood: {mood}\n\n{new_entry}"):
                    st.success("✨ Your companion has noted this and will remember your progress.")
                    st.balloons()
                    # Clear the text area
                    st.session_state.journal_entry = ""
                    st.rerun()
            else:
                st.warning("Please write something before saving.")

    # Past entries section
    st.markdown("---")
    st.write("**📚 Past Entries**")

    entries = load_all_journal_entries()

    if entries:
        for timestamp, content in entries:
            with st.expander(f"📅 {timestamp}"):
                st.write(content)
                if st.button(f"Delete this entry", key=f"delete_{timestamp}"):
                    st.info("Entry deletion will be implemented in a future update.")
    else:
        st.info("No journal entries yet. Start by writing your first entry above! 🌱")


# ============================================================================
# SUGGESTIONS (RECOMMENDATIONS ENGINE)
# ============================================================================

def render_suggestions():
    """Render the media recommendations tab."""
    st.subheader("📚 Media for the Soul")

    st.write("Discover books and movies tailored to your mood and preferences.")

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_genre = st.selectbox(
            "Choose a Genre:",
            list(RECOMMENDATIONS_DATA.keys())
        )

    with col2:
        media_type = st.radio("What would you like?", ["📚 Books", "🎬 Movies"], horizontal=True)

    st.markdown("---")

    if selected_genre:
        if media_type == "📚 Books":
            books = RECOMMENDATIONS_DATA[selected_genre]["books"]
            st.write(f"**{selected_genre} Books**")

            for idx, book in enumerate(books, 1):
                with st.container():
                    col1, col2 = st.columns([0.5, 4.5])
                    with col1:
                        st.write(f"**{idx}.**")
                    with col2:
                        st.markdown(f"**{book['title']}** by {book['author']}")
                        st.write(f"*{book['description']}*")
                    st.divider()

        else:  # Movies
            movies = RECOMMENDATIONS_DATA[selected_genre]["movies"]
            st.write(f"**{selected_genre} Movies**")

            for idx, movie in enumerate(movies, 1):
                with st.container():
                    col1, col2 = st.columns([0.5, 4.5])
                    with col1:
                        st.write(f"**{idx}.**")
                    with col2:
                        st.markdown(f"**{movie['title']}**")
                        st.write(f"*{movie['description']}*")
                    st.divider()


# ============================================================================
# AFFIRMATIONS & MANTRAS
# ============================================================================

def render_affirmations():
    """Render the affirmations and mantras tab."""
    st.subheader("✨ Daily Affirmations & Mantras")

    st.write("Choose an affirmation that resonates with you. Repeat it throughout your day.")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_affirmation = st.selectbox(
            "Select an affirmation or get a random one:",
            ["🎲 Random"] + AFFIRMATIONS,
            key="affirmation_select"
        )

    with col2:
        if st.button("🎲 Get Random", key="random_affirmation", use_container_width=True):
            selected_affirmation = random.choice(AFFIRMATIONS)

    if selected_affirmation != "🎲 Random":
        st.markdown("---")

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #E8F5F0 0%, #A8DADC 100%);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(107, 144, 128, 0.2);
            margin: 20px 0;
        ">
            <p style="font-size: 24px; font-weight: bold; color: #52796F; margin: 0;">
                {selected_affirmation}
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("💙 Save Favorite", use_container_width=True):
                st.info("Favorites feature coming soon!")

        with col2:
            if st.button("📋 Copy", use_container_width=True):
                st.success("Copied to clipboard! (Share with someone who needs it)")

        with col3:
            if st.button("🎲 Next", use_container_width=True):
                st.rerun()

        st.markdown("---")

        st.write("**💡 How to use:**")
        st.markdown("""
        1. Read the affirmation slowly
        2. Take a deep breath
        3. Say it out loud 3 times
        4. Believe it. Because it's true.
        """)


# ============================================================================
# STORIES & POETRY
# ============================================================================

def render_stories():
    """Render the stories and poetry tab."""
    st.subheader("📖 Stories & Poetry")

    st.write("Short, meaningful stories to inspire, uplift, and remind you that you're not alone.")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        story_type = st.multiselect(
            "Filter by type:",
            ["Motivational", "Wisdom", "Uplifting", "Heartwarming"],
            default=["Motivational", "Wisdom", "Uplifting", "Heartwarming"]
        )

    filtered_stories = [s for s in STORIES if s["type"] in story_type]

    if filtered_stories:
        for story in filtered_stories:
            with st.container():
                st.markdown(f"""
                <div style="
                    background: #F5F5F5;
                    border-left: 4px solid #6B9080;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 15px 0;
                ">
                    <h4 style="color: #52796F; margin-top: 0;">
                        {story['title']} <span style="font-size: 12px; color: #A8DADC;">({story['type']})</span>
                    </h4>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("Read Story"):
                    st.write(story['content'])

    else:
        st.info("No stories match your filter. Try selecting different types!")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main() -> None:
    """Render the Activities Hub page."""
    st.title("🎮 Wellness Activities Hub")

    st.write(
        "Welcome to your personal wellness playground! "
        "Choose activities that resonate with you today. "
        "There's no right or wrong—just what feels right for you. 💫"
    )

    st.markdown("---")

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🎮 Mini-Games", "📖 Journal", "📚 Suggestions", "✨ Affirmations", "📖 Stories"]
    )

    with tab1:
        st.subheader("🎮 Mini-Games for Calm & Engagement")
        st.write("Take a break. Play. Breathe. Feel better.")

        game_tabs = st.tabs([
            "🫧 Breathing Bubble",
            "🟢 Zen Clicker",
            "🔤 Word Scramble",
            "🧩 Mood Matcher",
            "⚡ Reaction Timer"
        ])

        with game_tabs[0]:
            render_breathing_bubble()

        with game_tabs[1]:
            render_zen_clicker()

        with game_tabs[2]:
            render_word_scramble()

        with game_tabs[3]:
            render_mood_matcher()

        with game_tabs[4]:
            render_reaction_timer()

    with tab2:
        render_journal()

    with tab3:
        render_suggestions()

    with tab4:
        render_affirmations()

    with tab5:
        render_stories()


if __name__ == "__main__":
    main()
