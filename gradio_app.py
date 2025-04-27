from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import tempfile
import shutil
from datetime import datetime

from doctor import encode_image, analyze_image_with_query
from patient_voice import record_audio, transcribe_with_groq
from doctor_voice import text_to_speech_with_elevenlabs

# Enhanced system prompt for better medical responses
system_prompt = """
You are a compassionate and experienced medical doctor. Although this is for educational purposes, respond as if you're advising a real patient.
Your role is to:
1. Carefully analyze any provided images for medical conditions
2. Listen to the patient's concerns and symptoms
3. Provide a professional medical assessment
4. Suggest appropriate next steps or remedies
5. Maintain a caring and professional tone

Guidelines:
- Keep responses concise but informative
- Use natural, conversational language
- Avoid medical jargon unless necessary
- Always err on the side of caution
- Recommend professional medical consultation for serious concerns
- Do not make definitive diagnoses without proper medical examination
- Focus on education and guidance rather than treatment

Format your response as a natural conversation, avoiding bullet points or special characters.
"""

# Global variable to store conversation history
conversation_history = []

def process_inputs(audio_filepath, image_filepath, chat_history):
    global conversation_history
    
    try:
        # Create a temporary directory for audio files
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, "temp_audio.mp3")
        temp_response_path = os.path.join(temp_dir, "doctor_response.mp3")
        
        # Process audio input
        if audio_filepath:
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
                audio_filepath=audio_filepath,
                stt_model="whisper-large-v3"
            )
        else:
            speech_to_text_output = "No audio input provided."

        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": speech_to_text_output})
        chat_history.append({"role": "user", "content": speech_to_text_output})

        # Process image input
        if image_filepath:
            try:
                encoded_image = encode_image(image_filepath)
                # Include conversation history in the query
                conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
                doctor_response = analyze_image_with_query(
                    query=system_prompt + "\nPrevious conversation:\n" + conversation_context,
                    encoded_image=encoded_image,
                    model="meta-llama/llama-4-maverick-17b-128e-instruct"
                )
            except Exception as e:
                doctor_response = f"Error analyzing image: {str(e)}"
        else:
            # If no image, still include conversation history
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            doctor_response = analyze_image_with_query(
                query=system_prompt + "\nPrevious conversation:\n" + conversation_context,
                encoded_image=None,
                model="meta-llama/llama-4-maverick-17b-128e-instruct"
            )

        # Add doctor's response to conversation history
        conversation_history.append({"role": "assistant", "content": doctor_response})
        chat_history.append({"role": "assistant", "content": doctor_response})

        # Try ElevenLabs first, fall back to gTTS if quota exceeded
        try:
            text_to_speech_with_elevenlabs(
                input_text=doctor_response,
                output_filepath=temp_response_path
            )
        except Exception as e:
            if "quota_exceeded" in str(e):
                try:
                    from doctor_voice import text_to_speech_with_gtts
                    text_to_speech_with_gtts(
                        input_text=doctor_response,
                        output_filepath=temp_response_path
                    )
                except Exception as gtts_error:
                    return chat_history, chat_history, None, f"Error generating voice response: {str(gtts_error)}"
            else:
                return chat_history, chat_history, None, f"Error generating voice response: {str(e)}"

        # Play the audio file
        try:
            from doctor_voice import play_audio
            play_audio(temp_response_path)
        except Exception as e:
            return chat_history, chat_history, temp_response_path, f"Error playing audio: {str(e)}"

        return chat_history, chat_history, temp_response_path, ""

    except Exception as e:
        return chat_history, chat_history, None, f"An error occurred: {str(e)}"

# Create the interface with improved UI
with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown("# AI Medical Assistant")
    gr.Markdown("""Welcome to your AI Medical Assistant. This tool is for educational purposes only and should not replace professional medical advice.
    
    How to use:
    1. For your first question:
       - Click the microphone button to record your symptoms or concerns
       - Optionally upload an image of your condition
       - Click Submit to receive a medical assessment
    
    2. To continue the conversation:
       - After the doctor responds, click the microphone button again
       - Record your follow-up question or response
       - Click Submit
       - The AI doctor will remember your previous conversation
    
    3. The conversation history will show your entire interaction
    
    Note: Always consult with a healthcare professional for proper medical advice.""")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input section
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Click to Record Your Response", interactive=True)
            image_input = gr.Image(type="filepath", label="Upload an image of your condition (optional)")
            submit_btn = gr.Button("Submit", variant="primary")
            clear_btn = gr.Button("Clear Recording", variant="secondary")
        
        with gr.Column(scale=1):
            # Output section
            chatbot = gr.Chatbot(label="Conversation History", height=400, type="messages")
            audio_output = gr.Audio(label="Doctor's Voice Response")
            status = gr.Textbox(label="Status/Error Messages")
    
    chat_history = gr.State([])
    
    def clear_audio():
        return None
    
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input, chat_history],
        outputs=[chatbot, chat_history, audio_output, status]
    )
    
    clear_btn.click(
        fn=clear_audio,
        inputs=[],
        outputs=[audio_input]
    )

if __name__ == "__main__":
    iface.launch(debug=True, share=True)

#http://127.0.0.1:7860