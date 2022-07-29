class UserStatus(object):
    """
    :param online_id: ID of the player (gamertag for xbox,
        psn_online_id for playstation, steam_id64 for steam)
    :param platform: 
    :param is_online: Represents whether the player is currently online
    :param current_title: The current title the player is playing, can be None
    :param last_seen: When the player was last online, can be None
    """
    def __init__(self, user_id, display_name, xbox_presence, psn_presence):
        self.user_id = user_id
        self.display_name = display_name
        self.presences = []
        if xbox_presence:
            self.presences.append(xbox_presence)
        if psn_presence:
            self.presences.append(psn_presence)
        self.presence_strength = 0
        for presence in self.presences:
            self.presence_strength += presence.player_state

    def __str__(self):
        str = f"{self.display_name}\n"
        for presence in self.presences:
            str += (presence.__str__() + "\n")
        str += "\n"
        return str

    def __lt__(self, other):
        return (self.presence_strength, self.display_name) < (other.presence_strength, other.display_name)

    def __eq__(self, other):
        return (self.presence_strength, self.display_name) == (other.presence_strength, other.display_name)
