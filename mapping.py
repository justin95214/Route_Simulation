import os
import numpy as np
import pandas as pd
from collections import deque
import glob
import folium

def check_the_possible_mapping(df, work_time, day, df_element):
	#index >>  3 7 11 15 19 23


	possible_list = []
	impossible_list = []

	for i in range(len(df)):
		if i%4 == 3:
			
			track_list =[]
			temp_list_1 = df.iloc[i].to_list()
			#print(temp_list_1)
			## 바꿀곳
			left_drive_time_float = float(temp_list_1[1])
			if left_drive_time_float > 0 :
				track_list.append(left_drive_time_float)
				track_list.append(float(work_time) - left_drive_time_float)
				track_list.extend(df.iloc[i-3].to_list()[1:])
				possible_list.append(track_list)

			else:
				track_list.append(left_drive_time_float)
				track_list.append(float(999))
				track_list.extend(df.iloc[i-3].to_list()[1:])
				impossible_list.append(track_list)
							
	
	result_df = pd.DataFrame(possible_list)
	
	col_name_list = ['left_time','work_time']
	for j in range(1,result_df.shape[1]-1):
		col_name_list.append("P"+str(j))


	result_df.columns = col_name_list

	result_df = result_df.sort_values(by=["left_time"], ascending=[True])
	result_df.to_csv("./possible1/"+day+"_"+df_element+"_result.csv",encoding='euc-kr')
	

	result_df_T = result_df.transpose()
	
	T_col_name_list = []

	for k in range(result_df_T.shape[1]):
		T_col_name_list.append("Temp_Route"+str(k))
	
	result_df_T.columns = T_col_name_list
	
	result_df_T.to_csv("./possible1/"+day+"_"+df_element+"_result_T.csv",encoding='euc-kr')

	if impossible_list !=[]:
		im_result_df = pd.DataFrame(impossible_list)
		col_name_im_list = ['left_time','work_time']
		print(im_result_df.shape)
		for j in range(1,im_result_df.shape[1]-1):
			col_name_im_list.append("P"+str(j))
		im_result_df.columns = col_name_im_list	
		im_result_df.to_csv("./possible1/"+day+"_"+df_element+"_im_result.csv",encoding='euc-kr')
		im_result_df_T = im_result_df.transpose()
		
		T_col_name_im_list = []
		for k in range(im_result_df_T.shape[1]):
			T_col_name_im_list.append("Temp_Route"+str(999-k))
					
		im_result_df_T.columns = T_col_name_im_list
		im_result_df_T.to_csv("./possible1/"+day+"_"+df_element+"_im_result_T.csv",encoding='euc-kr')

	else:
		im_result_df_T = pd.DataFrame([])
		im_result_df_T.to_csv("./possible1/"+day+"_"+df_element+"_im_result_T.csv",encoding='euc-kr')	
	
	return result_df_T, im_result_df_T 


def mapping1(T_df, T_im_df, day, df_element):

	left_time_dict = {}
	work_time_dict = {}
	matched_list = []

	T_df = pd.concat([T_df, T_im_df], axis=1)

	for col, left in zip(T_df.columns, T_df.iloc[0]):
		left_time_dict[col+"-left"] = left
		#print(col+"-left", left)


	for col, work in zip(T_df.columns, T_df.iloc[1]):
		work_time_dict[col+"-work"] = work
		#print(col+"-work", work)

	work_time_dict = dict(sorted(work_time_dict.items(), key = lambda item: item[1], reverse= False))

	#for l, w in zip(left_time_dict.items(), work_time_dict.items()):
		#print(l, w)

	left_deque = deque(left_time_dict)
	work_deque = deque(work_time_dict)
	rest_deque = deque(left_time_dict)	

	length_dict = len(work_time_dict)

	count = 1
	work_left = []

	while left_deque:
					
		left_v = left_deque.popleft()
		work_temp_deque = deque()
		
		next = True
		for i in range(len(work_deque)):
			if next == False or left_v in work_left:
				break;

			else:
				tmp = []
				work_v = work_deque.popleft()
				#print(left_v, work_v)
				count+=1

				if left_time_dict[left_v] >= work_time_dict[work_v]:
					matched_list.append([left_time_dict[left_v] - work_time_dict[work_v],left_v.split("-")[0],work_v.split("-")[0]])
					next=False
					work_left.append(work_v.split("-")[0]+"-left")
					continue
				
					

				work_temp_deque.append(work_v)

			work_deque = work_temp_deque
		
		if count == length_dict * length_dict:
			print(count)
			break;
	
	
	flatten_list = sum(matched_list, [])

	while rest_deque:
		rest_v = rest_deque.popleft()
		str_rest_v = rest_v.split("-")[0]
		
		if not str_rest_v in flatten_list:
			matched_list.append([left_time_dict[rest_v], str_rest_v, ""])	

	for m in matched_list:	
		print(m)
	
	map1_df = pd.DataFrame(matched_list, columns = ['Left_Time', 'Match-1','Match-2'])
	map1_df.to_csv("./possible1/"+day+"_"+df_element+"_result_Match1.csv",encoding='euc-kr')

	return map1_df

