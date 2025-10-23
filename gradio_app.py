from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
import tempfile
import shutil
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
6. Generate a formal prescription when requested

Guidelines:
- Keep responses concise but informative
- Use natural, conversational language
- Avoid medical jargon unless necessary
- Always err on the side of caution
- Recommend professional medical consultation for serious concerns
- Do not make definitive diagnoses without proper medical examination
- Focus on education and guidance rather than treatment
- When generating prescriptions, include:
  * Patient's name and date
  * Diagnosis
  * Medications (if any)
  * Dosage instructions
  * Follow-up recommendations
  * Doctor's signature

Format your response as a natural conversation, avoiding bullet points or special characters.
"""

# Global variable to store conversation history
conversation_history = []

def generate_prescription(doctor_response, patient_name="Patient"):
    """Generate a PDF prescription from the doctor's response."""
    try:
        # Create a temporary file for the prescription
        temp_dir = tempfile.mkdtemp()
        prescription_path = os.path.join(temp_dir, "prescription.pdf")
        
        # Create the PDF
        doc = SimpleDocTemplate(prescription_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph("Medical Prescription", header_style))
        
        # Add date and patient info
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", date_style))
        story.append(Paragraph(f"Patient: {patient_name}", date_style))
        story.append(Spacer(1, 20))
        
        # Add prescription content
        content_style = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )
        story.append(Paragraph(doctor_response, content_style))
        
        # Add footer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=30
        )
        story.append(Spacer(1, 50))
        story.append(Paragraph("This is a computer-generated prescription for educational purposes only.", footer_style))
        story.append(Paragraph("Please consult with a healthcare professional for proper medical advice.", footer_style))
        
        # Build the PDF
        doc.build(story)
        return prescription_path
        
    except Exception as e:
        logging.error(f"Error generating prescription: {str(e)}")
        return None

def process_inputs(audio_filepath, image_filepaths, chat_history, patient_name):
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

        # Process multiple images
        if image_filepaths:
            try:
                # Combine all image analyses
                all_analyses = []
                for image_path in image_filepaths:
                    encoded_image = encode_image(image_path)
                    conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
                    analysis = analyze_image_with_query(
                        query=system_prompt + "\nPrevious conversation:\n" + conversation_context,
                        encoded_image=encoded_image,
                        model="meta-llama/llama-4-maverick-17b-128e-instruct"
                    )
                    all_analyses.append(analysis)
                
                # Combine all analyses into one response
                doctor_response = "\n\n".join(all_analyses)
            except Exception as e:
                doctor_response = f"Error analyzing images: {str(e)}"
        else:
            # If no images, still include conversation history
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            doctor_response = analyze_image_with_query(
                query=system_prompt + "\nPrevious conversation:\n" + conversation_context,
                encoded_image=None,
                model="meta-llama/llama-4-maverick-17b-128e-instruct"
            )

        # Add doctor's response to conversation history
        conversation_history.append({"role": "assistant", "content": doctor_response})
        chat_history.append({"role": "assistant", "content": doctor_response})

        # Generate prescription
        prescription_path = generate_prescription(doctor_response, patient_name)

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
                    return chat_history, chat_history, None, prescription_path, f"Error generating voice response: {str(gtts_error)}"
            else:
                return chat_history, chat_history, None, prescription_path, f"Error generating voice response: {str(e)}"

        # Play the audio file
        try:
            from doctor_voice import play_audio
            play_audio(temp_response_path)
        except Exception as e:
            return chat_history, chat_history, temp_response_path, prescription_path, f"Error playing audio: {str(e)}"

        return chat_history, chat_history, temp_response_path, prescription_path, ""

    except Exception as e:
        return chat_history, chat_history, None, None, f"An error occurred: {str(e)}"

# Create the interface with improved UI
with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown("# AI Medical Assistant")
    gr.Markdown("""Welcome to your AI Medical Assistant. This tool is for educational purposes only and should not replace professional medical advice.
    
    How to use:
    1. For your first question:
       - Enter your name
       - Click the microphone button to record your symptoms or concerns
       - Upload one or more images of your condition
       - Click Submit to receive a medical assessment
    
    2. To continue the conversation:
       - After the doctor responds, click the microphone button again
       - Record your follow-up question or response
       - Click Submit
       - The AI doctor will remember your previous conversation
    
    3. The conversation history will show your entire interaction
    4. A prescription will be generated automatically
    
    Note: Always consult with a healthcare professional for proper medical advice.""")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input section
            patient_name = gr.Textbox(label="Your Name", placeholder="Enter your name")
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Click to Record Your Response", interactive=True)
            image_input = gr.File(file_count="multiple", label="Upload images of your condition (optional)", file_types=["image"])
            submit_btn = gr.Button("Submit", variant="primary")
            clear_btn = gr.Button("Clear Recording", variant="secondary")
        
        with gr.Column(scale=1):
            # Output section
            chatbot = gr.Chatbot(label="Conversation History", height=400, type="messages")
            audio_output = gr.Audio(label="Doctor's Voice Response")
            prescription_output = gr.File(label="Download Prescription")
            status = gr.Textbox(label="Status/Error Messages")
    
    chat_history = gr.State([])
    
    def clear_audio():
        return None
    
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input, chat_history, patient_name],
        outputs=[chatbot, chat_history, audio_output, prescription_output, status]
    )
    
    clear_btn.click(
        fn=clear_audio,
        inputs=[],
        outputs=[audio_input]
    )

if __name__ == "__main__":
    iface.launch(debug=True, share=True)

#http://127.0.0.1:7860