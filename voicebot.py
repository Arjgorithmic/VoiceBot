import os
import gradio as gr
import openai
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the AI bot's personality prompt
PERSONALITY_PROMPT = (
    "Your name is Arjun P Dinesh. Recent Graduate of MSc AI ML from Christ University, Bangalore "
    "You are an AI Engineer with 9 months of internship experience. Do not use any emojis. "
    "You should be entertaining yet a bit formal. Here is a summary of your background:\n"
    " - Graduated in BCA Data Science.\n"
    " - Completed an MSc in AI and ML recently.\n"
    " - Developed machine AI solutions for document processing pipelines during your internship.\n"
    " - Managed your internship alongside your studies, demonstrating excellent time management.\n"
    " - You learn and adapt rapidly.\n"
    " - Although your calm and methodical approach might seem reserved, you are enthusiastic and innovative when tackling challenges—your quiet focus masks creative problem-solving and energetic drive.\n"
    " - You constantly push your limits by exploring new technologies and domains, actively seeking feedback and investing time in learning."
)

def fetch_ai_response(user_message):
    """
    Fetch the AI's response from the GPT-4 model using the personality prompt.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": PERSONALITY_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

def convert_text_to_speech(text_response):
    """
    Convert the provided text into speech using gTTS and save as an MP3 file.
    """
    tts = gTTS(text=text_response, lang="en", slow=False)
    audio_filename = "response.mp3"
    tts.save(audio_filename)
    return audio_filename

def process_text_input(user_input, chat_history):
    """
    Process text-based user input:
      - Validate input.
      - Get the AI's response.
      - Generate an audio file from the response.
      - Update the chat history.
    """
    if not user_input.strip():
        return chat_history, "Please enter a valid question.", None

    ai_response = fetch_ai_response(user_input)
    audio_output = convert_text_to_speech(ai_response)
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": ai_response})
    return chat_history, "", audio_output

def process_voice_input(audio_filepath, chat_history):
    """
    Process voice-based user input:
      - Validate and transcribe the audio.
      - Get the AI's response.
      - Generate an audio file from the response.
      - Update the chat history.
    """
    recognizer = sr.Recognizer()

    if not isinstance(audio_filepath, str):
        chat_history.append({"role": "assistant", "content": "Invalid audio input. Please try again."})
        return chat_history, None, None

    try:
        with sr.AudioFile(audio_filepath) as source:
            audio_data = recognizer.record(source)
        try:
            transcribed_text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            chat_history.append({"role": "assistant", "content": "Could not understand the audio. Please try again."})
            return chat_history, None, None
        except sr.RequestError as req_err:
            chat_history.append({"role": "assistant", "content": f"Speech recognition request failed: {str(req_err)}"})
            return chat_history, None, None

        ai_response = fetch_ai_response(transcribed_text)
        audio_output = convert_text_to_speech(ai_response)
        chat_history.append({"role": "user", "content": transcribed_text})
        chat_history.append({"role": "assistant", "content": ai_response})
        return chat_history, None, audio_output

    except Exception as ex:
        chat_history.append({"role": "assistant", "content": f"Error processing audio: {str(ex)}"})
        return chat_history, None, None

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
* { font-family: 'Roboto', sans-serif; }
body { background-color: #f5f5f5; }
.main-title { 
    color: #333333; 
    font-size: 32px; 
    font-weight: 700; 
    text-align: center; 
    margin-bottom: 20px; 
}
.gradio-chatbot { 
    border: 1px solid #cccccc; 
    border-radius: 8px; 
    background-color: #ffffff; 
    padding: 10px; 
}
.input-container { 
    display: flex; 
    flex-direction: column; 
    gap: 10px; 
    background-color: #e8e8e8; 
    padding: 15px; 
    border-radius: 8px; 
}
.input-label { 
    color: #555555; 
    font-size: 14px; 
}
.btn-text, .btn-voice { 
    background-color: #4caf50; 
    color: #ffffff; 
    font-size: 16px; 
    font-weight: 500; 
    border: none; 
    padding: 10px 15px; 
    border-radius: 8px; 
    cursor: pointer; 
}
.btn-text:hover, .btn-voice:hover { 
    background-color: #388e3c; 
}
.audio-display { 
    border: 1px dashed #2196f3; 
    margin-top: 20px; 
    padding: 10px; 
    border-radius: 8px; 
}
.gr-audio .audio-recorder { 
    background-color: #4caf50 !important; 
    border-radius: 50%; 
    color: white; 
}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<h1 class='main-title'>Arjun P Dinesh</h1>")
    
    # AI voice response at the top of the interface
    audio_output = gr.Audio(label="AI Voice Response", elem_classes="audio-display")
    
    
    # Row for voice input
    with gr.Row(elem_classes="input-container"):
        voice_input = gr.Audio(sources=["microphone"], type="filepath", label="Record or Upload Voice", elem_classes="input-label")
        btn_voice = gr.Button("Send Voice", elem_classes="btn-voice")
    
    # Chat history now positioned at the bottom
    chatbot = gr.Chatbot(label="Chat History", type="messages")
    

    btn_voice.click(fn=process_voice_input, inputs=[voice_input, chatbot], outputs=[chatbot, voice_input, audio_output])

# Launch the Gradio app
demo.launch(inbrowser=True)