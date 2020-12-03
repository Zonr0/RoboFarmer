import screencapture
from enum import *

class GameState(Enum):
    """Major states (as in the states in a state machine) of the game."""
    UNKNOWN = -1
    PLAY = 0  # General free movement
    MENU = 1  # The in-game menu
    CONVERSATION = 2  # Talking to an NPC or animal
    CUTSCENE = 3  # Cutscene where we have no control of our character

class GameTime:
    """Represents a unit of game time. Can be either a fixed time (as in, it is 12 pm in game right now), or a unit
    of measurement."""
    def __init__(self,hour=0,minute=0):
        self.hour = hour
        self.minute = minute



class Game:
    """Singleton accumulator for everything we know about the current game. This needs to be threadsafe because we could
    be writing to it and reading to it from different threads."""
    def __init__(self):
        self.state = GameState.UNKNOWN
        self.time = GameTime()

