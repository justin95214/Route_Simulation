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
import new_v11 as v11

class Route:
	def __init__(self, client, dp, df_info,temp_df):
		self.temp_df = temp_df
		self.dp = dp
		self.df_info = df_info
		self.client = client
		self.tool = v11.sch_sys(self.client, self.dp, self.df_info)
		
	
	# route의 첫번째돌때
	def first_time(self, temp_df, current_point):
		temp_df = self.tool.cal_xy_DP(temp_df)
		temp_df = self.tool.cal_xy_client(temp_df)
		temp_df = self.tool.cal_xy_distance(temp_df, current_point)
		temp_df = self.tool.cal_azimuth(temp_df, current_point)
		#temp_df = temp_df[temp_df['stopby']==0].sort_values(by=[current_point+'_운행거리'], ascending=[False])
		tt.autolog()
		return temp_df

	def client_to_client(self, temp_df, current_point):
		#print("columns 개수1 :",len(temp_df.columns))
		temp_df = temp_df.drop(['rad','deg'], axis=1)
		#print("columns 개수2 :",len(temp_df.columns))
		temp_df = self.tool.cal_xy_point(temp_df, current_point)
		temp_df = self.tool.cal_xy_distance(temp_df, current_point)
		temp_df = self.tool.cal_azimuth(temp_df, current_point)
		#print("columns 개수3 :",len(temp_df.columns))
		return temp_df



	def update_init_element(self, df_info, df_element):
		kappa = df_info[df_info['DP']==df_element]['대당 적재능력(box)'].values.tolist()[0]
		drive_time = df_info[df_info['DP']==df_element]['대당 운행시간(분)'].values.tolist()[0]	
		average_speed = df_info[df_info['DP']==df_element]['평균 운행 속도(km/h)'].values.tolist()[0]
		get_up = df_info[df_info['DP']==df_element]['상차시간(분)'].values.tolist()[0]
		get_off = df_info[df_info['DP']==df_element]['하차시간(분)'].values.tolist()[0]
		tt.autolog()
		return kappa, drive_time, average_speed, get_up, get_off


	def situation_update(self, temp_df, Max_point, kappa, trace_list, average_speed, drive_time, before_distance, day, get_up, get_off, distance_list, time_list):

		route_check = False
		left_drive_time = drive_time
		left_kappa = kappa
		
		#print(Max_point)
		this_distance = Max_point[trace_list[-1]+'_운행거리']
		total_distance = before_distance + this_distance
		this_time = this_distance / average_speed
		#print(this_time*60,get_off, total_distance, this_distance)
		left_drive_time = left_drive_time - this_time*60 - get_off
		left_kappa = left_kappa - Max_point[day]

		logger.debug(f'situation_update0 >> this_distance : {this_distance} | total_distance :{total_distance} | this_time :{this_time*60} | \
{get_off} ')

		##########		
		location = Max_point['code']
		logger.debug(f'location : {location}')
		trace_list.append(location)
		distance_list.append(str(this_distance))
		time_list.append(str(left_drive_time))
		temp_df.loc[temp_df['code']==location,'stopby']=1

		# DP 복귀 시에 360분 초과가 되는지 확인해야함
		DP_distance = Max_point['DP_운행거리']
		DP_time = DP_distance/ average_speed *60
		##########


		logger.error(f'DP 복귀 후 시간 : {left_drive_time - DP_time} | left time : {left_drive_time} | DP까지-time : {DP_time}')
		if left_drive_time - DP_time <0 or left_kappa <0 :
			#left_drive_time = left_drive_time + this_time*60 + get_off
			#left_kappa = left_kappa + Max_point[day]
			#print(left_drive_time, left_kappa)
			#total_distance = before_distance - this_distance
			route_check = True
			logger.error(f'변경 없음:,{this_distance}, {total_distance}, {this_time},{left_drive_time}')

			## stopby =0 을추가해야함!!!!!
			#temp_df.loc[temp_df['code']==trace_list[-1],'stopby']=0

			#DP 복귀
			left_drive_time = left_drive_time - DP_time
			#print(left_drive_time)

			location = 'DP'
			total_distance = before_distance + DP_distance
			trace_list.append(location)
			distance_list.append(str(DP_distance))
			time_list.append(str(left_drive_time))

			logger.info(f'DP 복귀 :,{DP_distance}, {total_distance}, {DP_time}, {left_drive_time}')		
			
			logger.debug(f'situation_update1-1 >> this_distance : {this_distance} | total_distance :{total_distance} | left time : \
{left_drive_time} | this_time :{this_time*60} | {get_off} ')
			logger.debug(f'situation_update1-2 >> check the dp time : DP_distance : {DP_distance} | DP_time :{DP_time} | ')
			return trace_list, left_drive_time, int(left_kappa), total_distance, route_check, distance_list, time_list
		

		"""
		location = Max_point['code']
		#print(f'location : {location}')
		trace_list.append(location)
		distance_list.append(str(this_distance))
		time_list.append(str(left_drive_time))
		temp_df.loc[temp_df['code']==location,'stopby']=1
		"""

		if len(temp_df.loc[temp_df['stopby']==0]) == 0:
			left_drive_time = left_drive_time - DP_time
			location = 'DP'
			total_distance = before_distance + DP_distance
			trace_list.append(location)
			distance_list.append(str(DP_distance))
			time_list.append(str(left_drive_time))
			logger.info(f"DP 복귀",{DP_distance}, {total_distance}, {DP_time}, {left_drive_time})
			return trace_list, left_drive_time, int(left_kappa), total_distance, route_check, distance_list, time_list

			
		#print(this_distance, total_distance, this_time,left_drive_time)
		return trace_list, left_drive_time, int(left_kappa), total_distance, route_check, distance_list, time_list
			


	# route 전체
	def route(self, temp_df, df_element,day, current_point, df_info):
		#총 루트
		route_list = []	
		

		#DP별 조건
		kappa, drive_time, average_speed, get_up, get_off = self.update_init_element(df_info, df_element)	

		time_list = [str(drive_time)]
		trace_list =['DP']
		distance_list = ['0']	
		kappa_list = []		

		total_distance = 0
		left_drive_time = drive_time
		left_kappa = kappa
		data_count = len(temp_df[temp_df['stopby']==0])
		logger.debug(f'데이터 개수 : {data_count}' )	
		#처음 상황 
		temp_df = self.first_time(temp_df, current_point)
		#거리순으로 정렬
		temp_df = temp_df[temp_df['stopby']==0].sort_values(by=[current_point+'_운행거리'], ascending=[False])
		temp_df.to_csv("./temp/"+day+"_"+df_element+ current_point+"_dataframe0.csv", encoding='euc-kr')
		#print(temp_df.head(5))
		Max_distance_row_point = temp_df[temp_df['stopby']==0].iloc[0]

		temp_df.loc[temp_df['code']==Max_distance_row_point['code'],'stopby']=1
		#print(">>",temp_df[temp_df['code']== Max_distance_row_point['code']]['stopby'])
		#업데이트 현황
		trace_list, left_drive_time, left_kappa, total_distance, route_check, distance_list, time_list =self.situation_update(temp_df[temp_df['stopby']==0], Max_distance_row_point, left_kappa, trace_list, average_speed, left_drive_time,total_distance, day,get_up, get_off, distance_list, time_list)	

		logger.info(f'>> start : {trace_list[-2]} |  arrive : {trace_list[-1]} | left time : { left_drive_time}  | left kappa : {left_kappa}')		
		#time.sleep(10)
		
		#현재 위치 변경	
		current_point = trace_list[-1]		
		#print(temp_df.head(7))

		while (len(temp_df.loc[temp_df['stopby']==0]) >0):
			

			if route_check == False:
			
				left_count_0 = len(temp_df.loc[temp_df['stopby']==0])
				logger.error(f'stopby = 0 :, {left_count_0}, {current_point}')

				temp_df = self.client_to_client(temp_df, current_point)
				#두번쨰 긴거리, 방위각 정렬 descending descending
				
				###  방위각과 거리 정규화 ###
				
				temp_df['deg'] = [ 180-x if x > 90 and x<180 else x for x in temp_df['deg']] 
				#temp_df['deg'] = [ 180-x if x > 0 and x< 90 else x for x in temp_df['deg']]
				temp_df['deg'] = [ x-180 if x > 180 and x< 270 else x for x in temp_df['deg']]
				temp_df['deg'] = [ 360-x if x > 270 and x<360 else x for x in temp_df['deg']]
				
				#temp_df['deg'] = [ 180-x if x > 90 and x<180 else x for x in temp_df['deg']]				
				#temp_df['deg'] = [ 270-x if x > 180 and x<270 else x for x in temp_df['deg']]
				#temp_df['deg'] = [ 360-x if x > 270 and x<360 else x for x in temp_df['deg']]

				temp_df['deg'] = temp_df['deg']/360
				

				Max_dist = max(temp_df[current_point+'_운행거리'].values.tolist())
				temp_df[current_point+'_운행거리'] = temp_df[current_point+'_운행거리']/(Max_dist)

				temp_df['new_std'] = temp_df['deg'] + temp_df[current_point+'_운행거리']
				temp_df = temp_df[temp_df['stopby']==0].sort_values(by=['new_std'], ascending=[True])
				
				## 기존
				#temp_df = temp_df[temp_df['stopby']==0].sort_values(by=['deg'], ascending=[False])

				temp_df.to_csv("./temp/"+day+"_"+df_element+current_point+"_dataframe1.csv", encoding='euc-kr')

				#정렬한 가장 큰 값
				Max_distance_deg_point = temp_df.iloc[0] 
				#temp_df.loc[temp_df['code']==Max_distance_deg_point['code'],'stopby']=1

				#업데이트 현황
				trace_list, left_drive_time, left_kappa, total_distance, route_check, distance_list, time_list = \
