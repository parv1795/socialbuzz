import streamlit as st
import openai
import pyperclip
import time
import os
import base64
import requests
from io import BytesIO
from PIL import Image

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
    .image-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .image-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: space-around;
    }
    .image-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        width: 250px;
    }
    /* Aggressively target and remove all capsule containers and dividers */
    div[data-testid="stCaptionContainer"],
    div[data-testid="stHeader"],
    div[data-baseweb="card"],
    div.stMarkdown > div > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Target subheaders specifically */
    .stSubheader > div:first-child {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    
    /* Fix specific styling for headers */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.75em !important;
        margin-bottom: 0.5em !important;
        padding: 0 !important;
        background: none !important;
        border: none !important;
    }
    
    /* Fix for step containers */
    section[data-testid="stSidebar"] > div,
    .main > div {
        background-color: transparent !important;
        border: none !important;
    }
    .download-btn {
        background-color: #5b7dff;
        color: white !important; /* Force white text color */
        border-radius: 12px;
        padding: 8px 10px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        width: 100%;
        margin-top: 5px;
        transition: all 0.3s ease;
        text-decoration: none !important; /* Remove underline */
        display: block;
        text-align: center;
    }
    .download-btn:hover {
        background-color: #3957e0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: white !important; /* Keep text white even on hover */
    }
    .regenerate-btn {
        background-color: #FF5722;
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to download image
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}" class="download-btn">📥 {text}</a>'
    return href

# Function to generate image using DALL-E
def generate_dall_e_images(prompt, n=1):
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=n,
            size="1024x1024",  # Square format
            response_format="b64_json"
        )
        
        # Extract the base64 encoded images
        images_data = []
        for data in response.data:
            images_data.append(data.b64_json)
        
        return images_data
    except Exception as e:
        st.error(f"Error generating images: {str(e)}")
        return []

