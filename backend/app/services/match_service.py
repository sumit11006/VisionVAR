from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.models.match import Match
from backend.app.models.event import MatchEvent
from backend.app.models.player import Player
from backend.app.schemas.match import MatchResponse, Team, Score
from backend.app.schemas.event import MatchEventResponse, MatchEventsListResponse
from backend.app.schemas.player import PlayerResponse, PlayerTelemetryResponse, PlayerStats, Centroid3D


class MatchService:
    def __init__(self, db: Session):
        self.db = db

    def get_match(self, match_id: str) -> MatchResponse:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

        return MatchResponse(
            id=match.id,
            homeTeam=Team(code=match.home_team_code, name=match.home_team_name),
            awayTeam=Team(code=match.away_team_code, name=match.away_team_name),
            score=Score(home=match.score_home, away=match.score_away),
            clock=match.clock,
            period=match.period,
            competition=match.competition,
            venue=match.venue,
            status=match.status,
            feedSpec=match.feed_spec,
            latencyMs=match.latency_ms,
        )

    def get_events(self, match_id: str) -> MatchEventsListResponse:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

        events = (
            self.db.query(MatchEvent)
            .filter(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.minute.asc(), MatchEvent.second.asc())
            .all()
        )

        event_responses = [
            MatchEventResponse(
                id=e.id,
                minute=e.minute,
                second=e.second,
                frameId=e.frame_id,
                timecode=e.timecode,
                type=e.type,
                team=e.team,
                player=e.player,
                playerJersey=e.player_jersey,
                playerTeam=e.player_team,
                description=e.description,
                aiVerdict=e.ai_verdict,
                xg=e.xg,
                ballVelocityKph=e.ball_velocity_kph,
                impactGForce=e.impact_g_force,
                saotMarginCm=e.saot_margin_cm,
                aiExplanation=e.ai_explanation,
                isActive=e.is_active,
                status=e.status,
                confidence=e.confidence,
                metadata_json=e.metadata_json,
            )
            for e in events
        ]

        return MatchEventsListResponse(
            match_id=match_id,
            total_events=len(event_responses),
            events=event_responses,
        )

    def get_player_telemetry(self, match_id: str, player_id: str) -> PlayerTelemetryResponse:
        player = (
            self.db.query(Player)
            .filter(Player.match_id == match_id, Player.id == player_id)
            .first()
        )
        if not player:
            # Fallback search by ID alone or return 404
            player = self.db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(
                    status_code=404,
                    detail=f"Player '{player_id}' not found for match '{match_id}'.",
                )

        stats = PlayerStats(
            distanceKm=player.distance_km,
            sprints=player.sprints,
            topSpeedKph=player.top_speed_kph,
            avgVelocityKph=player.avg_velocity_kph,
        )
        centroid = Centroid3D(
            x=player.centroid_x,
            y=player.centroid_y,
            z=player.centroid_z,
        )

        return PlayerTelemetryResponse(
            player_id=player.id,
            match_id=match_id,
            name=player.name,
            jersey=player.jersey,
            team=player.team,
            stats=stats,
            centroid=centroid,
            pitch_coordinates={"pitch_x": player.pitch_x, "pitch_y": player.pitch_y},
            ai_confidence=player.ai_confidence,
            skeletal_lock_status=player.skeletal_lock_status,
            instantaneous_speed_kph=round(player.avg_velocity_kph * 1.08, 1),
            acceleration_ms2=2.4,
            stamina_index=88.5,
            timecode="01:07:24.482",
        )
