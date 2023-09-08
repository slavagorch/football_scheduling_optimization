import pyomo.environ as pe

class ConstraintsBuilder():
    def __init__(self, m):
        self.m = m
        self.build_all_constraints()

    def build_all_constraints(self):
        self.build_each_game_is_played_once_constr(self.m)
        self.build_max_one_home_game_per_week_constr(self.m)
        # self.build_balance_home_away_games_constr(self.m) No need in this constraint due to input structure
        self.build_no_game_with_itself_constr(self.m)
        self.no_more_than_two_away_games_in_a_row(self.m)


    # each game is played once throughout the season
    def build_each_game_is_played_once_constr(self, m):
        def _each_game_is_played_once_rule(m, team_i, team_j):
            if team_i == team_j:
                return pe.Constraint.Skip
            return sum(m.is_match_this_week_var[team_i, team_j, week_k]
                       for week_k in m.weeks_range_set) == 1
        m.each_game_is_played_once_constr = pe.Constraint(m.teams_range_set, m.teams_range_set,
                                                              rule=_each_game_is_played_once_rule)
        return m

    # maximum one game for each team per week (home or away)
    def build_max_one_home_game_per_week_constr(self, m):
        def _max_one_home_game_per_week_rule(m, team_i, week_k):
            return sum(m.is_match_this_week_var[team_i, team_j, week_k]
                       for team_j in m.teams_range_set) + \
                   sum(m.is_match_this_week_var[team_j, team_i, week_k]
                       for team_j in m.teams_range_set) <= 1

        m.max_one_home_game_per_week_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                   rule=_max_one_home_game_per_week_rule)
        return m

    # each team has equal number of home and away games in the season
    def build_balance_home_away_games_constr(self, m):
        def _balance_home_away_games_rule(m, team_i):
            return (sum(m.is_match_this_week_var[team_i, team_j, week_k]
                       for team_j in m.teams_range_set
                       for week_k in m.weeks_range_set) ==
                    sum(m.is_match_this_week_var[team_j, team_i, week_k]
                        for team_j in m.teams_range_set
                        for week_k in m.weeks_range_set))

        m.balance_home_away_games_constr = pe.Constraint(m.teams_range_set, rule=_balance_home_away_games_rule)

        return m


    # games team_a vs team_a are excluded
    def build_no_game_with_itself_constr(self, m):
        def _no_game_with_itself_rule(m, team_i, weak_k):
            return m.is_match_this_week_var[team_i, team_i, weak_k] == 0

        m.no_game_with_itself_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                         rule=_no_game_with_itself_rule)
        return m

    # each team should not have more than 2 games away in a row
    def no_more_than_two_away_games_in_a_row(self, m):
        pass
