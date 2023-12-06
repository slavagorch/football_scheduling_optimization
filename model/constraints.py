import pyomo.environ as pe


class ConstraintsBuilder():
    def __init__(self, m):
        self.m = m
        self.build_all_constraints()

    def build_all_constraints(self):
        self.build_each_match_is_played_once_constr(self.m)
        self.build_max_one_home_match_per_week_constr(self.m)
        # self.build_balance_home_away_matches_constr(self.m) No need in this constraint due to input structure
        self.build_no_match_with_itself_constr(self.m)
        self.no_more_than_two_away_matches_in_a_row(self.m)
        self.home_away_matches_same_teams(self.m)

    # each match is played once throughout the season
    def build_each_match_is_played_once_constr(self, m):
        def _each_match_is_played_once_rule(m, team_i, team_j):
            if team_i == team_j:
                return pe.Constraint.Skip
            return sum(m.is_match_this_week_var[team_i, team_j, week_k]
                       for week_k in m.weeks_range_set) == 1

        m.each_match_is_played_once_constr = pe.Constraint(m.teams_range_set, m.teams_range_set,
                                                          rule=_each_match_is_played_once_rule)
        return m

    # maximum one match for each team per week (home or away)
    def build_max_one_home_match_per_week_constr(self, m):
        def _max_one_home_match_per_week_rule(m, team_i, week_k):
            return sum(m.is_match_this_week_var[team_i, team_j, week_k]
                       for team_j in m.teams_range_set) + \
                sum(m.is_match_this_week_var[team_j, team_i, week_k]
                    for team_j in m.teams_range_set) <= 1

        m.max_one_home_match_per_week_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                            rule=_max_one_home_match_per_week_rule)
        return m

    # each team has equal number of home and away matches in the season
    def build_balance_home_away_matches_constr(self, m):
        def _balance_home_away_matches_rule(m, team_i):
            return (sum(m.is_match_this_week_var[team_i, team_j, week_k]
                        for team_j in m.teams_range_set
                        for week_k in m.weeks_range_set) ==
                    sum(m.is_match_this_week_var[team_j, team_i, week_k]
                        for team_j in m.teams_range_set
                        for week_k in m.weeks_range_set))

        m.balance_home_away_matches_constr = pe.Constraint(m.teams_range_set, rule=_balance_home_away_matches_rule)

        return m

    # matches team_a vs team_a are excluded
    def build_no_match_with_itself_constr(self, m):
        def _no_match_with_itself_rule(m, team_i, weak_k):
            return m.is_match_this_week_var[team_i, team_i, weak_k] == 0

        m.no_match_with_itself_constr = pe.Constraint(m.teams_range_set, m.weeks_range_set,
                                                     rule=_no_match_with_itself_rule)
        return m

    # each team should not have more than 2 matches away in a row
    def no_more_than_two_away_matches_in_a_row(self, m):
        pass

    # home and away matches of the same pair of teams should be in different half of the season
    def home_away_matches_same_teams(self, m):
        def _no_both_matches_weeks_first_half_rule(m, team_i, team_j):
            return sum(m.is_match_this_week_var[team_i, team_j, weak_k] +
                       m.is_match_this_week_var[team_j, team_i, weak_k]
                       for weak_k in m.weeks_first_half_set) <= 1

        def _no_both_matches_weeks_second_half_rule(m, team_i, team_j):
            return sum(m.is_match_this_week_var[team_i, team_j, weak_k] +
                       m.is_match_this_week_var[team_j, team_i, weak_k]
                       for weak_k in m.weeks_second_half_set) <= 1

        m.no_both_matches_weeks_first_half_constr = pe.Constraint(m.teams_range_set, m.teams_range_set,
                                                                  rule=_no_both_matches_weeks_first_half_rule)
        m.no_both_matches_weeks_second_half_constr = pe.Constraint(m.teams_range_set, m.teams_range_set,
                                                                   rule=_no_both_matches_weeks_second_half_rule)
        return m
