import streamlit as st
from openai import OpenAI
import pyperclip
import base64
from io import BytesIO
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide",
)

# Custom CSS (abbreviated for clarity)
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4267B2;
        color: white;
    }
    /* Other styles preserved but abbreviated */
</style>
""", unsafe_allow_html=True)

# Helper function to download image
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}" class="download-btn">📥 {text}</a>'
    return href

# Function to generate image using DALL-E - SIMPLIFIED
def generate_dall_e_images(prompt, n=1):
    try:
        # Clean initialization with NO proxies
        client = OpenAI(api_key=st.session_state.api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=n,
            size="1024x1024",
            response_format="b64_json"
        )
        
        # Extract images
        images_data = []
        for data in response.data:
            images_data.append(data.b64_json)
        
        return images_data
    except Exception as e:
        st.error(f"Error generating images: {str(e)}")
        return []

# Function to generate image prompts - SIMPLIFIED
def generate_image_prompts(title, post_content, num_images=2):
    try:
        prompt = f"""
        Based on this social media post about "{title}", create {num_images} different image prompts for DALL-E 3.
        Make the prompts specific, visually appealing, and under 200 characters each.
        Format your response as a numbered list with just the prompts.

        Post content:
        {post_content}
        """
        
        # Clean initialization with NO proxies
        client = OpenAI(api_key=st.session_state.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at creating visual prompts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Parse response
        prompts_text = response.choices[0].message.content.strip()
        prompts = []
        for line in prompts_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line[0] == '-'):
                cleaned_line = line[1:].strip()
                if cleaned_line[0] in ['.', ')', '-', ':']:
                    cleaned_line = cleaned_line[1:].strip()
                prompts.append(cleaned_line)
        
        return prompts[:num_images]
    
    except Exception as e:
        st.error(f"Error generating image prompts: {str(e)}")
        return [f"Professional image related to {title}"] * num_images

# Initialize session state variables
if 'api_key_verified' not in st.session_state:
    st.session_state.api_key_verified = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
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

# Main application
def main():
    # Header
    st.title("📱 Social Media Post Generator")
    st.markdown("Create customized posts for LinkedIn, Twitter, and WhatsApp with your preferred tone and length.")

    # Step 1: API Key Authentication
    if not st.session_state.api_key_verified:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown('<h3>Step 1: API Key Authentication</h3>', unsafe_allow_html=True)
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        
        if st.button("Verify API Key"):
            if api_key:
                try:
                    # FIXED: Simple client initialization with no additional parameters
                    client = OpenAI(api_key=api_key)
                    
                    # Make a simple test request
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    
                    # If we get here, the API key is valid
                    st.session_state.api_key_verified = True
                    st.session_state.api_key = api_key
                    st.success("API Key verified successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to verify API key: {str(e)}")
            else:
                st.error("Please enter an API key.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Rest of the application (simplified for brevity)
    else:
        # Input form
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<h3>Step 2: Customize Your Post</h3>', unsafe_allow_html=True)
            
            title = st.text_input("Post Topic:", value=st.session_state.title)
            platform = st.selectbox("Select Platform:", ["", "LinkedIn", "Twitter", "WhatsApp"])
            tone = st.selectbox("Select Tone:", ["", "Professional", "Casual", "Humorous", "Inspirational"])
            length = st.selectbox("Select Length:", ["", "Short", "Medium", "Long", "Custom Length"])
            
            if length == "Custom Length":
                custom_word_count = st.number_input("Word count:", min_value=1, max_value=2000, value=100)
                st.session_state.custom_word_count = custom_word_count
            
            if st.button("Create Post"):
                if title and platform and tone and length:
                    with st.spinner("Generating post..."):
                        try:
                            # FIXED: Simple client initialization
                            client = OpenAI(api_key=st.session_state.api_key)
                            
                            # Determine target word count
                            word_targets = {"Short": 75, "Medium": 175, "Long": 400, "Custom Length": st.session_state.custom_word_count}
                            target_words = word_targets.get(length, 150)
                            
                            # Create the prompt
                            prompt = f"""
                            Create a social media post about "{title}" for {platform}.
                            Tone: {tone}
                            Target length: {target_words} words
                            """
                            
                            # Make the API call
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "You are an expert social media manager."},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=1500,
                                temperature=0.7
                            )
                            
                            # Save the result
                            generated_post = response.choices[0].message.content.strip()
                            st.session_state.generated_post = generated_post
                            st.session_state.edited_post = generated_post
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error generating post: {str(e)}")
                else:
                    st.error("Please fill in all fields.")
        
        # Display generated post
        with col2:
            if st.session_state.generated_post:
                st.markdown('<h3>Your Generated Post</h3>', unsafe_allow_html=True)
                edited_post = st.text_area("Edit if needed:", value=st.session_state.generated_post, height=250)
                st.session_state.edited_post = edited_post
                
                if st.button("Copy to Clipboard"):
                    try:
                        pyperclip.copy(edited_post)
                        st.success("Copied to clipboard!")
                    except:
                        st.info("Clipboard works when running locally.")
                
                # Image generation button
                if st.button("Generate Images"):
                    with st.spinner("Generating images..."):
                        image_prompts = generate_image_prompts(title, edited_post, num_images=1)
                        if image_prompts:
                            images = generate_dall_e_images(image_prompts[0], n=1)
                            if images:
                                st.session_state.generated_images = images
                                st.session_state.image_prompts = image_prompts
                                st.rerun()
                
                # Display images if any
                if st.session_state.generated_images:
                    for i, img_data in enumerate(st.session_state.generated_images):
                        try:
                            image_bytes = base64.b64decode(img_data)
                            img = Image.open(BytesIO(image_bytes))
                            st.image(img, use_container_width=True)
                            st.markdown(get_image_download_link(img, f"image_{i+1}.jpg", "Download Image"), unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error displaying image: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