def vlookup_data(map1_df, result_df_T, im_result_df_T, day, df_element):
	
	result_DF = result_df_T.transpose()
	im_result_DF = im_result_df_T.transpose()
	
	merge1_df = pd.merge(map1_df, result_DF, left_on= 'Match-1', right_index=True, how='inner')
	merge1_df = pd.merge(merge1_df, result_DF, left_on= 'Match-2', right_index=True, how='left')
	print(merge1_df.columns)

	try:
		merge1_df = merge1_df.drop(['left_time_x','work_time_x'], axis=1)
	except:
		pass

	try:
		merge1_df = merge1_df.drop(['left_time_y','work_time_y'], axis=1)
	except:
		pass


	merge2_df = pd.merge(map1_df, im_result_DF, left_on= 'Match-1', right_index=True)
	print(merge2_df.columns)

	try:
		merge2_df = merge2_df.drop(['left_time','work_time'], axis=1)
	except:
		pass
	
	try:
		merge2_df = merge2_df.drop(['left_time_y','work_time_y'], axis=1)
	except:
		pass


	m1 = merge1_df.values.tolist()
	m2 = merge2_df.values.tolist()
	
	m1.extend(m2)
	final_df = pd.DataFrame(m1)
	
	max_length = [max(0,len(x)) for x in m1][0] -3
	columns_list = ['Left_Time','Match-1','Match-2']
	
	print(max_length)

	for k in range(1,max_length+1):
		columns_list.append('P'+str(k))
	final_df.columns = columns_list

	final_df['P0'] = 'DP'
	print(final_df.columns)
	
	f_col =['Left_Time','Match-1','Match-2']
	f_col.extend(['P'+str(x) for x in range(max_length+1)])
	final_df = final_df[f_col]
	

	final_df.to_csv("./possible1/"+day+"_"+df_element+"_result_Match1_merge.csv",encoding='euc-kr')
	print(final_df.columns)

	return final_df



def location_xy(final_df, location_df, DP_df, day, df_element):
	
	final_df_T = final_df.transpose()
	
	cols_list = []
	for i in range(final_df_T.shape[1]):
		cols_list.append('Mapped_Route'+str(i))
		
	final_df_T.columns = cols_list
	final_df_T.to_csv("./possible1/"+day+"_"+df_element+"_result_mapping.csv",encoding='euc-kr')	

	located_df = location_df[['code', '경도(X좌표)', '위도(Y좌표)']]
	#located_df = pd.DataFrame(located_df, columns=[['code', '경도(X좌표)', '위도(Y좌표)']])

	if not os.path.isdir(df_element):
		os.mkdir(df_element)
	
	y = DP_df.loc[DP_df['DP']==df_element,'Latitude'].values[0]
	x = DP_df.loc[DP_df['DP']==df_element,'Longitude'].values[0]
	

	for i in range(final_df_T.shape[1]):
		index_col = 'Mapped_Route'+str(i)

		final_df_part =  pd.DataFrame(final_df_T[index_col], columns=[index_col])
		#final_df_part = final_df_part.replace(' ',np.NaN)
		final_df_part = final_df_part.dropna(axis=0, inplace =False)
		
		map1_df = pd.merge(final_df_part, located_df, left_on=index_col, right_on='code',  how='left')		
	
		map1_df.loc[map1_df[index_col]== 'DP','경도(X좌표)']=x
		map1_df.loc[map1_df[index_col]== 'DP','위도(Y좌표)']=y
	
		map1_df.to_csv("./"+df_element+"/"+day+"_"+df_element+"_result_map_merge_"+str(i)+".csv",encoding='euc-kr')
	
	return


