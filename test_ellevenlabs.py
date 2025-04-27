import os
import platform
import subprocess
from gtts import gTTS
from dotenv import load_dotenv
load_dotenv()


import elevenlabs
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def text_to_speech_with_elevenlabs(input_text, output_filepath):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.generate(
        text=input_text,
        voice="Aria",  # Or "Sarah"
        output_format="mp3_22050_32",
        model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)

    os_name = platform.system()
    try:
        if os_name == "Windows":
            os.startfile(output_filepath)
        elif os_name == "Darwin":
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Linux":
            subprocess.run(['mpg123', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


# Example usage (uncomment one of them)
input_text = "Hi! This is your AI Doctor, powered by ElevenLabs!"
# text_to_speech_with_gtts(input_text, "gtts_testing_autoplay.mp3")
text_to_speech_with_elevenlabs(input_text, "elevenlabs_testing_autoplay.mp3")