import pandas as pd
from haversine import haversine_vector
from collections import defaultdict
import itertools

TABLE_COORDS_COLUMNS = {
    "FDCOUK": "team",
    "Latitude": "lat",
    "Longitude": "lon"
}


class DataPreprocess():
    def __init__(self):
        self.team_ranks_dict = None
        self.match_attractiveness_dict = None
        self.last_season_results_df = None
        self.stadium_coords_df = None
        self.teams_list = None
        self.teams_range = None
        self.weeks_range = None
        self.teams_name_index_map = None
        self.team_distance_matrix_dict = None
        self.team_season_points = None
        self.conflict_home_match_list = None
        self.all_teams_coords_df = self.preprocess_data()
        self.construct_model_input(all_teams_coords_df=self.all_teams_coords_df)

    def construct_model_input(self, all_teams_coords_df):
        self.teams_list = list(all_teams_coords_df['team'])
        self.teams_range = list(range(1, len(self.teams_list) + 1))
        self.teams_name_index_map = dict(zip(self.teams_list, self.teams_range))
        self.weeks_range = range(1, 35)  # assuming 34 matches weeks in the season
        self.team_distance_matrix_dict = DataPreprocess.construct_distance_matrix(all_teams_coords_df,
                                                                                  self.teams_name_index_map)
        self.team_ranks_dict = DataPreprocess.build_team_rank(self.teams_list, self.teams_name_index_map)
        self.match_attractiveness_dict = DataPreprocess.build_match_attractiveness(self)
        self.conflict_home_match_list = DataPreprocess.build_conflict_home_match_list(
            self.team_distance_matrix_dict)

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

    # store team results (sum of points) over last 3 seasons
    @staticmethod
    def build_team_performance(teams_list):
        team_season_points_dict = defaultdict(lambda: dict(zip(range(18, 21), [0] * 3)))
        # consider last 3 seasons
        for year in range(18, 21):
            season_data = pd.read_csv(f"data/D1_{year}-{year + 1}.csv")
            for index, row in season_data.iterrows():
                if row['FTR'] == 'H' and row['HomeTeam'] in teams_list:
                    team_season_points_dict[row['HomeTeam']][year] += 3
                elif row['FTR'] == 'A' and row['AwayTeam'] in teams_list:
                    team_season_points_dict[row['AwayTeam']][year] += 3
                elif row['HomeTeam'] in teams_list and row['AwayTeam'] in teams_list:
                    team_season_points_dict[row['HomeTeam']][year] += 1
                    team_season_points_dict[row['AwayTeam']][year] += 1
        return team_season_points_dict

    @staticmethod
    def build_team_rank(teams_list, team_name_index_map):
        """
        Team rank is a weighted sum of points over last 3 seasons
        """
        team_season_points_dict = DataPreprocess.build_team_performance(teams_list)
        team_ranks_dict = {}
        for team in teams_list:
            team_ranks_dict.setdefault(team_name_index_map[team],
                                       round(0.5 * team_season_points_dict[team].get(20, 0) + 0.3 *
                                             team_season_points_dict[

                                                 team].get(19, 0) + 0.2 * team_season_points_dict[team].get(18, 0)))
        return team_ranks_dict

    def build_match_attractiveness(self):
        """
        Calculate match attractiveness ranking
        Formula encourages match between top ranked teams in later stage of the season. With less priority matches of
        teams with similar ranks are favoured
        """
        match_attractiveness_dict = {
            (team_i, team_j, week_k): (rank_i + rank_j) * (1 + week_k / 10) * (1 - 1 / (1 + abs(rank_i - rank_j)))
            for team_i in self.teams_range
            for team_j in self.teams_range
            for week_k in self.weeks_range
            for rank_i, rank_j in [(self.team_ranks_dict[team_i], self.team_ranks_dict[team_j])]
        }
        return match_attractiveness_dict

    @staticmethod
    def build_conflict_home_match_list(team_distance_matrix_dict):
        """
        Prepare list of team pairs that have stadiums close enough to avoid schedule with 
        home matches for both on the same week
        """
        conflict_home_match_list = [(team_i, team_j) for (team_i, team_j) in team_distance_matrix_dict.keys()
                                    if team_distance_matrix_dict[(team_i, team_j)] < 15 and team_i != team_j]
        return conflict_home_match_list
