from general import values


class PlayerPresence(object):
    """
    :param online_id: ID of the player (gamertag for xbox,
        psn_online_id for playstation, steam_id64 for steam)
    :param service: Represents what service was used to obtain presence
    :param platform: Represents what system the players is on 
    :param player_state: Represents the online state of the player which can be
        Online, Away, or Offline
    :param game_title: The game title the player is playing, can be None
    :param last_seen: When the player was last online, can be None
    """
    UNKNOWN = 0
    OFFLINE = 1
    DO_NOT_DISTURB = 2
    AWAY = 3
    ONLINE = 4


    def __init__(self, online_id, service, platform, player_state, game_title, last_seen):
        self.online_id = online_id
        self.service = service
        self.platform = platform
        self.player_state = player_state
        self.game_title = game_title
        self.last_seen = last_seen

    def __str__(self):
        str = ""
        if self.player_state == PlayerPresence.ONLINE:
            str += f"{values.ONLINE_EMOJI} {self.service}: "
            if self.game_title:
                str += f"{self.game_title}"
            else:
                str += "Online"
            if self.platform:
                str += f" ({self.platform})"
        elif self.player_state == PlayerPresence.AWAY:
            str += f"{values.AWAY_EMOJI} {self.service}: "
            if self.game_title:
                str += f"{self.game_title}"
            else:
                str += "Away"
            if self.platform:
                str += f" ({self.platform})"
        elif self.player_state == PlayerPresence.DO_NOT_DISTURB:
            str += f"{values.DO_NOT_DISTURB_EMOJI} {self.service}: "
            if self.game_title:
                str += f"{self.game_title}"
            else:
                str += "Do Not Disturb"
            if self.platform:
                str += f" ({self.platform})"
        elif self.player_state == PlayerPresence.OFFLINE:
            str += f"{values.OFFLINE_EMOJI} {self.service}: "
            if not self.last_seen and not self.game_title and not self.platform:
                str += "Offline"
            else:
                str += "Last seen "
                if self.last_seen:
                    str += (self.last_seen + " ")
                if self.game_title:
                    str += f"- {self.game_title} "
                if self.platform:
                    str += f"({self.platform})"
        else:
            str += f"{values.UNKNOWN_EMOJI} {self.service}"

        return str

    def __lt__(self, other):
        return (self.player_state, self.online_id) < (other.player_state, other.online_id)

    def __eq__(self, other):
        return (self.player_state, self.online_id) == (other.player_state, other.online_id)
