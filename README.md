# AI Medical Assistant

A multimodal AI medical assistant that can analyze images, process voice inputs, and provide medical assessments with voice responses.

## Features

- Image analysis for medical conditions
- Voice input processing
- Text-to-speech responses
- User-friendly web interface
- Real-time medical assessments

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- PortAudio installed on your system
- Groq API key
- ElevenLabs API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-medical-assistant.git
cd ai-medical-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Usage

1. Start the application:
```bash
python gradio_app.py
```

2. Open your web browser and navigate to:
```
http://localhost:7860
```

3. Use the interface to:
   - Record your symptoms or concerns using the microphone
   - Upload images of your condition (optional)
   - Receive medical assessments with voice responses

## Important Notes

- This application is for educational purposes only
- Always consult with healthcare professionals for proper medical advice
- The AI's responses should not be considered as definitive medical diagnoses
- Keep your API keys secure and never share them

## Troubleshooting

1. If you encounter audio recording issues:
   - Ensure your microphone is properly connected and configured
   - Check if PortAudio is correctly installed
   - Verify that FFmpeg is in your system PATH

2. If you encounter image processing issues:
   - Ensure the image file is in a supported format (JPEG, PNG)
   - Check if the image file is not corrupted
   - Verify that you have sufficient system memory

3. If you encounter API-related issues:
   - Verify your API keys are correct
   - Check your internet connection
   - Ensure you have sufficient API credits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



