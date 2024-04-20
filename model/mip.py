import pyomo.environ as pe
import pyomo.opt as popt
from model.sets import SetsBuilder
from model.variables import VariablesBuilder
from model.parameters import ParametersBuilder
from model.constraints import ConstraintsBuilder
from model.objective import ObjectiveBuilder
from pyomo.contrib.appsi.solvers import Highs 



class Model():
    def __init__(self,
                 teams_list,
                 teams_range,
                 weeks_range,
                 team_distance_matrix_dict,
                 team_ranks_dict,
                 match_attractiveness_dict,
                 conflict_home_match_list):
        self.teams_list = teams_list
        self.teams_range = teams_range
        self.weeks_range = weeks_range
        self.team_ranks_dict = team_ranks_dict
        self.match_attractiveness_dict = match_attractiveness_dict
        self.conflict_home_match_list = conflict_home_match_list
        self.m = None
        self.build_model(teams_range,
                         weeks_range,
                         team_distance_matrix_dict,
                         team_ranks_dict,
                         match_attractiveness_dict,
                         conflict_home_match_list)

    def build_model(self,
                    teams_range,
                    weeks_range,
                    team_distance_matrix_dict,
                    team_rank_dict,
                    match_attractiveness_dict,
                    conflict_home_match_list):

        self.m = pe.ConcreteModel()
        SetsBuilder(self.m, teams_range, weeks_range)
        VariablesBuilder(self.m)
        ParametersBuilder(self.m, team_distance_matrix_dict)
        ConstraintsBuilder(self.m, conflict_home_match_list)
        ObjectiveBuilder(self.m, team_rank_dict, match_attractiveness_dict)

    @staticmethod
    def solve_model(m):
        # Solve model
        solver = popt.SolverFactory("gurobi")
        model_instance = m.create_instance()
        solver.solve(
            model_instance,
            tee=True,
            keepfiles=True,
            logfile="model_logfile",
            report_timing=True,
            symbolic_solver_labels=True
        )
        return model_instance
