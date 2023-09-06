from data_preprocesser import DataPreprocess
from data_visualizer import DataVisualize
from model.mip import ModelBuild

def main():
    dp = DataPreprocess()
    model = ModelBuild(dp.teams_list, dp.teams_range, dp.weeks_range, dp.team_distance_matrix_dict)
    print("Done")

    viz = DataVisualize(model.solved_model, dp.teams_name_index_map)




if __name__ == "__main__":
    main()