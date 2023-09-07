from data_preprocesser import DataPreprocess
from data_postprocess import DataPostprocess
from model.mip import ModelBuild


def run_pipeline():
    dp = DataPreprocess()
    model = ModelBuild(dp.teams_list, dp.teams_range, dp.weeks_range, dp.team_distance_matrix_dict)
    output = DataPostprocess(model.solved_model, dp.teams_name_index_map, dp.all_teams_coords_df)

    return output


if __name__ == "__main__":
    run_pipeline()