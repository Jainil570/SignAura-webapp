import streamlit as st
import pandas as pd
import time
from datetime import datetime
import base64
import io
from PIL import Image
import json

# Page configuration
st.set_page_config(
    page_title="Signaura - Sign Language Learning",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Login"
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {
            'alphabets': {'current': 0, 'completed': []},
            'numbers': {'current': 0, 'completed': []},
            'words': {'current': 0, 'completed': []}
        }
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"

# Sample data (in production, this would come from a database)
USERS_DB = {
    "demo": {"password": "demo123", "email": "demo@signaura.com"},
    "user1": {"password": "pass123", "email": "user1@example.com"}
}

SIGN_DICTIONARY = {
    "alphabets": {
        "A": {"video_url": "placeholder_a.mp4", "description": "Letter A in ASL"},
        "B": {"video_url": "placeholder_b.mp4", "description": "Letter B in ASL"},
        "C": {"video_url": "placeholder_c.mp4", "description": "Letter C in ASL"},
        # Add more letters...
    },
    "numbers": {
        "1": {"video_url": "placeholder_1.mp4", "description": "Number 1 in ASL"},
        "2": {"video_url": "placeholder_2.mp4", "description": "Number 2 in ASL"},
        "3": {"video_url": "placeholder_3.mp4", "description": "Number 3 in ASL"},
        # Add more numbers...
    },
    "words": {
        "hello": {"video_url": "placeholder_hello.mp4", "description": "Hello greeting in ASL"},
        "thank you": {"video_url": "placeholder_thanks.mp4", "description": "Thank you in ASL"},
        "please": {"video_url": "placeholder_please.mp4", "description": "Please in ASL"},
        "family": {"video_url": "placeholder_family.mp4", "description": "Family in ASL"},
        # Add more words...
    }
}

# CSS for styling
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        padding: 3px;
        margin: 10px 0;
    }
    
    .progress-fill {
        background-color: #4CAF50;
        height: 20px;
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: auto;
    }
    
    .bot-message {
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
    }
    
    .video-placeholder {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 3rem;
        text-align: center;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication functions
def login_page():
    st.markdown('<h1 class="main-header">🤟 Welcome to Signaura</h1>', unsafe_allow_html=True)
    st.markdown("### Your Gateway to Sign Language Learning")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login to Your Account")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Login", use_container_width=True):
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            with col_b:
                if st.button("Demo Login", use_container_width=True):
                    st.session_state.authenticated = True
                    st.session_state.username = "demo"
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
        
        with tab2:
            st.subheader("Create New Account")
            new_username = st.text_input("Choose Username", key="signup_username")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Create Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True):
                if new_password == confirm_password and len(new_password) >= 6:
                    # In production, save to database
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Passwords don't match or are too short (min 6 characters)")

def authenticate_user(username, password):
    return username in USERS_DB and USERS_DB[username]["password"] == password

