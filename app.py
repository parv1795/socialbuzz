import streamlit as st
import openai
import pyperclip
import time

# Set page config
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4267B2;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #365899;
    }
    .copy-btn {
        background-color: #25D366;
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    .copy-btn:hover {
        background-color: #128C7E;
    }
    .platform-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .post-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .input-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key_verified' not in st.session_state:
    st.session_state.api_key_verified = False
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""
if 'edited_post' not in st.session_state:
    st.session_state.edited_post = ""
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'platform' not in st.session_state:
    st.session_state.platform = ""
if 'tone' not in st.session_state:
    st.session_state.tone = ""
if 'length' not in st.session_state:
    st.session_state.length = ""

# Header
st.title("📱 Social Media Post Generator")
st.markdown("Create customized posts for LinkedIn, Twitter, and WhatsApp with your preferred tone and length.")

# Step 1: API Key Authentication
if not st.session_state.api_key_verified:
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.subheader("Step 1: API Key Authentication")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if st.button("Verify API Key"):
        if api_key:
            try:
                openai.api_key = api_key
                # Simple verification by just making a small request
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                st.session_state.api_key_verified = True
                st.session_state.api_key = api_key
                st.success("API Key verified successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to verify API key: {str(e)}")
        else:
            st.error("Please enter an API key.")
    st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Input Fields
else:
    # Left column for inputs
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.subheader("Step 2: Customize Your Post")
        
        # Title input
        title = st.text_input("Post Topic:", placeholder="e.g., AI Summit Delhi 2025", value=st.session_state.title)
        
        # Platform dropdown
        platform = st.selectbox(
            "Select Platform:",
            ["", "LinkedIn", "Twitter", "WhatsApp"],
            index=0 if st.session_state.platform == "" else 
                 ["", "LinkedIn", "Twitter", "WhatsApp"].index(st.session_state.platform)
        )
        
        # Tone dropdown
        tone = st.selectbox(
            "Select Tone:",
            ["", "Professional", "Casual", "Sarcastic", "Humorous", "Inspirational", 
             "Excited/Hyped", "Minimalist", "Storytelling", "Authoritative", "Marketing/Salesy"],
            index=0 if st.session_state.tone == "" else 
                 ["", "Professional", "Casual", "Sarcastic", "Humorous", "Inspirational", 
                  "Excited/Hyped", "Minimalist", "Storytelling", "Authoritative", "Marketing/Salesy"].index(st.session_state.tone)
        )
        
        # Length dropdown
        length = st.selectbox(
            "Select Length:",
            ["", "Short", "Medium", "Long", "Thread/Multiple Messages"],
            index=0 if st.session_state.length == "" else 
                 ["", "Short", "Medium", "Long", "Thread/Multiple Messages"].index(st.session_state.length)
        )
        
        # Create post and reset buttons
        col1_btn, col2_btn = st.columns(2)
        with col1_btn:
            create_post = st.button("Create Post")
        with col2_btn:
            reset = st.button("Reset")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: Display generated post
    with col2:
        if st.session_state.generated_post:
            st.markdown('<div class="post-container">', unsafe_allow_html=True)
            st.subheader("Step 3: Your Generated Post")
            
            # Display platform-specific header
            if platform:
                icon = "🔗" if platform == "LinkedIn" else "🐦" if platform == "Twitter" else "💬"
                st.markdown(f'<div class="platform-header">{icon} {platform} Post</div>', unsafe_allow_html=True)
            
            # Display editable post
            edited_post = st.text_area("Edit your post if needed:", value=st.session_state.generated_post, height=300)
            st.session_state.edited_post = edited_post
            
            # Copy button
            if st.button("Copy to Clipboard"):
                try:
                    pyperclip.copy(edited_post)
                    st.success("Post copied to clipboard!")
                except Exception:
                    st.info("Clipboard functionality works when running locally. If you're using this in a web environment, please manually copy the text.")
            st.markdown('</div>', unsafe_allow_html=True)

    # Generate post when Create Post button is clicked
    if create_post:
        if title and platform and tone and length:
            st.session_state.title = title
            st.session_state.platform = platform
            st.session_state.tone = tone
            st.session_state.length = length
            
            # Show loading indicator
            with st.spinner("Generating your post..."):
                try:
                    # Length definitions
                    length_constraints = {
                        "Short": "within 280 characters for Twitter, about 50-100 words for others",
                        "Medium": "around 150-200 words",
                        "Long": "around 300-500 words, detailed and comprehensive",
                        "Thread/Multiple Messages": "create a thread of 3-5 connected posts"
                    }
                    
                    # Platform-specific instructions
                    platform_instructions = {
                        "LinkedIn": "professional tone, include hashtags, and focus on business value",
                        "Twitter": "concise, attention-grabbing, include relevant hashtags, stay within character limits",
                        "WhatsApp": "conversational, use emojis appropriately, and make it shareable"
                    }
                    
                    # Tone definitions
                    tone_descriptions = {
                        "Professional": "formal and business-like",
                        "Casual": "friendly and conversational",
                        "Sarcastic": "witty with a hint of mockery",
                        "Humorous": "lighthearted and fun",
                        "Inspirational": "motivational and uplifting",
                        "Excited/Hyped": "energetic and enthusiastic",
                        "Minimalist": "short and to the point",
                        "Storytelling": "engaging with a narrative style",
                        "Authoritative": "bold and confident, establishing expertise",
                        "Marketing/Salesy": "persuasive with a strong call-to-action"
                    }
                    
                    # Construct the prompt
                    prompt = f"""
                    Create a {platform} post about '{title}' with the following specifications:
                    - Tone: {tone} ({tone_descriptions[tone]})
                    - Length: {length} ({length_constraints[length]})
                    - Platform considerations: {platform_instructions[platform]}
                    
                    Make sure the post is engaging, authentic, and optimized for the {platform} platform.
                    If generating a thread, clearly separate each post with [Post 1], [Post 2], etc.
                    Include appropriate hashtags and emojis where relevant.
                    """
                    
                    # Call OpenAI API
                    response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"You are an expert social media content creator specializing in creating engaging posts for {platform}."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    # Extract the generated post
                    generated_post = response.choices[0].message.content.strip()
                    st.session_state.generated_post = generated_post
                    st.session_state.edited_post = generated_post
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating post: {str(e)}")
        else:
            st.error("Please fill in all fields to generate a post.")
    
    # Reset the form when Reset button is clicked
    if reset:
        st.session_state.title = ""
        st.session_state.platform = ""
        st.session_state.tone = ""
        st.session_state.length = ""
        st.session_state.generated_post = ""
        st.session_state.edited_post = ""
        st.rerun()

# Footer
st.markdown("---")
st.markdown("📱 Social Media Post Generator | Create engaging content in seconds")