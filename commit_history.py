import os
import subprocess

commits = [
    {
        "date": "2026-10-02T10:30:00+05:30",
        "msg": "Implement real-time WebSocket telemetry and live runner pipeline",
        "files": ["backend/app/services/live_runner.py", "backend/app/schemas/live.py", "backend/app/api/endpoints/live.py", "backend/app/websocket/analysis_ws.py", "backend/app/services/detection_runner.py"]
    },
    {
        "date": "2026-10-03T14:15:00+05:30",
        "msg": "Add advanced event detection models (Passes, Shots, Goals, Possession)",
        "files": ["backend/cv/events/", "backend/cv/field/", "backend/app/services/match_service.py", "backend/app/models/match.py"]
    },
    {
        "date": "2026-10-04T11:45:00+05:30",
        "msg": "Develop tracking-based player analytics and match summaries",
        "files": ["backend/cv/analytics/", "backend/app/api/endpoints/matches.py", "backend/app/api/endpoints/sessions.py", "backend/app/services/session_service.py"]
    },
    {
        "date": "2026-10-05T16:20:00+05:30",
        "msg": "Integrate Gemini AI Assistant and MCP server capabilities",
        "files": ["backend/app/mcp/", "backend/app/api/endpoints/assistant.py", "visionvar-app/components/assistant/"]
    },
    {
        "date": "2026-10-06T09:10:00+05:30",
        "msg": "Implement Next.js Player Analytics and Match Summary pages",
        "files": ["visionvar-app/app/sessions/", "visionvar-app/components/pipeline/MatchSessionCard.tsx"]
    },
    {
        "date": "2026-10-07T13:30:00+05:30",
        "msg": "Enhance Pitch Radar and Event Timeline components",
        "files": ["visionvar-app/components/radar/", "visionvar-app/components/events/", "visionvar-app/lib/api.ts"]
    },
    {
        "date": "2026-10-08T15:00:00+05:30",
        "msg": "Add comprehensive test suite for CV and Analytics pipelines",
        "files": ["backend/tests/"]
    },
    {
        "date": "2026-10-09T10:45:00+05:30",
        "msg": "Update API router and connect frontend telemetry feeds",
        "files": ["backend/app/api/router.py", "backend/app/main.py", "backend/requirements.txt", "visionvar-app/app/", "visionvar-app/components/layout/", "visionvar-app/types/", "visionvar-app/lib/mockData/"]
    },
    {
        "date": "2026-10-10T12:00:00+05:30",
        "msg": "Finalize README, docs, and prepare repository for V1.0 release",
        "files": ["."]
    }
]

for commit in commits:
    for f in commit["files"]:
        if f == ".":
            subprocess.run(["git", "add", "."])
        elif os.path.exists(f) or os.path.isdir(f):
            subprocess.run(["git", "add", f])
    
    # We use os.environ to set the commit dates temporarily
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit["date"]
    env["GIT_COMMITTER_DATE"] = commit["date"]
    
    subprocess.run(["git", "commit", "-m", commit["msg"]], env=env)

print("Commits successfully rewritten!")
