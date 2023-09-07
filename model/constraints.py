import pyomo.environ as pe

class ConstraintsBuilder():
    def __init__(self, m):
        self.m = m
        self.build_all_constraints()

    def build_all_constraints(self):
        self.build_each_game_is_played_once_constr(self.m)
        self.build_max_one_home_game_per_week_constr(self.m)
        self.build_max_one_away_game_per_week_constr(self.m)
        self.build_no_game_with_itself_constr(self.m)


    # each game is played once throughout the season
    def build_each_game_is_played_once_constr(self, m):
        def _each_game_is_played_once_rule(m, team_i, team_j):
            if team_i == team_j:
                return pe.Constraint.Skip
            return sum(m.is_match_this_week_var[team_i, team_j, weak_k]
                       for weak_k in m.weeks_range_set) == 1
        m.each_game_is_played_once_constr = pe.Constraint(m.teams_range_set, m.teams_range_set,
                                                              rule=_each_game_is_played_once_rule)
        return m

    # maximum one home game for each team per week
    def build_max_one_home_game_per_week_constr(self, m):
        def _max_one_home_game_per_week_rule(m, team_i, weak_k):
            return sum(m.is_match_this_week_var[team_i, team_j, weak_k]
                       for team_j in m.teams_range_set) + \
                   sum(m.is_match_this_week_var[team_j, team_i, weak_k]
                       for team_j in m.teams_range_set) <= 1

        m.max_one_home_game_per_week_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                   rule=_max_one_home_game_per_week_rule)
        return m

    # maximum one away game for each team per week
    def build_max_one_away_game_per_week_constr(self, m):
        def _max_one_away_game_per_week_rule(m, team_j, weak_k):
            return sum(m.is_match_this_week_var[team_i, team_j, weak_k]
                       for team_i in m.teams_range_set) <= 1

        m.max_one_game_per_week_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                   rule=_max_one_away_game_per_week_rule)
        return m

    # games team_a vs team_a are excluded
    def build_no_game_with_itself_constr(self, m):
        def _no_game_with_itself_rule(m, team_i, weak_k):
            return m.is_match_this_week_var[team_i, team_i, weak_k] == 0

        m.no_game_with_itself_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                         rule=_no_game_with_itself_rule)
        return m