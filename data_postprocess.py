import pyomo.environ as pe
import pandas as pd
import openpyxl
import plotly.graph_objects as go
import os

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

class DataPostprocess():
    def __init__(self, solved_model, teams_name_index_map, all_teams_coords_df):
        self.solved_model = solved_model
        self.fig = DataPostprocess.build_teams_map(all_teams_coords_df, MAPBOX_TOKEN)
        self.chosen_matches, self.league_schedule_table, self.filtered_schedule_per_team_dict = self.prepare_schedule_table(teams_name_index_map)

    @staticmethod
    def build_teams_map(all_teams_coords_df,
                        MAPBOX_TOKEN):
        # quick plot of teams location on map
        fig = go.Figure()
        fig.add_trace(
            go.Scattermapbox(
                mode="markers+text",
                lat=all_teams_coords_df.lat.tolist(),
                lon=all_teams_coords_df.lon.tolist(),
                marker={"size": 10, "color": "black"},
                hovertext=all_teams_coords_df.team,
            )
        )
        fig.update_layout(mapbox={
            "accesstoken": MAPBOX_TOKEN,
            "zoom": 5,
            "center": {
                "lat": pd.concat([all_teams_coords_df.lat, all_teams_coords_df.lat], axis=0).mean(),
                "lon": pd.concat([all_teams_coords_df.lon, all_teams_coords_df.lon], axis=0).mean(),
            },
        },
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

        fig.write_image("output/bundesliga_teams_coords.png")
        return fig

    def prepare_schedule_table(self, teams_name_index_map):
        teams_index_name_map = {index: name for name, index in teams_name_index_map.items()}
        chosen_is_match_this_week = {
            index: pe.value(self.solved_model.is_match_this_week_var[index])
            for index in self.solved_model.is_match_this_week_var
            if self.solved_model.is_match_this_week_var[index].value != 0
        }
        chosen_matches = list(chosen_is_match_this_week.keys())

        league_schedule_table = pd.DataFrame(columns=teams_name_index_map.keys(), index=teams_name_index_map.keys())
        for match in chosen_matches:
            team1_idx, team2_idx, result = match[0], match[1], match[2]
            league_schedule_table.at[teams_index_name_map[team1_idx], teams_index_name_map[team2_idx]] = f'Week {result}'
        league_schedule_table.to_excel("output/bundesliga_schedule.xlsx")

        filtered_schedule_per_team_dict = {}
        # Iterate through the list of tuples and collect data
        for team1_idx, team2_idx, week in chosen_matches:
            if teams_index_name_map[team1_idx] in filtered_schedule_per_team_dict:
                filtered_schedule_per_team_dict[teams_index_name_map[team1_idx]]['Team'].append(teams_index_name_map[team2_idx])
                filtered_schedule_per_team_dict[teams_index_name_map[team1_idx]]['Week'].append(week)
            else:
                filtered_schedule_per_team_dict[teams_index_name_map[team1_idx]] = {'Team': [teams_index_name_map[team2_idx]], 'Week': [week]}

        filtered_schedule_per_team_dict = {team: pd.DataFrame(data) for team, data in filtered_schedule_per_team_dict.items()}
        for team, schedule_df in filtered_schedule_per_team_dict.items():
            filtered_schedule_per_team_dict[team] = schedule_df.sort_values(by='Week')

        return chosen_matches, league_schedule_table, filtered_schedule_per_team_dict