# Dashboard
def dashboard_page():
    st.markdown('<h1 class="main-header">🤟 Signaura Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"### Welcome back, {st.session_state.username}! 👋")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Letters Learned", len(st.session_state.learning_progress['alphabets']['completed']), "2")
    with col2:
        st.metric("Numbers Learned", len(st.session_state.learning_progress['numbers']['completed']), "1")
    with col3:
        st.metric("Words Learned", len(st.session_state.learning_progress['words']['completed']), "3")
    with col4:
        st.metric("Study Streak", "7 days", "1")
    
    st.markdown("---")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📚 Learn Sign Language</h3>
            <p>Start with alphabets, numbers, and basic words</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Learning", key="learn_btn", use_container_width=True):
            st.session_state.current_page = "Learning"
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔄 Translator</h3>
            <p>Convert signs to text and speech</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Translator", key="translate_btn", use_container_width=True):
            st.session_state.current_page = "Translator"
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI Assistant</h3>
            <p>Get help with your learning journey</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chat with AI", key="chat_btn", use_container_width=True):
            st.session_state.current_page = "Chatbot"

# Learning modules
def learning_page():
    st.markdown('<h1 class="main-header">📚 Learn Sign Language</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔤 Alphabets", "🔢 Numbers", "💬 Words"])
    
    with tab1:
        alphabet_learning()
    
    with tab2:
        number_learning()
    
    with tab3:
        word_learning()

def alphabet_learning():
    st.subheader("ASL Alphabet Learning")
    
    alphabets = list(SIGN_DICTIONARY["alphabets"].keys())
    current_idx = st.session_state.learning_progress['alphabets']['current']
    
    if current_idx < len(alphabets):
        current_letter = alphabets[current_idx]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Learning: Letter {current_letter}")
            
            # Video placeholder (in production, use actual video)
            st.markdown(f"""
            <div class="video-placeholder">
                <h2>📹 Video: Letter {current_letter}</h2>
                <p>Sign language demonstration for letter {current_letter}</p>
                <p><em>Video would play here in production</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(SIGN_DICTIONARY["alphabets"][current_letter]["description"])
        
        with col2:
            st.write("**Progress**")
            progress = (current_idx / len(alphabets)) * 100
            st.progress(progress / 100)
            st.write(f"{current_idx}/{len(alphabets)} completed")
            
            st.write("**Actions**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✓ Got it!", key="alphabet_next"):
                    if current_letter not in st.session_state.learning_progress['alphabets']['completed']:
                        st.session_state.learning_progress['alphabets']['completed'].append(current_letter)
                    if current_idx < len(alphabets) - 1:
                        st.session_state.learning_progress['alphabets']['current'] += 1
                    st.rerun()
            
            with col_b:
                if st.button("🔄 Replay", key="alphabet_replay"):
                    st.info("Video replayed!")
    else:
        st.success("🎉 Congratulations! You've completed all alphabets!")
        if st.button("Start Over"):
            st.session_state.learning_progress['alphabets']['current'] = 0
            st.rerun()

def number_learning():
    st.subheader("ASL Numbers Learning")
    
    numbers = list(SIGN_DICTIONARY["numbers"].keys())
    current_idx = st.session_state.learning_progress['numbers']['current']
    
    if current_idx < len(numbers):
        current_number = numbers[current_idx]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Learning: Number {current_number}")
            
            st.markdown(f"""
            <div class="video-placeholder">
                <h2>📹 Video: Number {current_number}</h2>
                <p>Sign language demonstration for number {current_number}</p>
                <p><em>Video would play here in production</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(SIGN_DICTIONARY["numbers"][current_number]["description"])
        
        with col2:
            st.write("**Progress**")
            progress = (current_idx / len(numbers)) * 100
            st.progress(progress / 100)
            st.write(f"{current_idx}/{len(numbers)} completed")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✓ Got it!", key="number_next"):
                    if current_number not in st.session_state.learning_progress['numbers']['completed']:
                        st.session_state.learning_progress['numbers']['completed'].append(current_number)
                    if current_idx < len(numbers) - 1:
                        st.session_state.learning_progress['numbers']['current'] += 1
                    st.rerun()
            
            with col_b:
                if st.button("🔄 Replay", key="number_replay"):
                    st.info("Video replayed!")
    else:
        st.success("🎉 Great job! You've learned all numbers!")

def word_learning():
    st.subheader("Basic Words & Phrases")
    
    words = list(SIGN_DICTIONARY["words"].keys())
    current_idx = st.session_state.learning_progress['words']['current']
    
    if current_idx < len(words):
        current_word = words[current_idx]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Learning: {current_word.title()}")
            
            st.markdown(f"""
            <div class="video-placeholder">
                <h2>📹 Video: {current_word.title()}</h2>
                <p>Sign language demonstration for "{current_word}"</p>
                <p><em>Video would play here in production</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(SIGN_DICTIONARY["words"][current_word]["description"])
        
        with col2:
            st.write("**Progress**")
            progress = (current_idx / len(words)) * 100
            st.progress(progress / 100)
            st.write(f"{current_idx}/{len(words)} completed")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✓ Got it!", key="word_next"):
                    if current_word not in st.session_state.learning_progress['words']['completed']:
                        st.session_state.learning_progress['words']['completed'].append(current_word)
                    if current_idx < len(words) - 1:
                        st.session_state.learning_progress['words']['current'] += 1
                    st.rerun()
            
            with col_b:
                if st.button("🔄 Replay", key="word_replay"):
                    st.info("Video replayed!")
    else:
        st.success("🎉 Excellent! You've learned all basic words!")

# Translator
def translator_page():
    st.markdown('<h1 class="main-header">🔄 Sign Language Translator</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📸 Sign to Text", "📝 Text to Sign"])
    
    with tab1:
        sign_to_text()
    
    with tab2:
        text_to_sign()

def sign_to_text():
    st.subheader("Convert Sign Language to Text")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Upload Image or Use Camera**")
        
        upload_option = st.radio("Choose input method:", ["Upload Image", "Use Camera"])
        
        if upload_option == "Upload Image":
            uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                if st.button("🔍 Analyze Sign"):
                    # Placeholder for ML model prediction
                    with st.spinner("Analyzing sign..."):
                        time.sleep(2)  # Simulate processing time
                        predicted_text = "Hello"  # This would come from your ML model
                        confidence = 95.2
                        
                        st.success(f"**Detected Sign:** {predicted_text}")
                        st.info(f"**Confidence:** {confidence}%")
                        
                        # Audio output option
                        if st.button("🔊 Play Audio"):
                            st.audio("data:audio/wav;base64,UklGRnABAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YUwBAABBhAr//39/f39/f39/f39/f39/f3...") # Placeholder
        
        else:
            st.write("📹 **Live Camera Feed**")
            st.info("Camera integration would be implemented here using webcam capture")
            
            if st.button("📷 Capture & Analyze"):
                with st.spinner("Capturing and analyzing..."):
                    time.sleep(2)
                    st.success("**Detected Sign:** Thank you")
                    st.info("**Confidence:** 89.7%")
    
    with col2:
        st.write("**Translation History**")
        
        # Sample translation history
        history = [
            {"time": "2 min ago", "sign": "Hello", "confidence": "95.2%"},
            {"time": "5 min ago", "sign": "Thank you", "confidence": "89.7%"},
            {"time": "8 min ago", "sign": "Please", "confidence": "92.1%"},
        ]
        
        for item in history:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; margin: 5px 0; border-radius: 5px;">
                <strong>{item['sign']}</strong> - {item['confidence']}<br>
                <small>{item['time']}</small>
            </div>
            """, unsafe_allow_html=True)

def text_to_sign():
    st.subheader("Convert Text to Sign Language")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Enter Text or Speak**")
        
        input_method = st.radio("Input method:", ["Type Text", "Voice Input"])
        
        if input_method == "Type Text":
            user_text = st.text_area("Enter text to convert:", placeholder="Type your message here...")
            
            if st.button("🔄 Convert to Signs") and user_text:
                words = user_text.lower().split()
                
                st.write("**Sign Language Translation:**")
                
                for word in words:
                    if word in SIGN_DICTIONARY["words"]:
                        st.markdown(f"""
                        <div class="video-placeholder" style="margin: 10px 0; padding: 20px;">
                            <h4>📹 Sign for: "{word}"</h4>
                            <p><em>Video demonstration would play here</em></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Try to spell out unknown words
                        st.write(f"**Spelling out '{word}':**")
                        for char in word:
                            if char.upper() in SIGN_DICTIONARY["alphabets"]:
                                st.write(f"Letter: {char.upper()}")
        
        else:
            st.info("🎤 Voice input would be integrated here using speech recognition")
            if st.button("🎤 Start Recording"):
                st.success("Recording... (This would use speech-to-text API)")
    
    with col2:
        st.write("**Quick Phrases**")
        
        common_phrases = ["Hello", "Thank you", "Please", "Good morning", "How are you?", "Nice to meet you"]
        
        for phrase in common_phrases:
            if st.button(phrase, key=f"phrase_{phrase}"):
                st.write(f"Showing signs for: **{phrase}**")
                st.markdown(f"""
                <div class="video-placeholder">
                    <h4>📹 "{phrase}"</h4>
                    <p><em>Video would play here</em></p>
                </div>
                """, unsafe_allow_html=True)

# Chatbot
def chatbot_page():
    st.markdown('<h1 class="main-header">🤖 AI Learning Assistant</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Chat with your AI tutor")
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>AI Tutor:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Ask me anything about sign language:", placeholder="How do I sign 'hello'?")
        
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("Send", use_container_width=True) and user_input:
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Generate AI response (placeholder - in production use actual AI)
                ai_response = generate_ai_response(user_input)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
                st.rerun()
        
        with col_b:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    with col2:
        st.write("**Quick Help**")
        
        quick_questions = [
            "How do I sign 'hello'?",
            "Show me the alphabet",
            "What's my progress?",
            "Practice numbers",
            "Common phrases"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": question})
                ai_response = generate_ai_response(question)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()

def generate_ai_response(user_input):
    """Generate AI response (placeholder function)"""
    user_input_lower = user_input.lower()
    
    if "hello" in user_input_lower:
        return "To sign 'hello', wave your hand with your palm facing outward, similar to a regular wave! You can practice this in the Words section of our learning module."
    
    elif "alphabet" in user_input_lower:
        return "The sign language alphabet uses different hand shapes for each letter. You can learn all 26 letters in our Alphabets learning section. Would you like me to show you a specific letter?"
    
    elif "progress" in user_input_lower:
        completed_letters = len(st.session_state.learning_progress['alphabets']['completed'])
        completed_numbers = len(st.session_state.learning_progress['numbers']['completed'])
        completed_words = len(st.session_state.learning_progress['words']['completed'])
        return f"Great question! Here's your progress: Letters: {completed_letters} completed, Numbers: {completed_numbers} completed, Words: {completed_words} completed. Keep up the good work!"
    
    elif "number" in user_input_lower:
        return "Numbers in sign language are formed using specific finger configurations. Numbers 1-5 use your fingers naturally, while 6-9 have special hand positions. Check out our Numbers learning section!"
    
    elif "phrase" in user_input_lower:
        return "Some common phrases include 'Hello', 'Thank you', 'Please', and 'Nice to meet you'. You can find these in our Words section or use the Text-to-Sign translator!"
    
    else:
        return "I'm here to help you learn sign language! You can ask me about letters, numbers, words, or your learning progress. You can also use our learning modules and translator tools."

# Dictionary
def dictionary_page():
    st.markdown('<h1 class="main-header">📖 Sign Language Dictionary</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Search functionality
        search_term = st.text_input("🔍 Search for a sign:", placeholder="Enter a letter, number, or word...")
        
        category_filter = st.selectbox("Filter by category:", ["All", "Alphabets", "Numbers", "Words"])
        
        # Display results
        if search_term:
            st.subheader(f"Search results for: '{search_term}'")
            show_search_results(search_term, category_filter)
        else:
            st.subheader("Browse Dictionary")
            show_all_signs(category_filter)
    
    with col2:
        st.write("**Quick Navigation**")
        
        if st.button("📝 All Alphabets", use_container_width=True):
            st.session_state.dict_filter = "Alphabets"
            st.rerun()
        
        if st.button("🔢 All Numbers", use_container_width=True):
            st.session_state.dict_filter = "Numbers"
            st.rerun()
        
        if st.button("💬 Common Words", use_container_width=True):
            st.session_state.dict_filter = "Words"
            st.rerun()
        
        st.markdown("---")
        st.write("**Statistics**")
        st.metric("Total Signs", len(SIGN_DICTIONARY["alphabets"]) + len(SIGN_DICTIONARY["numbers"]) + len(SIGN_DICTIONARY["words"]))
        st.metric("Categories", 3)

def show_search_results(search_term, category_filter):
    results = []
    
    # Search in each category
    for category, signs in SIGN_DICTIONARY.items():
        if category_filter == "All" or category_filter.lower() == category:
            for sign, data in signs.items():
                if search_term.lower() in sign.lower() or search_term.lower() in data["description"].lower():
                    results.append({"category": category, "sign": sign, "data": data})
    
    if results:
        for result in results:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #007bff;">
                <h4>{result['sign'].upper()} ({result['category'].title()})</h4>
                <p>{result['data']['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button(f"▶️ Play Video", key=f"play_{result['sign']}"):
                    st.info(f"Playing video for: {result['sign']}")
            with col_b:
                if st.button(f"📚 Learn More", key=f"learn_{result['sign']}"):
                    st.info(f"More info about: {result['sign']}")
    else:
        st.warning("No results found. Try a different search term.")

def show_all_signs(category_filter):
    for category, signs in SIGN_DICTIONARY.items():
        if category_filter == "All" or category_filter.lower() == category:
            st.subheader(f"{category.title()}")
            
            # Display in columns for better layout
            cols = st.columns(3)
            
            for idx, (sign, data) in enumerate(signs.items()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 10px; margin: 5px 0; border-radius: 5px; text-align: center;">
                        <h5>{sign.upper()}</h5>
                        <p><small>{data['description']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"▶️", key=f"dict_play_{sign}_{category}", help=f"Play {sign}"):
                        st.info(f"Playing: {sign}")

# Profile/Settings
def profile_page():
    st.markdown('<h1 class="main-header">👤 Profile & Settings</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Progress", "Settings"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Profile Picture")
            st.image("https://via.placeholder.com/150/007bff/ffffff?text=👤", width=150)
            
            if st.button("Upload New Photo"):
                st.info("Photo upload would be implemented here")
        
        with col2:
            st.markdown("### Account Information")
            
            # Get user info (in production, from database)
            user_info = USERS_DB.get(st.session_state.username, {})
            
            name = st.text_input("Full Name", value="Demo User")
            email = st.text_input("Email", value=user_info.get("email", ""))
            bio = st.text_area("Bio", value="Learning sign language with Signaura!")
            
            join_date = st.text_input("Member Since", value="January 2025", disabled=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Save Changes", use_container_width=True):
                    st.success("Profile updated successfully!")
            with col_b:
                if st.button("Reset Password", use_container_width=True):
                    st.info("Password reset email sent!")
    
    with tab2:
        st.markdown("### Learning Progress")
        
        # Overall progress
        total_alphabets = len(SIGN_DICTIONARY["alphabets"])
        total_numbers = len(SIGN_DICTIONARY["numbers"])
        total_words = len(SIGN_DICTIONARY["words"])
        
        completed_alphabets = len(st.session_state.learning_progress['alphabets']['completed'])
        completed_numbers = len(st.session_state.learning_progress['numbers']['completed'])
        completed_words = len(st.session_state.learning_progress['words']['completed'])
        
        # Progress cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            alphabet_progress = (completed_alphabets / total_alphabets) * 100
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>🔤 Alphabets</h3>
                <h2>{completed_alphabets}/{total_alphabets}</h2>
                <p>{alphabet_progress:.1f}% Complete</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            number_progress = (completed_numbers / total_numbers) * 100
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>🔢 Numbers</h3>
                <h2>{completed_numbers}/{total_numbers}</h2>
                <p>{number_progress:.1f}% Complete</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            word_progress = (completed_words / total_words) * 100
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3>💬 Words</h3>
                <h2>{completed_words}/{total_words}</h2>
                <p>{word_progress:.1f}% Complete</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed progress
        st.markdown("### Detailed Progress")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Completed Items:**")
            
            if st.session_state.learning_progress['alphabets']['completed']:
                st.write("📝 **Alphabets:**", ", ".join(st.session_state.learning_progress['alphabets']['completed']))
            
            if st.session_state.learning_progress['numbers']['completed']:
                st.write("🔢 **Numbers:**", ", ".join(st.session_state.learning_progress['numbers']['completed']))
            
            if st.session_state.learning_progress['words']['completed']:
                st.write("💬 **Words:**", ", ".join(st.session_state.learning_progress['words']['completed']))
        
        with col2:
            st.write("**Study Statistics:**")
            st.metric("Total Study Time", "2h 30m")
            st.metric("Sessions Completed", "15")
            st.metric("Current Streak", "7 days")
            st.metric("Best Streak", "12 days")
        
        # Reset progress button
        st.markdown("---")
        if st.button("🔄 Reset All Progress", type="secondary"):
            if st.checkbox("I understand this will reset all my progress"):
                st.session_state.learning_progress = {
                    'alphabets': {'current': 0, 'completed': []},
                    'numbers': {'current': 0, 'completed': []},
                    'words': {'current': 0, 'completed': []}
                }
                st.success("Progress reset successfully!")
                st.rerun()
    
    with tab3:
        st.markdown("### App Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Display Settings**")
            
            theme = st.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "light" else 1)
            if theme != st.session_state.theme:
                st.session_state.theme = theme.lower()
                st.info("Theme updated! (Full implementation would require CSS changes)")
            
            font_size = st.selectbox("Font Size", ["Small", "Medium", "Large"], index=1)
            
            show_progress = st.checkbox("Show progress indicators", value=True)
            
            st.write("**Learning Settings**")
            
            auto_play = st.checkbox("Auto-play videos", value=True)
            repeat_mode = st.checkbox("Repeat videos automatically", value=False)
            
            difficulty = st.selectbox("Learning Pace", ["Beginner", "Intermediate", "Advanced"], index=0)
        
        with col2:
            st.write("**Notification Settings**")
            
            daily_reminder = st.checkbox("Daily learning reminder", value=True)
            
            if daily_reminder:
                reminder_time = st.time_input("Reminder time", value=None)
            
            achievement_notifications = st.checkbox("Achievement notifications", value=True)
            
            progress_emails = st.checkbox("Weekly progress emails", value=False)
            
            st.write("**Audio Settings**")
            
            enable_sound = st.checkbox("Enable sound effects", value=True)
            
            voice_feedback = st.checkbox("Voice feedback for translations", value=True)
            
            if voice_feedback:
                voice_speed = st.slider("Voice speed", 0.5, 2.0, 1.0, 0.1)
        
        st.markdown("---")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("Save Settings", use_container_width=True):
                st.success("Settings saved successfully!")
        
        with col_b:
            if st.button("Export Data", use_container_width=True):
                st.info("Your data export is being prepared...")
        
        with col_c:
            if st.button("Delete Account", use_container_width=True, type="secondary"):
                st.error("Account deletion would be implemented here with proper confirmation.")

# Sidebar navigation
def sidebar_navigation():
    with st.sidebar:
        st.markdown("### 🤟 Signaura")
        
        if st.session_state.authenticated:
            st.markdown(f"**Welcome, {st.session_state.username}!**")
            
            # Navigation menu
            pages = {
                "🏠 Dashboard": "Dashboard",
                "📚 Learn": "Learning",
                "🔄 Translator": "Translator",
                "🤖 AI Assistant": "Chatbot",
                "📖 Dictionary": "Dictionary",
                "👤 Profile": "Profile"
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # Quick stats in sidebar
            st.markdown("### 📊 Quick Stats")
            completed_total = (
                len(st.session_state.learning_progress['alphabets']['completed']) +
                len(st.session_state.learning_progress['numbers']['completed']) +
                len(st.session_state.learning_progress['words']['completed'])
            )
            st.metric("Signs Learned", completed_total)
            st.metric("Study Streak", "7 days")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.current_page = "Login"
                st.rerun()
        
        else:
            st.markdown("**Please login to continue**")
            st.info("Use demo/demo123 for quick access")

# Main app logic
def main():
    init_session_state()
    load_css()
    
    sidebar_navigation()
    
    # Route to appropriate page
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.current_page == "Dashboard":
            dashboard_page()
        elif st.session_state.current_page == "Learning":
            learning_page()
        elif st.session_state.current_page == "Translator":
            translator_page()
        elif st.session_state.current_page == "Chatbot":
            chatbot_page()
        elif st.session_state.current_page == "Dictionary":
            dictionary_page()
        elif st.session_state.current_page == "Profile":
            profile_page()
        else:
            dashboard_page()

# Footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🤟 <strong>Signaura</strong> - Making sign language accessible to everyone</p>
        <p>Built with ❤️ using Streamlit | <a href="#" style="color: #007bff;">Support</a> | <a href="#" style="color: #007bff;">Privacy</a> | <a href="#" style="color: #007bff;">Terms</a></p>
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
    show_footer()