# Function to generate image prompts based on post content
def generate_image_prompts(title, post_content, num_images=2):
    try:
        prompt = f"""
        Based on this social media post about "{title}", create {num_images} different image prompts for DALL-E 3.
        Each prompt should describe a square-format image that would complement the post well.
        Make the prompts specific, visually appealing, and under 200 characters each.
        Format your response as a numbered list with just the prompts, nothing else.

        Post content:
        {post_content}
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use faster model to speed up process
            messages=[
                {"role": "system", "content": "You are an expert at creating visual prompts for AI image generators."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Reduced tokens
            temperature=0.7
        )
        
        # Parse the response to extract prompts
        prompts_text = response.choices[0].message.content.strip()
        # Split by line, filter empty lines and remove numbering
        prompts = []
        for line in prompts_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line[0] == '-'):
                # Remove numbering/bullet and any separator like ". " or ") "
                cleaned_line = line[1:].strip()
                if cleaned_line[0] in ['.', ')', '-', ':']:
                    cleaned_line = cleaned_line[1:].strip()
                prompts.append(cleaned_line)
        
        # Limit to requested number
        return prompts[:num_images]
    
    except Exception as e:
        st.error(f"Error generating image prompts: {str(e)}")
        # Fallback prompts
        return [f"Professional square image related to {title}"] * num_images

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
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'image_prompts' not in st.session_state:
    st.session_state.image_prompts = []

def main():
    # Apply custom CSS directly to target white capsules
    st.markdown("""
    <style>
    /* Target and remove white capsule dividers around subheaders */
    .stSubheader {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }

    /* Target the specific subheader wrapper Streamlit uses */
    .stSubheader > div {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("📱 Social Media Post Generator")
    st.markdown("Create customized posts for LinkedIn, Twitter, and WhatsApp with your preferred tone and length. Now with AI image generation!")

    # Step 1: API Key Authentication
    if not st.session_state.api_key_verified:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown('<h3>Step 1: API Key Authentication</h3>', unsafe_allow_html=True)
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
            st.markdown('<h3>Step 2: Customize Your Post</h3>', unsafe_allow_html=True)
            
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
                create_post = st.button("Create Post", key="create_post_btn")
            with col2_btn:
                reset = st.button("Reset", key="reset_btn")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Step 3: Display generated post
        with col2:
            if st.session_state.generated_post:
                st.markdown('<div class="post-container">', unsafe_allow_html=True)
                st.markdown('<h3>Step 3: Your Generated Post</h3>', unsafe_allow_html=True)
                
                # Display platform-specific header
                if platform:
                    icon = "🔗" if platform == "LinkedIn" else "🐦" if platform == "Twitter" else "💬"
                    st.markdown(f'<div class="platform-header">{icon} {platform} Post</div>', unsafe_allow_html=True)
                
                # Display editable post
                edited_post = st.text_area("Edit your post if needed:", value=st.session_state.generated_post, height=250)
                st.session_state.edited_post = edited_post
                
                # Word count display
                word_count = len(edited_post.split())
                st.info(f"Current word count: {word_count} words")
                
                # Copy and regenerate post buttons
                col1_action, col2_action = st.columns(2)
                with col1_action:
                    if st.button("Copy to Clipboard", key="copy_clipboard"):
                        try:
                            pyperclip.copy(edited_post)
                            st.success("Post copied to clipboard!")
                        except Exception:
                            st.info("Clipboard functionality works when running locally. If you're using this in a web environment, please manually copy the text.")
                
                with col2_action:
                    if st.button("Regenerate Post", key="regenerate_post_btn"):
                        with st.spinner("Regenerating your post..."):
                            try:
                                # Define word count targets based on length selection
                                word_count_targets = {
                                    "Short": 75,  # ~75 words
                                    "Medium": 175,  # ~175 words
                                    "Long": 400,  # ~400 words
                                    "Thread/Multiple Messages": 600,  # ~600 words (to be split into multiple messages)
                                    "Custom Length": st.session_state.custom_word_count
                                }
                                
                                target_words = word_count_targets.get(length, 150)  # Default to 150 if not found
                                
                                # Additional constraints based on platform
                                platform_notes = ""
                                if platform == "Twitter":
                                    platform_notes = "Respect Twitter's character limit (280 chars). Use hashtags appropriately."
                                elif platform == "LinkedIn":
                                    platform_notes = "Professional tone with appropriate line breaks. Can include hashtags and tag people with @."
                                elif platform == "WhatsApp":
                                    platform_notes = "More casual, conversational and direct. Can use emojis naturally."
                                
                                # Additional notes for thread format
                                thread_notes = ""
                                if length == "Thread/Multiple Messages":
                                    if platform == "Twitter":
                                        thread_notes = "Format as 4-5 connected tweets in a thread, with each under 280 characters."
                                    else:
                                        thread_notes = "Format as 3-4 separate messages that build on each other."
                                
                                # Create prompt for GPT
                                prompt = f"""
                                Create a compelling social media post about "{title}" for {platform}.
                                
                                Tone: {tone}
                                Target length: {target_words} words
                                {platform_notes}
                                {thread_notes}
                                
                                The post should be engaging, relevant to the platform, and formatted appropriately.
                                Add emojis where they fit naturally with the tone and platform.
                                For LinkedIn and Twitter, include 2-3 appropriate hashtags.
                                For LinkedIn, make sure it has good paragraph breaks for readability.
                                For WhatsApp, make it more personal and conversational.
                                
                                Return ONLY the post content with no explanations or additional text.
                                """
                                
                                # Make request to GPT
                                response = openai.chat.completions.create(
                                    model="gpt-4",
                                    messages=[
                                        {"role": "system", "content": "You are an expert social media manager who creates engaging, platform-appropriate content."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    max_tokens=1500,
                                    temperature=0.7
                                )
                                
                                # Extract response
                                generated_post = response.choices[0].message.content.strip()
                                st.session_state.generated_post = generated_post
                                st.session_state.edited_post = generated_post
                                
                                # Reset images when post is regenerated
                                st.session_state.generated_images = []
                                st.session_state.image_prompts = []
                                
                                # Refresh page to show results
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error regenerating post: {str(e)}")
                        
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 4: Generated Images
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.markdown('<h3>Step 4: AI Generated Images</h3>', unsafe_allow_html=True)
                
                # Generate/Regenerate images button
                if st.session_state.generated_images:
                    if st.button("Regenerate Images for this Post", key="regenerate_images"):
                        with st.status("Regenerating images...", expanded=True) as status:
                            status.update(label="Creating new image prompts...", state="running")
                            # Reduce to just 2 images to speed up generation
                            image_prompts = generate_image_prompts(title, st.session_state.edited_post, num_images=2)
                            st.session_state.image_prompts = image_prompts
                            
                            # Generate images for the prompts
                            if image_prompts:
                                all_images = []
                                for i, prompt in enumerate(image_prompts):
                                    status.update(label=f"Generating image {i+1} of {len(image_prompts)}...", state="running")
                                    images = generate_dall_e_images(prompt, n=1)
                                    all_images.extend(images)
                                
                                st.session_state.generated_images = all_images
                                status.update(label="Images regenerated successfully!", state="complete")
                                st.rerun()  # Refresh to show images
                            else:
                                status.update(label="Failed to generate image prompts. Please try again.", state="error")
                else:
                    if st.button("Generate Relevant Images for this Post", key="generate_images"):
                        with st.status("Generating images...", expanded=True) as status:
                            status.update(label="Creating image prompts...", state="running")
                            # Reduce to just 2 images to speed up generation
                            image_prompts = generate_image_prompts(title, st.session_state.edited_post, num_images=2)
                            st.session_state.image_prompts = image_prompts
                            
                            # Generate images for the prompts
                            if image_prompts:
                                all_images = []
                                for i, prompt in enumerate(image_prompts):
                                    status.update(label=f"Generating image {i+1} of {len(image_prompts)}...", state="running")
                                    images = generate_dall_e_images(prompt, n=1)
                                    all_images.extend(images)
                                
                                st.session_state.generated_images = all_images
                                status.update(label="Images generated successfully!", state="complete")
                                st.rerun()  # Refresh to show images
                            else:
                                status.update(label="Failed to generate image prompts. Please try again.", state="error")
                
                # Display images with improved layout
                if st.session_state.generated_images:
                    # Create a container with custom CSS class for targeted styling
                    image_display = st.container()
                    with image_display:
                        cols = st.columns(len(st.session_state.generated_images))
                        
                        for i, ((img_data, prompt), col) in enumerate(zip(zip(st.session_state.generated_images, st.session_state.image_prompts), cols)):
                            try:
                                # Convert base64 to image
                                image_bytes = base64.b64decode(img_data)
                                img = Image.open(BytesIO(image_bytes))
                                
                                # Display image in column with minimal wrapping
                                with col:
                                    # Display image without caption
                                    st.image(img, use_container_width=True)
                                    st.markdown(get_image_download_link(img, f"social_media_image_{i+1}.jpg", "Download Image"), unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error displaying image {i+1}: {str(e)}")

                
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
                            "Thread/Multiple Messages": 600,  # ~600 words (to be split into multiple messages)
                            "Custom Length": st.session_state.custom_word_count
                        }
                        
                        target_words = word_count_targets.get(length, 150)  # Default to 150 if not found
                        
                        # Additional constraints based on platform
                        platform_notes = ""
                        if platform == "Twitter":
                            platform_notes = "Respect Twitter's character limit (280 chars). Use hashtags appropriately."
                        elif platform == "LinkedIn":
                            platform_notes = "Professional tone with appropriate line breaks. Can include hashtags and tag people with @."
                        elif platform == "WhatsApp":
                            platform_notes = "More casual, conversational and direct. Can use emojis naturally."
                        
                        # Additional notes for thread format
                        thread_notes = ""
                        if length == "Thread/Multiple Messages":
                            if platform == "Twitter":
                                thread_notes = "Format as 4-5 connected tweets in a thread, with each under 280 characters."
                            else:
                                thread_notes = "Format as 3-4 separate messages that build on each other."
                        
                        # Create prompt for GPT
                        prompt = f"""
                        Create a compelling social media post about "{title}" for {platform}.
                        
                        Tone: {tone}
                        Target length: {target_words} words
                        {platform_notes}
                        {thread_notes}
                        
                        The post should be engaging, relevant to the platform, and formatted appropriately.
                        Add emojis where they fit naturally with the tone and platform.
                        For LinkedIn and Twitter, include 2-3 appropriate hashtags.
                        For LinkedIn, make sure it has good paragraph breaks for readability.
                        For WhatsApp, make it more personal and conversational.
                        
                        Return ONLY the post content with no explanations or additional text.
                        """
                        
                        # Make request to GPT
                        response = openai.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are an expert social media manager who creates engaging, platform-appropriate content."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=1500,
                            temperature=0.7
                        )
                        
                        # Extract response
                        generated_post = response.choices[0].message.content.strip()
                        st.session_state.generated_post = generated_post
                        st.session_state.edited_post = generated_post
                        
                        # No longer automatically generate images
                        # Just set the generated post and continue
                        st.session_state.generated_images = []  # Reset any existing images
                        st.session_state.image_prompts = []     # Reset any existing prompts
                        
                        # Refresh page to show results
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error generating post: {str(e)}")
            else:
                st.error("Please fill in all fields (Topic, Platform, Tone, and Length).")
        
        # Reset functionality
        if reset:
            # Reset all session state except API verification
            st.session_state.generated_post = ""
            st.session_state.edited_post = ""
            st.session_state.title = ""
            st.session_state.platform = ""
            st.session_state.tone = ""
            st.session_state.length = ""
            st.session_state.generated_images = []
            st.session_state.image_prompts = []
            st.rerun()

if __name__ == "__main__":
    try:
        openai.api_key = st.session_state.get('api_key', '')
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