def dataframe2html(route_list, day, df_element, location):
	print(route_list)	
	col_list = []
	for i in range(1, len(route_list[0])+1):
		col_list.append('P'+str(i))

	df = pd.DataFrame(route_list, columns= col_list)
	df.to_html('./map_test/'+df_element+"/"+day+location+'_route.html',encoding='euc-kr')


def draw_map(df_element, day):

	path0 =["map_test","./map_test/"+df_element+"/"]
	
	for p in path0:
		if not os.path.isdir(p):
			os.mkdir(p)



	path ="./"+df_element+"/*"

	file_list = glob.glob(path)
	file_list_csv = [file for file in file_list if file.endswith(".csv")]

	df = pd.read_csv(file_list_csv[0], encoding='euc-kr')
	
	y = df.loc[df[df.columns[1]]=="DP",'위도(Y좌표)'].values[0]
	x = df.loc[df[df.columns[1]]=="DP",'경도(X좌표)'].values[0]
	init_xy = [y, x]
	
	MM = folium.Map(location = init_xy, zoom_start=10)

	for i in file_list_csv:
		position_list = []
		position_name = []

		df = pd.read_csv(i, encoding='euc-kr')	
		location = df[df.columns[1]].values.tolist()
		df1 = df.replace(np.NaN, "")
		df1.to_html('./map_test/'+df_element+"/"+day+df.columns[1]+'_detail.html',encoding='euc-kr')		
		
		for idx, p in enumerate(location):
			if idx>=3 :
				if p == 'DP' or df_element in p:
					
					y = df.loc[df[df.columns[1]]==p,'위도(Y좌표)'].values[0]
					x = df.loc[df[df.columns[1]]==p,'경도(X좌표)'].values[0]
					position_list.append([y, x])
					position_name.append(p)			

		m = folium.Map(location = position_list[0], zoom_start=12)
		
		count = 1
		P_list =[]
		for P,M in zip(position_list, position_name):
			if M !='DP':
				folium.Marker(P, popup=str(count)+"-"+M).add_to(m)
				folium.Marker(P, popup=str(count)+"-"+M).add_to(MM)		
			else:
				folium.Marker(P, popup=str(count)+"-"+M, icon=folium.Icon(color='red')).add_to(m)
				folium.Marker(P, popup=str(count)+"-"+M, icon=folium.Icon(color='red')).add_to(MM)
			count+=1		
			P_list.append(M)

		folium.PolyLine(locations = position_list, tooltip='Polyline').add_to(m)
		folium.PolyLine(locations = position_list, tooltip='Polyline').add_to(MM)
		folium.Polygon(locations = position_list, fill=True, tooltip='Polygon').add_to(MM)

		#m.add_child(folium.ClickForMarker(popup= 'ClickForMarker'))
		m.save("./map_test/"+df_element+"/"+day+"_"+df.columns[1]+"_map_test.html")
		location_n = df.columns[1]
		dataframe2html([P_list], day, df_element, location_n)

	MM.save("./map_test/"+df_element+"/"+"total_"+"map_test.html")	

"""
loc = "부발"
df = pd.read_csv("./test2/월_"+loc+"_result.csv", encoding='euc-kr')
df_info = pd.read_excel('./sheet_5.xlsx')            
work_time = df_info[df_info['DP']==loc]['대당 운행시간(분)'].values.tolist()[0]

result_df_T, im_result_df_T = check_the_possible_mapping(df, work_time, '월', loc)
map1_df = mapping1(result_df_T, im_result_df_T, '월', loc)
vlookup_data(map1_df, result_df_T, im_result_df_T, '월', loc)
"""
