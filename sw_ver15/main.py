
import math
import inspect
import subprocess
import sys
import warnings
import string_source as ss
import logging
import log_package as lp
warnings.filterwarnings('ignore')
import tt as tt
import string_source as ss
import time
#log 설정
logger = lp.log_setting(logging)
import pandas as pd
import os

import temp_v11 as t_v11
import new_v11 as n_v11
import mapping as mapping

#CSV FILE

client = ss.DF_client
dp = ss.DP
df_info = ss.Df_info

sch = n_v11.sch_sys(client, dp, df_info)


df_client, df_DP, df_info = sch.load_data()
df_merge = sch.merge_data(df_client, df_DP, "right")
df_client = df_merge.copy()

week_num = ss.week_list

for i in ['test2', 'possible1','test3','temp']:
	if not os.path.isdir(i):
		os.mkdir(i)


for day in week_num:
	for DF_element in  df_DP['DP'].values.tolist():
		current_point = 'DP'
		print(df_client.columns)
		temp_df = sch.dateframe_init(df_client, DF_element, week_num, day)
		print(len(temp_df))
		route = t_v11.Route(client, dp, df_info, temp_df)

		temp_df, route_list, total_distance = route.route(temp_df, DF_element, day, current_point, df_info)

		max_col = max(list(map(len, route_list)))
		count_route = len(route_list)


		result = []

		print('max :',max_col, count_route)

		for i in range(len(route_list)):
			for _ in range(max_col-len(route_list[i])):
				route_list[i].append(" ")



		result_df = pd.DataFrame(route_list)
		result_df.to_csv("./test2/"+day+"_"+DF_element+"_result.csv",encoding='euc-kr')
		result_df.transpose().to_csv("./test3/"+day+"_"+DF_element+"_result_T.csv",encoding='euc-kr')

		work_time = df_info[df_info['DP']==DF_element]['대당 운행시간(분)'].values.tolist()[0]                

		result_df_T, im_result_df_T = mapping.check_the_possible_mapping(result_df, work_time, day, DF_element)

		map1_df = mapping.mapping1(result_df_T, im_result_df_T, day, DF_element)

		final_df = mapping.vlookup_data(map1_df, result_df_T, im_result_df_T, day, DF_element)

		mapping.location_xy(final_df, df_client, df_DP, day, DF_element)

		mapping.draw_map(DF_element, day)

logger.debug("---------------------------------------------------------------------------------------------")

