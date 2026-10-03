from typing import Dict, Any

class GoalGeometry:
    def __init__(self, pitch_length: float = 105.0, pitch_width: float = 68.0, goal_width: float = 7.32, y_tolerance: float = 1.0):
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.goal_width = goal_width
        
        # Center of pitch width is 34.0
        center_y = self.pitch_width / 2.0
        self.goal_y_min = center_y - (self.goal_width / 2.0) - y_tolerance
        self.goal_y_max = center_y + (self.goal_width / 2.0) + y_tolerance

    def get_goal_line(self, attacking_direction: str) -> float:
        if attacking_direction == "positive_x":
            return self.pitch_length
        elif attacking_direction == "negative_x":
            return 0.0
        return -1.0 # Unknown

    def is_in_goal_mouth(self, y: float) -> bool:
        return self.goal_y_min <= y <= self.goal_y_max

    def did_cross_line(self, prev_x: float, curr_x: float, attacking_direction: str) -> bool:
        if attacking_direction == "positive_x":
            return prev_x <= self.pitch_length and curr_x > self.pitch_length
        elif attacking_direction == "negative_x":
            return prev_x >= 0.0 and curr_x < 0.0
        return False
