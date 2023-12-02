import pyomo.environ as pe


class ObjectiveBuilder():
    def __init__(self, m):
        self.build_objective(m)

    def build_obj_rule(self, m):
        return sum(m.distance_between_teams_param[team_i, team_j] * m.is_match_this_week_var[team_i, team_j, week_k]
                   for team_i in m.teams_range_set
                   for team_j in m.teams_range_set
                   for week_k in m.weeks_range_set)

    def build_objective(self, m):
        m.OBJ = pe.Objective(rule=self.build_obj_rule)
