import pyomo.environ as pe

class ParametersBuilder:
    def __init__(self, m, team_distance_matrix_dict):
        self.team_distance_matrix_dict = team_distance_matrix_dict
        self.build_team_distance_matrix_param(m, team_distance_matrix_dict)

    @staticmethod
    def build_team_distance_matrix_param(m, team_distance_matrix_dict):
        m.distance_between_teams_param = pe.Param(m.teams_range_set, m.teams_range_set,
                                                      initialize=team_distance_matrix_dict)
