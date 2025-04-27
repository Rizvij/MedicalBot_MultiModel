import os
from dotenv import load_dotenv
load_dotenv()
import base64
from groq import Groq
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

def encode_image(image_path):
    """
    Encode an image file to base64 string.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image string
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the file is not a valid image
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        logging.error(f"Error encoding image: {str(e)}")
        raise

def analyze_image_with_query(query, model, encoded_image):
    """
    Analyze an image using the Groq API with a given query.
    
    Args:
        query (str): The query to analyze the image with
        model (str): The model to use for analysis
        encoded_image (str): Base64 encoded image string
        
    Returns:
        str: The analysis response from the model
        
    Raises:
        Exception: If there's an error in the API call
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    },
                ],
            }
        ]
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.7,  # Add some randomness to responses
            max_tokens=500    # Limit response length
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        raise