from .get_items_in_current_league import get_items_in_current_league
from .get_league_by_value import get_league_by_value
from .get_leagues import get_all_leagues, get_leagues


class LeagueRepository:
    def __init__(self):
        self.get_leagues = get_leagues
        self.get_league_by_value = get_league_by_value
        self.get_all_leagues = get_all_leagues
        self.get_items_in_current_league = get_items_in_current_league
