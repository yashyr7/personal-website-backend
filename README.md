# Personal Website Backend

This is a FastAPI project for the personal website backend.

## Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Chatbot WebSocket

The chatbot is available via WebSocket at `/ws/chat`. It uses Google Gemini (`gemini-2.5-flash`) to provide real-time streaming responses. Each WebSocket connection keeps an in-memory conversation history for the duration of the session.

## Running the application

```bash
uvicorn main:app --reload
```
