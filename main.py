from data_preprocesser import DataPreprocess
from data_postprocess import DataPostprocess
from model.mip import Model
import logging
import sys

def run_pipeline():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info('Start of Data Preprocessing')
    dp = DataPreprocess()
    logger.info('Start of building model')
    model = Model(dp.teams_list,
                  dp.teams_range,
                  dp.weeks_range,
                  dp.team_distance_matrix_dict,
                  dp.team_ranks_dict,
                  dp.match_attractiveness_dict)
    logger.info('Start of solving model')
    solution = Model.solve_model(model.m)
    logger.info('Start of postprocessing model')
    output = DataPostprocess(solution, dp.teams_name_index_map, dp.all_teams_coords_df)
    return output


if __name__ == "__main__":
    run_pipeline()
