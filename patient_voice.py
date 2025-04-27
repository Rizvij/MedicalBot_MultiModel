import os
from dotenv import load_dotenv
load_dotenv()

#Setup Audio recorder (ffmpeg & portaudio)
# ffmpeg, portaudio, pyaudio
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Record audio from the microphone and save it as an MP3 file.
    
    Args:
        file_path (str): Path to save the recorded audio file
        timeout (int): Maximum time to wait for a phrase to start (in seconds)
        phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds)
        
    Returns:
        bool: True if recording was successful, False otherwise
        
    Raises:
        Exception: If there's an error during recording
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            
            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            # Convert the recorded audio to an MP3 file
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Audio saved to {file_path}")
            return True

    except sr.WaitTimeoutError:
        logging.error("No speech detected within the timeout period")
        return False
    except Exception as e:
        logging.error(f"An error occurred during recording: {str(e)}")
        return False

audio_filepath="patient_voice_test_for_patient.mp3"
record_audio(file_path=audio_filepath)

#Setup Speech to text–STT–model for transcription
stt_model="whisper-large-v3"

def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """
    Transcribe audio using the Groq API.
    
    Args:
        stt_model (str): The speech-to-text model to use
        audio_filepath (str): Path to the audio file to transcribe
        GROQ_API_KEY (str): Groq API key
        
    Returns:
        str: The transcribed text
        
    Raises:
        Exception: If there's an error during transcription
    """
    try:
        if not os.path.exists(audio_filepath):
            raise FileNotFoundError(f"Audio file not found: {audio_filepath}")
            
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
            
        return transcription.text
        
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        raise
