import pyomo.environ as pe
import pandas as pd
import openpyxl

class DataVisualize():
    def __init__(self, solved_model, teams_name_index_map):
        self.solved_model = solved_model
        self.prepare_schedule_table(teams_name_index_map)
        pass

    def prepare_schedule_table(self, teams_name_index_map):
        chosen_is_match_this_week = {
            index: pe.value(self.solved_model.is_match_this_week_var[index])
            for index in self.solved_model.is_match_this_week_var
            if self.solved_model.is_match_this_week_var[index].value != 0
        }

        chosen_matches = list(chosen_is_match_this_week.keys())
        league_schedule = pd.DataFrame(columns=teams_name_index_map.keys(), index=teams_name_index_map.keys())
        for match in chosen_matches:
            team1_idx, team2_idx, result = match[0], match[1], match[2]
            team1_name = next(name for name, idx in teams_name_index_map.items() if idx == team1_idx)
            team2_name = next(name for name, idx in teams_name_index_map.items() if idx == team2_idx)
            league_schedule.at[team1_name, team2_name] = f'Week {result}'
        league_schedule.to_excel("output/bundesliga_schedule.xlsx")


