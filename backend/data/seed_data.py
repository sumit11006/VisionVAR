from sqlalchemy.orm import Session
from backend.app.models.match import Match
from backend.app.models.player import Player
from backend.app.models.event import MatchEvent
from backend.app.models.session import AnalysisSession


def seed_database(db: Session):
    # Check if already seeded
    existing_match = db.query(Match).filter(Match.id == "UCL-2024-MCI-RMA-F").first()
    if existing_match:
        return

    # 1. Primary Match
    match = Match(
        id="UCL-2024-MCI-RMA-F",
        home_team_code="MCI",
        home_team_name="Manchester City",
        away_team_code="RMA",
        away_team_name="Real Madrid",
        score_home=2,
        score_away=1,
        clock="67:24",
        period="2H",
        competition="UEFA Champions League",
        venue="Etihad Stadium",
        status="LIVE",
        feed_spec="4K RAW 120FPS",
        latency_ms=12,
    )
    db.add(match)

    # 2. Additional Matches for sessions
    match_bay = Match(
        id="UCL-2024-BAY-ARS-QF",
        home_team_code="BAY",
        home_team_name="Bayern Munich",
        away_team_code="ARS",
        away_team_name="Arsenal",
        score_home=1,
        score_away=0,
        clock="90:00",
        period="FT",
        competition="UCL Quarter-Final",
        venue="Allianz Arena",
        status="COMPLETE",
        feed_spec="4K UHD 60FPS",
        latency_ms=15,
    )
    db.add(match_bay)

    match_int = Match(
        id="UCL-2024-INT-ATL-R16",
        home_team_code="INT",
        home_team_name="Inter",
        away_team_code="ATL",
        away_team_name="Atletico",
        score_home=1,
        score_away=0,
        clock="45:00",
        period="HT",
        competition="UCL R16",
        venue="San Siro",
        status="LIVE",
        feed_spec="1080P SDI",
        latency_ms=18,
    )
    db.add(match_int)
    db.flush()

    # 3. Seed Players for MCI-RMA
    players_data = [
        {
            "id": "849-19",
            "match_id": match.id,
            "jersey": 19,
            "name": "Mason Mount",
            "team": "Chelsea FC / Man City",
            "nationality": "ENG",
            "role": "Attacking Midfield",
            "ai_confidence": 98.8,
            "skeletal_lock_status": "OK",
            "distance_km": 8.42,
            "sprints": 19,
            "top_speed_kph": 32.8,
            "avg_velocity_kph": 28.4,
            "centroid_x": 34.08,
            "centroid_y": -8.12,
            "centroid_z": 1.42,
            "pitch_x": 210.0,
            "pitch_y": 82.0,
        },
        {
            "id": "849-15",
            "match_id": match.id,
            "jersey": 15,
            "name": "Eric Dier",
            "team": "Tottenham Hotspur",
            "nationality": "ENG",
            "role": "Centre-Back",
            "ai_confidence": 99.2,
            "skeletal_lock_status": "OK",
            "distance_km": 7.20,
            "sprints": 11,
            "top_speed_kph": 28.4,
            "avg_velocity_kph": 21.6,
            "centroid_x": 34.22,
            "centroid_y": -7.88,
            "centroid_z": 0.12,
            "pitch_x": 220.0,
            "pitch_y": 95.0,
        },
        {
            "id": "849-17",
            "match_id": match.id,
            "jersey": 17,
            "name": "Kevin De Bruyne",
            "team": "Manchester City",
            "nationality": "BEL",
            "role": "Central Midfield",
            "ai_confidence": 97.6,
            "skeletal_lock_status": "OK",
            "distance_km": 9.14,
            "sprints": 22,
            "top_speed_kph": 30.2,
            "avg_velocity_kph": 26.8,
            "centroid_x": 28.4,
            "centroid_y": -4.2,
            "centroid_z": 1.1,
            "pitch_x": 115.0,
            "pitch_y": 80.0,
        },
        {
            "id": "849-09",
            "match_id": match.id,
            "jersey": 9,
            "name": "Erling Haaland",
            "team": "Manchester City",
            "nationality": "NOR",
            "role": "Centre Forward",
            "ai_confidence": 99.1,
            "skeletal_lock_status": "OK",
            "distance_km": 6.88,
            "sprints": 28,
            "top_speed_kph": 35.8,
            "avg_velocity_kph": 24.2,
            "centroid_x": 38.6,
            "centroid_y": -2.1,
            "centroid_z": 1.8,
            "pitch_x": 235.0,
            "pitch_y": 35.0,
        },
        {
            "id": "849-07",
            "match_id": match.id,
            "jersey": 7,
            "name": "Vinícius Jr.",
            "team": "Real Madrid",
            "nationality": "BRA",
            "role": "Left Winger",
            "ai_confidence": 98.4,
            "skeletal_lock_status": "OK",
            "distance_km": 8.96,
            "sprints": 31,
            "top_speed_kph": 36.4,
            "avg_velocity_kph": 27.6,
            "centroid_x": 26.8,
            "centroid_y": 14.2,
            "centroid_z": 1.2,
            "pitch_x": 170.0,
            "pitch_y": 50.0,
        },
        {
            "id": "849-10",
            "match_id": match.id,
            "jersey": 10,
            "name": "Luka Modrić",
            "team": "Real Madrid",
            "nationality": "CRO",
            "role": "Central Midfield",
            "ai_confidence": 96.8,
            "skeletal_lock_status": "OK",
            "distance_km": 10.2,
            "sprints": 18,
            "top_speed_kph": 27.4,
            "avg_velocity_kph": 23.8,
            "centroid_x": 22.4,
            "centroid_y": 1.8,
            "centroid_z": 1.0,
            "pitch_x": 165.0,
            "pitch_y": 80.0,
        },
    ]

    for p in players_data:
        db.add(Player(**p))

    # 4. Seed Events
    events_data = [
        {
            "id": "EVT-001", "match_id": match.id, "minute": 12, "second": 0, "frame_id": 21600,
            "timecode": "00:12:00.000", "type": "GOAL", "team": "MCI", "player": "Erling Haaland",
            "player_jersey": 9, "player_team": "Manchester City / NOR",
            "description": "Clinical finish from Haaland after a through-ball from De Bruyne; right foot placement into far post.",
            "ai_verdict": "VALIDATED", "xg": 0.72, "ball_velocity_kph": 112.4, "impact_g_force": 18.6,
            "ai_explanation": "Kick-point confirmed at Frame #21,600. Multi-camera reconstruction validates onside position. Ball in play: verified.",
            "is_active": False,
        },
        {
            "id": "EVT-002", "match_id": match.id, "minute": 17, "second": 0, "frame_id": 30600,
            "timecode": "00:17:00.000", "type": "YELLOW_CARD", "team": "RMA", "player": "Eduardo Camavinga",
            "player_jersey": 12, "player_team": "Real Madrid / FRA",
            "description": "Late challenge on Rodri near the center circle.",
            "ai_verdict": None, "xg": None, "ball_velocity_kph": None, "impact_g_force": None,
            "ai_explanation": None, "is_active": False,
        },
        {
            "id": "EVT-003", "match_id": match.id, "minute": 22, "second": 0, "frame_id": 39600,
            "timecode": "00:22:00.000", "type": "GOAL", "team": "RMA", "player": "Vinícius Jr.",
            "player_jersey": 7, "player_team": "Real Madrid / BRA",
            "description": "Vinícius capitalizes on a defensive error; left-foot low drive across goal.",
            "ai_verdict": "VALIDATED", "xg": 0.68, "ball_velocity_kph": 98.7, "impact_g_force": 16.2,
            "ai_explanation": "Ball trajectory confirmed at Frame #39,600. Onside verified. No foul in build-up.",
            "is_active": False,
        },
        {
            "id": "EVT-004", "match_id": match.id, "minute": 28, "second": 0, "frame_id": 50400,
            "timecode": "00:28:00.000", "type": "YELLOW_CARD", "team": "MCI", "player": "Rodri",
            "player_jersey": 16, "player_team": "Manchester City / ESP",
            "description": "Deliberate handball to stop a counter-attack.",
            "ai_verdict": None, "xg": None, "ball_velocity_kph": None, "impact_g_force": None,
            "ai_explanation": None, "is_active": False,
        },
        {
            "id": "EVT-005", "match_id": match.id, "minute": 34, "second": 18, "frame_id": 61740,
            "timecode": "00:34:18.000", "type": "PENALTY_RESCINDED", "team": "MCI", "player": "Erling Haaland",
            "player_jersey": 9, "player_team": "Manchester City / NOR",
            "description": "Initial penalty award overturned after VAR review — contact was minimal, outside penalty box.",
            "ai_verdict": "AI EVENT: CONTACT DETECTED (MINIMAL)", "xg": None, "ball_velocity_kph": None,
            "impact_g_force": None, "ai_explanation": "Contact force below threshold. Incident occurred 2.4cm outside penalty area by reprojection.",
            "is_active": False,
        },
        {
            "id": "EVT-006", "match_id": match.id, "minute": 39, "second": 0, "frame_id": 70200,
            "timecode": "00:39:00.000", "type": "YELLOW_CARD", "team": "RMA", "player": "Luka Modrić",
            "player_jersey": 10, "player_team": "Real Madrid / CRO",
            "description": "Simulation after drawing a free-kick near the edge of the box.",
            "ai_verdict": None, "xg": None, "ball_velocity_kph": None, "impact_g_force": None,
            "ai_explanation": None, "is_active": False,
        },
        {
            "id": "EVT-007", "match_id": match.id, "minute": 44, "second": 0, "frame_id": 79200,
            "timecode": "00:44:00.000", "type": "OFFSIDE", "team": "MCI", "player": None,
            "player_jersey": None, "player_team": None,
            "description": "Marginal offside flag confirmed against Manchester City attacker.",
            "ai_verdict": "FLAG CONFIRMED", "xg": None, "ball_velocity_kph": None, "impact_g_force": None,
            "saot_margin_cm": 4.2, "ai_explanation": "SAOT triangulation confirms offside by 4.2cm. Uncertainty: ±0.8cm.",
            "is_active": False,
        },
        {
            "id": "EVT-008", "match_id": match.id, "minute": 46, "second": 0, "frame_id": 82800,
            "timecode": "00:46:00.000", "type": "SUBSTITUTION", "team": "RMA", "player": "Substitution",
            "player_jersey": None, "player_team": None,
            "description": "Halftime tactical substitution by Real Madrid.",
            "ai_verdict": None, "xg": None, "ball_velocity_kph": None, "impact_g_force": None,
            "ai_explanation": None, "is_active": False,
        },
        {
            "id": "EVT-009", "match_id": match.id, "minute": 53, "second": 2, "frame_id": 95450,
            "timecode": "00:53:02.000", "type": "GOAL", "team": "MCI", "player": "Kevin De Bruyne",
            "player_jersey": 17, "player_team": "Manchester City / BEL",
            "description": "Low-probability long-range strike from De Bruyne deflects off a defender into the net.",
            "ai_verdict": "VALIDATED", "xg": 0.08, "ball_velocity_kph": 127.3, "impact_g_force": 22.1,
            "ai_explanation": "Deflection did not initiate offside phase. Clean trajectory locked.",
            "is_active": False,
        },
        {
            "id": "EVT-010", "match_id": match.id, "minute": 67, "second": 24, "frame_id": 121340,
            "timecode": "01:07:24.482", "type": "OFFSIDE", "team": "MCI", "player": "Mason Mount",
            "player_jersey": 19, "player_team": "Manchester City / ENG",
            "description": "SAOT automated alert: Attacker shoulder datum 14.2cm beyond penultimate defender boot datum.",
            "ai_verdict": "OFFSIDE CONFIRMED (+14.2cm)", "xg": None, "ball_velocity_kph": 86.4,
            "impact_g_force": None, "saot_margin_cm": 14.2,
            "ai_explanation": "Skeletal limb keypoint tracking locked (18/18 KP). Frame #121,340 kick-point confirmed by multi-cam triangulation.",
            "is_active": True,
        },
    ]

    for ev in events_data:
        db.add(MatchEvent(**ev))

    # 5. Seed Sessions
    sessions_data = [
        {
            "id": "UCL-2024-MCI-RMA-F",
            "match_id": match.id,
            "status": "READY",
            "progress_percent": 100,
            "current_stage": "COMPLETE",
            "eta_minutes": 0,
            "var_alerts": 14,
            "offside_checks": 9,
            "penalty_radar": 3,
            "red_card_eval": 2,
            "goal_verify": 2,
            "avg_overturn_seconds": 18.4,
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBm42jvQ9ReERba-4rgVJF1S6wBtM1-pHEeCZnV-FroGWllwMj3rz_49xQwDcbyE8QQb5Q5NIfgkC2iGwiNxmBJCNhTBjzQPPWNkG3lVGFnh5H-vJ65VCmJ118_LIUg3rJaMMJm9MQ0TfvIapTS8IX761nApI_2DfkN6xcG00zf62Bt1SAOcXIVkXmup5L2pTWu7CxFLyJtxR6OumBidV-LpImLSzrbAIqcxpw7Ht8HlB7l60_kadSH",
            "camera_sources": "4-Camera Synchronized VAR feed",
        },
        {
            "id": "UCL-2024-BAY-ARS-QF",
            "match_id": match_bay.id,
            "status": "ARCHIVED",
            "progress_percent": 100,
            "current_stage": "COMPLETE",
            "eta_minutes": 0,
            "var_alerts": 18,
            "offside_checks": 16,
            "penalty_radar": 1,
            "red_card_eval": 0,
            "goal_verify": 4,
            "avg_overturn_seconds": 22.4,
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDJKQcO46lczmV3uvMU3eNjMXPlcQaLNVIy5v2HBkqikgMCwf6KhsgsyogANRwEkMf5x11HrcJJdV4BnNkD9dPbihenmzIpHLHidbb-ovD8O76Q4C-mPCUZGxJ33GAss9Mjrw8JLVmVZwyjsPSxVdj8zCBLBzvRRZEhM5OXD9KLQylS8sm6zdYYug_jmDyCiqF0oshIklIU6vaDKCnsWI57iSX85ARI2xLRW4H2QU0Xv3RFgTpFGzio",
            "camera_sources": "12-Cam Optical Array",
        },
        {
            "id": "UCL-2024-INT-ATL-R16",
            "match_id": match_int.id,
            "status": "PROCESSING",
            "progress_percent": 68,
            "current_stage": "BALL_TRACKING",
            "eta_minutes": 4,
            "var_alerts": 8,
            "offside_checks": 5,
            "penalty_radar": 2,
            "red_card_eval": 1,
            "goal_verify": 1,
            "avg_overturn_seconds": 19.8,
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAUOwdgdpJSGJ83a9o3_-3NmJUWherZh8ZWG0VMaD_FkPJ8zNvikcJNZevxAcIFMsQcI1ucaEx7k4BTnW80MpKd6qXmSXGrNFoOYXbuj7CTjGoiJ3DvroCN54EpKNGDOyRAdCxgEQgrWy-UX02BKq8_kFTsZ9ar0xtnBNzisJuh3SpPzYtyEIiPi8RUpBUTQnNRcq6HrBrExXr52HOQhS3AFx2L7QG8U2ylgamelzNLUzg9VLwat5i1",
            "camera_sources": "8-Camera Optical Array",
        },
    ]

    for s in sessions_data:
        db.add(AnalysisSession(**s))

    db.commit()
