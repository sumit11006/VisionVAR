import os
from dotenv import load_dotenv
load_dotenv()
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.match import Match
from backend.app.models.session import AnalysisSession
from backend.app.models.video import Video
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Create Match
m = Match(
    id='UCL-2024-MCI-RMA-F',
    home_team_code='MCI',
    home_team_name='Manchester City',
    away_team_code='RMA',
    away_team_name='Real Madrid',
    competition='UEFA Champions League — Final',
    status='LIVE',
    score_home=0,
    score_away=0,
    clock='00:00'
)

# Create Video
v = Video(
    id='vid_ucl_action_01',
    filename='ucl_match_action.mp4',
    file_path='data/uploads/ucl_match_action.mp4',
    status='analyzed',
    uploaded_at=datetime.now(timezone.utc)
)

# Create Session
s = AnalysisSession(
    id='UCL-2024-MCI-RMA-F',
    match_id='UCL-2024-MCI-RMA-F',
    video_id='vid_ucl_action_01',
    status='READY',
    created_at=datetime.now(timezone.utc),
    progress_percent=100
)

db.merge(m)
db.merge(v)
db.merge(s)
db.commit()
print("Supabase Data seeded successfully!")
