from general import values


class Player(object):
    """
    :param online_id: ID of the player (gamertag for xbox,
        psn_online_id for playstation, steam_id64 for steam)
    :param is_online: Represents whether the player is currently online
    :param current_title: The current title the player is playing, can be None
    :param last_seen: When the player was last online, can be None
    """
    def __init__(self, online_id, is_online, current_title, last_seen):
        self.online_id = online_id
        self.is_online = is_online
        self.current_title = current_title
        self.last_seen = last_seen

    def __str__(self):
        str = ""
        emoji = values.ONLINE_EMOJI if self.is_online else values.OFFLINE_EMOJI
        status = "Online" if self.is_online else "Offline"

        str += f"{emoji} {self.online_id}: {status}\n"
        if self.current_title:
            str += f"Playing: {self.current_title}\n\n"
        elif self.last_seen:
            str += f"Last seen: {self.last_seen}\n\n"
        else:
            str += "\n"

        return str

    def __lt__(self, other):
        return (self.is_online, self.online_id) < (other.is_online, other.online_id)

    def __eq__(self, other):
        return (self.is_online, self.online_id) == (other.is_online, other.online_id)
