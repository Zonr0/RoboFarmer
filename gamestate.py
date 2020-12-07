import screencapture
from enum import *
from threading import RLock, Lock, Condition, Semaphore

# We will be making extensive use of Re-Entrant locks for this one. The same routine might need to write to the state
# multiple times, and we should make sure that it doesn't end in deadlock.

time_lock: RLock = RLock()

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
        self._hour: int = hour # Internal 24H time.
        self._minute: int = minute
        self._time_lock: RLock = RLock()

    def __str__(self):
        return f"{self._hour}:{self._minute}"

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    def set_time_from_string(self, time_str: str):
        """Converts the time from HH:MM A.M./P.M."""
        tokenized = time_str.split(":")
        if len(tokenized) != 2:
            print(f"ERROR: Unexpected time string length. {tokenized}")
            return
        minutes_and_morning = tokenized[1].split() # "MM A.M." -> ("MM") ("A.M.")
        if len(minutes_and_morning) != 2:
            print(f"ERROR: Unexpected length of second half of string. {minutes_and_morning}")
            return
        if not tokenized[0].isnumeric():
            print(f"ERROR: {tokenized[0]} non-numeric.")
            return
        if not minutes_and_morning[0].isnumeric():
            print(f"ERROR: {minutes_and_morning[0]} non-numeric.")
            return
        if not minutes_and_morning[1].lower() not in ("a.m.","p.m"):
            print(f"Morning field not correct. {minutes_and_morning[1]}")
        hours = int(tokenized[0])
        minutes = int(minutes_and_morning[0])
        if minutes_and_morning[1].lower() == 'p.m':
            hours += 12

        # This maybe should move to a set time function and the above to a functional conversion.
        # Acquire lock and write.
        self._time_lock.acquire()
        self._hour = hours
        self._minute = minutes
        self._time_lock.release()

        return


class Game:
    """Singleton accumulator for everything we know about the current game. This needs to be threadsafe because we could
    be writing to it and reading to it from different threads."""


    def __init__(self):
        self._state: GameState = GameState.UNKNOWN
        self._time: GameTime = GameTime()
        self._money: int = 0
        # Locks:
        self._state_lock: RLock = RLock()
        self._money_lock: RLock = RLock()

    @property
    def state(self):
        """The current macro state of the game."""
        return self._state

    @state.setter
    def state(self,new_state: GameState):
        self._state_lock.acquire()
        self._state = new_state
        self._state_lock.release()

    @property
    def time(self):
        return self._time