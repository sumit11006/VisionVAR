from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
load_dotenv()
from google import genai
from backend.app.mcp.server import (
    get_match_summary,
    get_team_analytics,
    get_player_analytics,
    get_events,
    get_offside_incidents,
    get_formation,
    get_player_position,
    get_live_status,
    get_video_frame,
)
from backend.app.core.database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    match_id: str = None
    session_id: str = None

# We can reuse the Python functions from our MCP Server definition
AVAILABLE_TOOLS = {
    "get_match_summary": get_match_summary,
    "get_team_analytics": get_team_analytics,
    "get_player_analytics": get_player_analytics,
    "get_events": get_events,
    "get_offside_incidents": get_offside_incidents,
    "get_formation": get_formation,
    "get_player_position": get_player_position,
    "get_live_status": get_live_status,
    "get_video_frame": get_video_frame,
}

SYSTEM_PROMPT = """
You are the VisionVAR AI Assistant, an AI layer over the VisionVAR Computer Vision pipeline.
You MUST use the provided tools to fetch real data. DO NOT guess, fabricate, or hallucinate data.
Rules:
- Be precise. State "VisionVAR observed..." or "The AI assessment indicates..."
- Use the exact terms: "Track ID" (not "Player Name", since Re-ID is missing).
- Preserve uncertainty states: If a tool returns "INSUFFICIENT EVIDENCE", report that. Do NOT call it a confirmed offside.
- If data is missing, clearly state that it is unavailable.
- Do NOT claim official VAR or referee decisions.
"""

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest, db = Depends(get_db)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "response": "Error: GEMINI_API_KEY is not set in the environment. MCP tools are ready, but the LLM cannot be reached.",
            "tools_used": []
        }

    client = genai.Client(api_key=api_key)
    
    # Inject context automatically if available
    context = ""
    resolved_match_id = req.match_id
    if req.session_id and not resolved_match_id:
        from backend.app.models.session import AnalysisSession
        session = db.query(AnalysisSession).filter(AnalysisSession.id == req.session_id).first()
        if session and session.match_id:
            resolved_match_id = session.match_id

    if resolved_match_id:
        context += f" Current Match ID context: {resolved_match_id}."
    if req.session_id:
        context += f" Current Session ID context: {req.session_id}."
        
    config = {
        "tools": list(AVAILABLE_TOOLS.values()),
        "system_instruction": SYSTEM_PROMPT + context,
        "temperature": 0.0
    }

    tools_used = []
    
    try:
        # Use gemini-3.8-flash as the standard capable tool-calling model
        chat = client.chats.create(model="gemini-3.8-flash", config=config)
        
        response = chat.send_message(req.message)
        
        # When tools are called, the chat history will have function calls.
        # google-genai handles tool calling automatically if we provide the functions.
        # But we need to extract the tools used from the parts.
        for step in chat.get_history():
            for part in step.parts:
                if part.function_call:
                    tools_used.append({
                        "tool": part.function_call.name,
                        "args": {k: v for k, v in part.function_call.args.items()}
                    })

        return {
            "response": response.text,
            "tools_used": tools_used
        }
    except Exception as e:
        return {
            "response": f"Assistant Error: {str(e)}",
            "tools_used": tools_used
        }
