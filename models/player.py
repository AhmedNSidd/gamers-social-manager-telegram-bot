import datetime
import humanize
from general import values

class Player(object):
    """
    :param id: ID of the player
    :param is_online: Represents whether the player is currently online
    :param current_title: The current title the player is playing, can be None
    :param last_seen: When the player was last online, can be None
    """
    def __init__(self, id, name, is_online, current_title, last_seen):
        self.id = id
        self.name = name
        self.is_online = is_online
        self.current_title = current_title
        self.last_seen = last_seen

    def __str__(self):
        str = ""
        emoji = values.ONLINE_EMOJI if self.is_online else values.OFFLINE_EMOJI
        status = "Online" if self.is_online else "Offline"

        str += f"{emoji} {self.name}: {status}\n"
        if self.current_title:
            str += f"Playing: {self.current_title}\n\n"
        elif self.last_seen:
            str += f"Last seen: {self.last_seen}\n\n"
        else:
            str += "\n\n"

        return str

    def __lt__(self, other):
        return (self.is_online, self.name) < (other.is_online, other.name)

    def __eq__(self, other):
        return (self.is_online, self.name) == (other.is_online, other.name)
