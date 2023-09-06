import pyomo.environ as pe

class VariablesBuilder:
    def __init__(self, m):
        self.m = m
        self.build_all_variables()

    def build_all_variables(self):
        self.build_is_match_this_week_var(self.m)
        return self.m

    @staticmethod
    def build_is_match_this_week_var(m):
        m.is_match_this_week_var = pe.Var(m.teams_range_set, m.teams_range_set, m.weeks_range_set, domain=pe.Boolean, initialize=0)
        return m
