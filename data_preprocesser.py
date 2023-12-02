import pandas as pd
from haversine import haversine_vector

TABLE_COORDS_COLUMNS = {
    "FDCOUK": "team",
    "Latitude": "lat",
    "Longitude": "lon"
}


class DataPreprocess():
    def __init__(self):
        self.last_season_results_df = None
        self.stadium_coords_df = None
        self.teams_list = None
        self.teams_range = None
        self.weeks_range = None
        self.all_teams_coords_df = self.preprocess_data()
        self.construct_model_input(all_teams_coords_df=self.all_teams_coords_df)

    @staticmethod
    def preprocess_data():
        last_season_results_df = pd.read_csv("data/D1_21-22.csv")
        stadium_coords_df = pd.read_csv("data/stadiums-with-GPS-coordinates.csv")
        teams_coords_df = stadium_coords_df.loc[stadium_coords_df["FDCOUK"].isin(last_season_results_df["HomeTeam"])]
        # add missing team information
        all_teams_coords_df = DataPreprocess.add_missing_data(teams_coords_df)
        all_teams_coords_df = \
            all_teams_coords_df[["FDCOUK", "Latitude", "Longitude"]].rename(columns=TABLE_COORDS_COLUMNS)[
                TABLE_COORDS_COLUMNS.values()]
        return all_teams_coords_df

    @staticmethod
    def add_missing_data(teams_coords_df):
        # manually add stadium info not represented in the stadium coordinates file
        missing_data = {
            'Team': ['Arminia Bielefeld', 'VfL Bochum', 'RB Leipzig', 'Union Berlin'],
            'FDCOUK': ['Bielefeld', 'Bochum', 'RB Leipzig', 'Union Berlin'],
            'City': ['Bielefeld', 'Bochum', 'Leipzig', 'Berlin'],
            'Stadium': ['SchücoArena', 'Vonovia Ruhrstadion', 'Red Bull Arena', 'Stadion An der Alten Försterei'],
            'Capacity': [27240, 30272, 42500, 22706],
            'Latitude': [52.021168, 51.481663, 51.345261, 52.453489],
            'Longitude': [8.541486, 7.222778, 12.361012, 13.288811],
            'Country': ['Germany', 'Germany', 'Germany', 'Germany']
        }
        missing_df = pd.DataFrame(missing_data)
        all_teams_coords_df = pd.concat([teams_coords_df, missing_df], axis=0)
        return all_teams_coords_df

    @staticmethod
    def construct_distance_matrix(all_teams_coords_df, team_name_index_map):
        # compute matrix of haversine distances among teams
        teams_distance_matrix_df = pd.DataFrame(
            [haversine_vector([[row.lat, row.lon]] * len(all_teams_coords_df), all_teams_coords_df[["lat", "lon"]]) for
             index, row in all_teams_coords_df.iterrows()], columns=all_teams_coords_df.team,
            index=all_teams_coords_df.team
        )
        teams_distance_matrix_dict = {
            (team_name_index_map[team_i], team_name_index_map[team_j]): teams_distance_matrix_df.loc[team_i, team_j]
            for team_i in teams_distance_matrix_df.index for team_j in teams_distance_matrix_df.columns}
        return teams_distance_matrix_dict

    def construct_model_input(self, all_teams_coords_df):
        self.teams_list = list(all_teams_coords_df['team'])
        self.teams_range = list(range(1, len(self.teams_list) + 1))
        self.teams_name_index_map = dict(zip(self.teams_list, self.teams_range))
        self.weeks_range = range(1, 35)  # assuming 34 game weeks in the season
        self.team_distance_matrix_dict = DataPreprocess.construct_distance_matrix(all_teams_coords_df,
                                                                                  self.teams_name_index_map)
