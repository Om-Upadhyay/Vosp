import os
import uuid
import asyncio
from edge_tts import Communicate
import pygame

def speak(text):
    try:
        filename = f"temp_{uuid.uuid4().hex}.mp3"
        communicate = Communicate(text, voice="en-IN-NeerjaNeural")

        async def generate_and_play():
            await communicate.save(filename)
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            pygame.mixer.quit()
            os.remove(filename)

        asyncio.run(generate_and_play())

    except Exception as e:
        print(f"TTS error: {e}")
