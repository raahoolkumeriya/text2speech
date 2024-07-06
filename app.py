from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS
import os
import uuid
import logging
from tempfile import NamedTemporaryFile, gettempdir

app = FastAPI()

class TextToSpeechRequest(BaseModel):
    text: str
    lang: str = "en"  # Default language is English

@app.post("/text-to-speech/")
async def generate_speech(request: TextToSpeechRequest):
    try:
        logging.info(f"Generating speech for text: {request.text} in language: {request.lang}")
        tts = gTTS(text=request.text, lang=request.lang)

        with NamedTemporaryFile(delete=False, suffix=".mp3", dir=gettempdir()) as temp_file:
            temp_file_name = temp_file.name
            logging.info(f"Saving file to: {temp_file_name}")
            tts.save(temp_file_name)

        # Print the directory contents for debugging
        temp_dir = gettempdir()
        logging.info(f"Contents of the temporary directory ({temp_dir}): {os.listdir(temp_dir)}")

        # Ensure the file was created
        if not os.path.exists(temp_file_name):
            raise RuntimeError(f"File at path {temp_file_name} does not exist.")

        logging.info(f"File exists: {temp_file_name}")
        return FileResponse(temp_file_name, media_type='audio/mpeg', filename=os.path.basename(temp_file_name))

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    #finally:
        # Cleanup the file if it exists
    #    if 'temp_file_name' in locals() and os.path.exists(temp_file_name):
    #        os.remove(temp_file_name)
    #        logging.info(f"File removed: {temp_file_name}")

if __name__ == "__main__":
    import uvicorn
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
