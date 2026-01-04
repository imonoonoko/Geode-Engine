from enum import Enum

class ActivityState(Enum):
    """
    Kaname Activity States
    Shared between Brain (Plan) and Body (Action).
    """
    IDLE = "idle"
    GAME = "game"
    LESSON = "lesson"
    SLEEP = "sleep"

class GameType(Enum):
    """
    Supported Game Types
    """
    SNAKE = "snake"
    BREAKOUT = "breakout"
    SHOOTER = "shooter"
    RANDOM = "random"
