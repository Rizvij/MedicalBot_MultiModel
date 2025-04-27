import os
import platform
import subprocess
from gtts import gTTS
from dotenv import load_dotenv

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

input_text = "testing AI in health care autoplay!"
text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.mp3")
