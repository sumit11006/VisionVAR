
## VisionVAR Phase 8: Live Analysis Pipeline

**Architecture:**
- Introduced `LiveAnalysisRunner` in `backend/app/services/live_runner.py`.
- Consumes webcam, network RTSP, or local video frames in a non-blocking background task.
- Executes the standard CV pipeline (Detection -> Tracking -> Offside -> Analytics) on streaming bytes.
- Websocket emits FPS, frame counts, and live tracking metadata dynamically without waiting for full MP4 conclusion.

## VisionVAR Phase 9 & 10: MCP AI Assistant (Gemini)

**Architecture:**
- Uses **Google Gemini** (`gemini-2.5-flash`) via the `google-genai` SDK as the intelligence layer.
- Secured backend-only `GEMINI_API_KEY` implementation avoiding frontend exposure.
- Utilizes the **Model Context Protocol (MCP)** standard to expose 9 distinct read-only data extraction tools (e.g. `get_match_summary`, `get_offside_incidents`).
- Enforces strict AI rules: No statistical fabrication, no claiming professional accuracy, handles "INSUFFICIENT EVIDENCE" appropriately.

**Usage:**
- Ask the assistant: "What was the match summary?", "Show me the offside candidates", or "What's the status of the live analysis?"
- The AI dynamically executes backend tools to provide context-aware reporting.
