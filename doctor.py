import os
from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY=os.environ.get("GROQ_API_KEY")

#Convert image from bits to str (required format)
import base64



image_path="image.jpg"
image_file=open(image_path, "rb")
encoded_image=base64.b64encode(image_file.read()).decode('utf-8')

#Setup Multimodal LLM 
from groq import Groq

query="Is there something wrong with my face?"
model="llama-3.2-90b-vision-preview"


client=Groq()  
messages=[
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
        }]
chat_completion=client.chat.completions.create(
        messages=messages,
        model=model
    )

print(chat_completion.choices[0].message.content)