self.situation_update(temp_df, Max_distance_deg_point, left_kappa, trace_list, average_speed, left_drive_time, total_distance, day, get_up, get_off,distance_list, time_list)



				current_point = trace_list[-1]
				logger.info(f'>> start : {trace_list[-2]} |  arrive : {trace_list[-1]} | left time : { left_drive_time}  | left kappa : { left_kappa}')

				logger.debug(f'Trace List : {trace_list}')
		
			if route_check ==True:

				
				left_count_0 = len(temp_df.loc[temp_df['stopby']==0])
				logger.error(f'stopby = 0 :, {left_count_0}, {current_point}')
				
				# route 기
				route_list.append(trace_list)
				route_list.append(distance_list)
				route_list.append(time_list)
				route_list.append( [str(float(time_list[0]) - float(time_list[-1])), float(time_list[-1])] )
				#처음으로 변경
				distance_list =['0']
				trace_list =['DP']
				time_list = [str(drive_time)]
				total_distance = 0
				left_drive_time = drive_time
				left_kappa = kappa
				stopby_count = len(temp_df[temp_df['stopby']==0])
				logger.debug(f'stopby count : {stopby_count}')
					
				#처음 상황
				temp_df = self.first_time(temp_df, current_point)
				#거리순으로 정렬
				temp_df = temp_df[temp_df['stopby']==0].sort_values(by=[current_point+'_운행거리'], ascending=[False])
				temp_df.to_csv("./temp/"+day+"_"+df_element+ current_point+"_dataframe0.csv", encoding='euc-kr')
				#print(temp_df.head(5))
				
				#print("Route Check ==true : ",temp_df[temp_df['stopby']==0])

				try:
					Max_distance_row_point = temp_df[temp_df['stopby']==0].iloc[0]
			        
					temp_df.loc[temp_df['code']==Max_distance_row_point['code'],'stopby']=1
					#print(">>",temp_df[temp_df['code']== Max_distance_row_point['code']]['stopby'])
					#업데이트 현황
					trace_list, left_drive_time, left_kappa, total_distance, route_check, distance_list, time_list = \
self.situation_update(temp_df[temp_df['stopby']==0], Max_distance_row_point, left_kappa, trace_list, average_speed, left_drive_time, total_distance,day, get_up, get_off, distance_list, time_list)
 
					logger.info(f'>> start : {trace_list[-2]} |  arrive : {trace_list[-1]} | left time : { left_drive_time}  | left kappa : { left_kappa}')

					#현재 위치 변경
					current_point = trace_list[-1]

				except:
					trace_list, left_drive_time, left_kappa, total_distance, route_check, distance_list, time_list = \
self.situation_update(temp_df[temp_df['stopby']==0], Max_distance_row_point, left_kappa, trace_list, average_speed, left_drive_time, total_distance,day, get_up, get_off, distance_list, time_list)
					
					logger.info(f'>> start : {trace_list[-2]} |  arrive : {trace_list[-1]} | left time : { left_drive_time}  | left kappa : { left_kappa}')
					current_point = trace_list[-1]


		for k in route_list:
			print(k)



		tt.autolog()
		return temp_df, route_list, total_distance

