import os
import json
from typing import List, Dict
from anyio import sleep
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from dotenv import load_dotenv
from knowledge.info import info as knowledge_profile
from google.genai.types import GenerateContentConfig

load_dotenv()

app = FastAPI()

# Persona/system instruction for the chatbot
SYSTEM_PROMPT = f"You are acting as Yash Rathore. You are answering questions on Yash Rathore's website, \
particularly questions related to Yash Rathore's career, background, skills and experience. \
Your responsibility is to represent Yash Rathore for interactions on the website as faithfully as possible. \
You are given a summary of Yash Rathore's background which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to a question, say that politely steering the conversation to what you know."

KNOWLEDGE_CONTEXT = "Knowledge base (from knowledge/):\n" + knowledge_profile

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.get("/")
async def root():
    return {"message": "Personal Website Backend is running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=GenerateContentConfig(
            system_instruction=f"{SYSTEM_PROMPT}\n\n{KNOWLEDGE_CONTEXT}"
        ),
    )
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_text()

            try:
                # Send message to Gemini and get streaming response
                response = chat.send_message_stream(data)
                assistant_reply: List[str] = []
                
                for chunk in response:
                    if chunk.text:
                        await sleep(0.1)  # Optional: simulate delay for streaming effect
                        print("Sending chunk:", chunk.text)
                        await websocket.send_text(chunk.text)
                        assistant_reply.append(chunk.text)
                
                # Send a special token to indicate end of stream if needed
                # await websocket.send_text("[DONE]")
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota/resource exhausted error
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    error_message = {
                        "type": "error",
                        "code": "QUOTA_EXCEEDED",
                        "message": "API quota exceeded. Please try again later.",
                        "details": error_str
                    }
                else:
                    error_message = {
                        "type": "error",
                        "code": "API_ERROR",
                        "message": f"An error occurred: {error_str}",
                        "details": error_str
                    }
                await websocket.send_text(json.dumps(error_message))
                print(f"API Error: {e}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")
        try:
            error_message = {
                "type": "error",
                "code": "UNEXPECTED_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e)
            }
            await websocket.send_text(json.dumps(error_message))
        except:
            pass
        await websocket.close()
