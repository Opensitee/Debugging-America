import os
import json
import streamlit as st
from PIL import Image
from io import BytesIO
from tempfile import NamedTemporaryFile
import pytesseract
import random

# Specify the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Replace with your actual Tesseract path

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools

# System Prompt for AI
SYSTEM_PROMPT = """
You are an expert Food Product Analyst specializing in nutrition and health effects of ingredients.
Your job is to analyze product ingredients and assess their impact.
Consider:
- The nutritional impact of the product.
- Artificial additives, preservatives, and harmful chemicals.
- Provide a clear, science-backed summary including risks and better alternatives.
* Also rate the ingredients with a 1-5 star rating.
* Use emojis to make the analysis more engaging and fun.
"""

# Instructions for the AI agent
INSTRUCTIONS = """
* Analyze the list of ingredients carefully.
* Highlight harmful additives, preservatives, and chemicals.
* Explain the nutritional value and potential risks.
* Suggest healthier alternatives if necessary.
* Rate the ingredients from 1-5 stars.
* Make the explanation fun, engaging, and easy to understand by using emojis and bold important terms.
"""

# Initialize AI agent
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=st.secrets["TAVILY"]["API_KEY"])],  # Use Tavily API key from secrets
        markdown=True,
    )

# Extract text from the image using Tesseract OCR
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)  # Extract text
    return text

# Function to generate a random 1-5 star rating (to simulate the rating process)
def generate_rating():
    return random.randint(1, 5)

# Analyze ingredients considering the user's health problem (optional)
def analyze_ingredients(image_path, health_problem=None):
    extracted_text = extract_text_from_image(image_path)  # Extract ingredients
    
    # If no health problem is provided, analyze the ingredients generally
    if not health_problem:
        health_problem = "general product analysis"

    agent = get_agent()
    response = agent.run(f"""
        The user has a health problem: {health_problem}
        Analyze the ingredients: {extracted_text}
        Identify any harmful ingredients, nutritional impacts, and provide a 1-5 star rating.
        Suggest healthier alternatives if needed.
        Make sure to include **emojis** and **bold important terms** to make the summary more fun and engaging!
    """)
    
    # Adding a 1-5 star rating to the analysis result
    rating = generate_rating()
    formatted_response = f"🌟 **Rating:** {rating} / 5 🌟\n\n"
    
    # Add the emojis and bold important words
    response_content = response.content
    response_content = response_content.replace("preservatives", "**preservatives** ⚠️")
    response_content = response_content.replace("chemicals", "**chemicals** 🧪")
    response_content = response_content.replace("additives", "**additives** 🍭")
    response_content = response_content.replace("healthier alternatives", "🍏 **healthier alternatives** 🍎")
    
    # Add some fun emojis throughout the summary
    response_content += f"\n\n🎉 Overall Rating: {rating} ⭐\n\n✨ Stay healthy and enjoy your food! ✨"

    # Include response with emojis and bolding
    formatted_response += response_content
    return formatted_response

# Save uploaded file temporarily
def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        return tmp_file.name

# Streamlit UI
def main():
    st.title("Debugging America 🍔⚠️🕵 ")
    "Created by OpenSite.co "
    "Upload any food, snack, or product ingredient list and find out the what the secret chemical names actually mean for you 🧪 "
    "*Note: AI may be inaccurate at times*"
    # Upload Image or Take a Photo (Mobile-friendly)
    uploaded_file = st.file_uploader(
        "Upload an image of the ingredient list 📤", 
        type=["jpg", "jpeg", "png"],
        help="Upload an image of the ingredient list from your snack/food product. "
    )

   
    # Get Health Problem Input
    health_problem = st.text_input("What health issue do you have? 🩺 ex: acne, anxiety, depression, high blood pressure, etc (Optional)")

    # Use the uploaded image or camera input
    if uploaded_file :
        
        image = Image.open(uploaded_file)
        
        st.image(image, caption="Uploaded Image", use_container_width=False, width=300)

        # Save uploaded file temporarily
        if uploaded_file:
            temp_path = save_uploaded_file(uploaded_file)
       
        
        if st.button("🔍 Analyze Ingredients & Health Impact"):
            st.write("Extracting ingredients...")
            analysis_result = analyze_ingredients(temp_path, health_problem)
            st.write(analysis_result)
            os.unlink(temp_path)

    elif not uploaded_file and health_problem:
        st.warning("Please upload an image or take a photo of your food ingredients to analyze.")

if __name__ == "__main__":
    main()

