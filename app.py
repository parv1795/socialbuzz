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
if 'custom_word_count' not in st.session_state:
    st.session_state.custom_word_count = 100

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
        length_options = ["", "Short", "Medium", "Long", "Thread/Multiple Messages", "Custom Length"]
        length = st.selectbox(
            "Select Length:",
            length_options,
            index=0 if st.session_state.length == "" else 
                 (length_options.index(st.session_state.length) if st.session_state.length in length_options else 0)
        )
        
        # Custom word count input (conditionally shown)
        if length == "Custom Length":
            custom_word_count = st.number_input(
                "Enter desired word count:",
                min_value=1,
                max_value=2000,
                value=st.session_state.custom_word_count
            )
            st.session_state.custom_word_count = custom_word_count
        
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
            
            # Word count display
            word_count = len(edited_post.split())
            st.info(f"Current word count: {word_count} words")
            
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
                    # Define word count targets based on length selection
                    word_count_targets = {
                        "Short": 75,  # ~75 words
                        "Medium": 175,  # ~175 words
                        "Long": 400,  # ~400 words
                        "Thread/Multiple Messages": 450,  # ~450 words total across posts
                        "Custom Length": st.session_state.custom_word_count  # User-defined
                    }
                    
                    # Get target word count based on selected length
                    target_word_count = word_count_targets[length]
                    
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
                    
                    # Determine if post should be a thread or single post
                    is_thread = (length == "Thread/Multiple Messages")
                    
                    # Construct the prompt with explicit word count instructions
                    if is_thread:
                        format_instructions = (
                            f"Create a thread of 3-5 connected posts. "
                            f"Clearly separate each post with [Post 1], [Post 2], etc. "
                            f"Ensure the total word count across all posts is EXACTLY {target_word_count} words."
                        )
                    else:
                        format_instructions = (
                            f"Create a SINGLE cohesive post with EXACTLY {target_word_count} words. "
                            f"Do NOT use [Post 1], [Post 2] formatting - this should be one continuous post."
                        )
                    
                    prompt = f"""
                    Create a {platform} post about '{title}' with the following specifications:
                    - Tone: {tone} ({tone_descriptions[tone]})
                    - Word Count: EXACTLY {target_word_count} words (this is very important)
                    - Format: {format_instructions}
                    - Platform considerations: {platform_instructions[platform]}
                    
                    Make sure the post is engaging, authentic, and optimized for the {platform} platform.
                    Include appropriate hashtags and emojis where relevant, but these count toward the total word count.
                    
                    The final post MUST be exactly {target_word_count} words - no more, no less.
                    """
                    
                    # Call OpenAI API with adjusted max_tokens to accommodate the desired word count
                    # Estimating ~1.5 tokens per word on average for English
                    max_tokens = int(target_word_count * 2)  # Multiplying by 2 to give some margin
                    
                    response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"You are an expert social media content creator specializing in creating engaging posts for {platform}. Your task is to create posts with EXACTLY the requested word count. {'Create a thread of multiple posts separated by [Post 1], [Post 2] etc.' if is_thread else 'Create a single cohesive post without any [Post X] markings.'}"},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.7
                    )
                    
                    # Extract the generated post
                    generated_post = response.choices[0].message.content.strip()
                    
                    # Verify and adjust word count if needed
                    words = generated_post.split()
                    actual_word_count = len(words)
                    
                    # If the word count is off by more than 10%, make another attempt
                    if abs(actual_word_count - target_word_count) > target_word_count * 0.1:
                        adjustment_prompt = f"""
                        The post you created has {actual_word_count} words, but I requested EXACTLY {target_word_count} words.
                        Please adjust the post to have EXACTLY {target_word_count} words while maintaining the same topic, tone, and style.
                        {'Maintain the thread format with [Post X] markers.' if is_thread else 'Keep it as a single cohesive post without any [Post X] markings.'}
                        
                        Current post:
                        {generated_post}
                        """
                        
                        response = openai.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": f"You are an expert at adjusting text to exact word counts while maintaining quality."},
                                {"role": "user", "content": adjustment_prompt}
                            ],
                            max_tokens=max_tokens,
                            temperature=0.5
                        )
                        
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
        st.session_state.custom_word_count = 100  # Reset to default
        st.rerun()

# Footer
st.markdown("---")
st.markdown("📱 Social Media Post Generator | Create engaging content in seconds")
