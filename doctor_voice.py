import os
import platform
import subprocess
from gtts import gTTS
from dotenv import load_dotenv
import logging
import elevenlabs
from elevenlabs.client import ElevenLabs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def text_to_speech_with_gtts(input_text, output_filepath):
    language = "en"

    # Generate the speech
    audioobj = gTTS(text=input_text, lang=language, slow=False)
    audioobj.save(output_filepath)

    os_name = platform.system()
    try:
        if os_name == "Windows":
            os.startfile(output_filepath)  # ✅ FIXED: Autoplay works here
        elif os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Linux":
            subprocess.run(['mpg123', output_filepath])  # Ensure mpg123 is installed
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

def text_to_speech_with_elevenlabs(input_text, output_filepath):
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        input_text (str): The text to convert to speech
        output_filepath (str): Path to save the audio file
        
    Returns:
        str: Path to the generated audio file
        
    Raises:
        Exception: If there's an error during text-to-speech conversion
    """
    try:
        if not input_text:
            raise ValueError("Input text cannot be empty")
            
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Generate the audio
        audio = client.generate(
            text=input_text,
            voice="Aria",  # Professional female voice
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        
        # Save the audio file
        elevenlabs.save(audio, output_filepath)
        logging.info(f"Audio saved to {output_filepath}")
        
        # Play the audio file
        play_audio(output_filepath)
        
        return output_filepath
        
    except Exception as e:
        logging.error(f"Error in text-to-speech conversion: {str(e)}")
        raise

def play_audio(filepath):
    """
    Play an audio file using the appropriate system command.
    
    Args:
        filepath (str): Path to the audio file to play
        
    Raises:
        OSError: If the operating system is not supported
        Exception: If there's an error playing the audio
    """
    try:
        os_name = platform.system()
        
        if os_name == "Windows":
            os.startfile(filepath)
        elif os_name == "Darwin":  # macOS
            subprocess.run(['afplay', filepath])
        elif os_name == "Linux":
            subprocess.run(['mpg123', filepath])
        else:
            raise OSError(f"Unsupported operating system: {os_name}")
            
    except Exception as e:
        logging.error(f"Error playing audio: {str(e)}")
        raise