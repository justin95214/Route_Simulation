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


# 패키지 설치
try:
	import module_source as ms
	logger.info("module import succeed!!\n")
except:
	libraries = ['numpy','pandas', 'io','folium']
	logger.warning("module import except process\n")

	for i in libraries:
		subprocess.check_call([sys.executables, '-m', 'pip', 'install', i])


	import module_source as ms

ms.pd.set_option('display.width', 500)


class sch_sys():
	
	def __init__(self, client, dp, df_info):
		
		try:
			self.client = client
			self.dp = dp
			self.df_info = df_info
			tt.autolog()
		except:
			tt.error_autolog()

	#데이터 로드
	def load_data(self):
		df_client = ms.pd.read_excel(self.client)
		df_DP = ms.pd.read_excel(self.dp)
		df_info = ms.pd.read_excel(self.df_info)
		tt.autolog()
		return df_client, df_DP, df_info

	#데이터프레임 병합	
	def merge_data(self, client, dp, how_way):
		df_merge = ms.pd.merge(left=client, right=dp, on="DP", how= how_way)
		tt.autolog()
		return df_merge

	#DP x,y 곡률값계산
	def cal_xy_DP(self, temp_df):
		temp_df['DP_y곡률값']=temp_df['Latitude']*3600
		temp_df['DP_x곡률값']=temp_df['Longitude']*3600
		tt.autolog()
		return temp_df

	def cal_xy_point(self, temp_df, current_point):
		y = temp_df[temp_df['code']==current_point]['경도(X좌표)'].values.tolist()[0]
		x = temp_df[temp_df['code']==current_point]['위도(Y좌표)'].values.tolist()[0]
		#print(x,y)

		temp_df[current_point+'_y곡률값']=x*3600
		temp_df[current_point+'_x곡률값']=y*3600
		#print(temp_df.head(5))
		return temp_df


	#client x,y 곡률값
	def cal_xy_client(self, temp_df):
		
		temp_df['x곡률값']=temp_df['경도(X좌표)']*3600
		temp_df['y곡률값']=temp_df['위도(Y좌표)']*3600
		tt.autolog()	
		return temp_df


	def cal_xy_from(self, temp_df, current_point):
		temp_df[current_point+'_y곡률값']=temp_df[temp_df['code']== current_point]['y곡률값'].values.tolist()[0]
		temp_df[current_point+'_x곡률값']=temp_df[temp_df['code']== current_point]['x곡률값'].values.tolist()[0]
		#print(temp_df.head(10))
		tt.autolog()
		return temp_df


	#현재 위치에서 거래처간 거리 계산
	def cal_xy_distance(self, temp_df, current_point):
		#print(temp_df.head(3))
		temp_df[current_point+'_경도거리']= abs(temp_df['x곡률값']-temp_df[current_point+'_x곡률값'])*0.0245
		temp_df[current_point+'_위도거리']= abs(temp_df['y곡률값']-temp_df[current_point+'_y곡률값'])*0.0306
		temp_df[current_point+'_운행거리'] = temp_df[current_point+'_위도거리']+temp_df[current_point+'_경도거리']
		temp_df[current_point+'_위도거리'] = temp_df[current_point+'_위도거리'].astype(float)
		temp_df[current_point+'_경도거리'] = temp_df[current_point+'_경도거리'].astype(float)
		#print(temp_df.columns)       
		tt.autolog()
		return temp_df



	
	#데이터프레임 초기화
	def dateframe_init(self, df_client, DF_element, week_num, day):
		temp_df = df_client.loc[df_client['DP']==DF_element].copy()

		#요일을 뺀 나머지 columns
		filter_columns = list(set(temp_df.columns.values.tolist())- set(week_num))

		#해당 요일은 filter_col에서 붙이기
		filter_columns.append(day)
		temp_df = temp_df[filter_columns]

		#얼마나 들렸는지 체크하기 위한 지표 stopby
		temp_df['stopby'] = 0
		#print(temp_df.head(10))
		#temp_df =temp_df.dropna(axis=0)
		tt.autolog()
		return temp_df

	#데이터프레임 방위각 계산
	def cal_azimuth(self, temp_df, current_point):

		CPI = math.pi
		CstLatVal = 0.0245
		CstLonVal = 0.0306
		CStVal = 3600
		#temp_df =temp_df.dropna(axis=0)
		temp_df['rad'] = ms.np.arctan2(temp_df[current_point+'_위도거리'],temp_df[current_point+'_경도거리']) 
		temp_df['deg'] = temp_df['rad'] * 180 / CPI
		tt.autolog()
		return temp_df

