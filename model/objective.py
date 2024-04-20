import pyomo.environ as pe


class ObjectiveBuilder():
    def __init__(self, m, team_rank_dict, match_attractiveness_dict):
        self.team_rank_dict = team_rank_dict
        self.match_attractiveness_dict = match_attractiveness_dict
        self.build_objective(m)

    def travel_distance_over_season(self, m):
        return sum((m.distance_between_teams_param[team_i, team_j] ** 2) * m.is_match_this_week_var[team_i, team_j, week_k]
                   for team_i in m.teams_range_set
                   for team_j in m.teams_range_set
                   for week_k in m.weeks_range_set)

    def season_attractiveness_score(self, m):
        return sum(
            self.match_attractiveness_dict[team_i, team_j, week_k] * m.is_match_this_week_var[team_i, team_j, week_k]
            for team_i in m.teams_range_set
            for team_j in m.teams_range_set
            for week_k in m.weeks_range_set)

    def build_obj_rule(self, m):
        return self.travel_distance_over_season(m) + self.season_attractiveness_score(m)

    def build_objective(self, m):
        m.OBJ = pe.Objective(rule=self.build_obj_rule)
