import pyomo.environ as pe

class SetsBuilder():
    def __init__(self, m, teams_range, weeks_range):
        self.m = m
        self.teams_range = teams_range
        self.weeks_range = weeks_range
        self.build_all_sets(teams_range, weeks_range)

    def build_all_sets(self, teams_range, weeks_range):
        self.build_teams_range_set(self.m, teams_range)
        self.build_weeks_range_set(self.m, weeks_range)
        return self.m

    @staticmethod
    def build_teams_range_set(m, teams_range):
        m.teams_range_set = pe.Set(initialize=teams_range, dimen=1)

    @staticmethod
    def build_weeks_range_set(m, weeks_range):
        m.weeks_range_set = pe.Set(initialize=weeks_range, dimen=1)

