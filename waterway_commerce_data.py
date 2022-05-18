#THIS IS A WORK-IN-PROGRESS PANDAS PROJECT FOR DEMO AND SHOWCASE: continuing to iterate and show what I'm learning

import datetime
from numpy import average
import pandas as pd

border_df = pd.read_csv('Border_Crossing_Entry_Data.csv')
border_df['Date'] = pd.to_datetime(border_df['Date'], format = '%b %Y').apply(lambda x: x.strftime('%Y-%m'))

#Quick exploration of data:
#print(border_df.info())
#print(border_df.head(20))

num_distinct_ports = border_df['Port Name'].nunique()
distinct_ports = border_df['Port Name'].unique()

#--> Try to make this more useful:
distinct_ports_per_state = border_df.groupby(['State'])['Port Name'].unique().reset_index()
measures = border_df.Measure.unique()
#print(distinct_ports_per_state)
#print(measures)
measures_per_state = border_df.groupby(['State'])['Measure'].unique().reset_index()
#print(measures_per_state)

#Really ungly and unpythonic...I just wanted to see if it would work. I would definitly make it two lines:
ohio_measure = (border_df[border_df.State == 'Ohio'].reset_index()).Measure.unique()
#print(ohio_measure)

no_personal_vehicles = border_df.Measure.isin(['Personal Vehicle Passengers',
 'Truck Containers Empty', 'Truck Containers Loaded', 'Trucks', 'Buses',
 'Bus Passengers', 'Pedestrians', 'Rail Containers Empty',
 'Rail Containers Loaded', 'Trains', 'Train Passengers'])
no_ohio = border_df[no_personal_vehicles]


no_ohio_port_df = no_ohio.groupby(['Port Name', 'Measure']).Value.sum().reset_index()
#print(no_ohio_port_df)

#Sort by date just for fun
sort_by_date = no_ohio.groupby(['Date', 'Measure']).Value.sum().reset_index()
sort_by_date['Value Difference'] = sort_by_date['Value'].diff().fillna(0)

port_measure_pivot_df = no_ohio_port_df.pivot(
    columns = 'Measure',
    index = 'Port Name',
    values = 'Value'
).reset_index()
#print(port_measure_pivot_df)

sort_by_date_pivot = sort_by_date.pivot(
    columns = 'Measure',
    index = 'Date'
).reset_index()
#print(sort_by_date_pivot)

only_personal_vehicles = border_df.Measure.isin(['Personal Vehicle'])
df_personal_vehicles = border_df[only_personal_vehicles]
alcan = border_df[border_df['Port Name'] == 'Alcan'].reset_index(drop = True)
print(alcan)

#__________________________________________________________________________________________________________

#Overall, has bus travel declined near borders?
border_bus_trend_df = sort_by_date[sort_by_date.Measure =='Bus Passengers'].reset_index(drop=True)

border_bus_trends_pivot = border_bus_trend_df.pivot(
    columns = 'Measure',
    index = 'Date'
).reset_index()
#print(border_bus_trends_pivot)

#Bus Alcan trends:
alcan_bus_trends_df = alcan[alcan.Measure == 'Buses'].reset_index(drop = True)
alcan_bus_trends_df['BDifference'] = alcan_bus_trends_df['Value'].diff(periods = -1).fillna(0)
print(alcan_bus_trends_df)
alcan_bus_date_df = alcan_bus_trends_df[['Date', 'Measure', 'Value', 'BDifference']].reset_index(drop = True)
alcan_bus_date_pivot = alcan_bus_date_df.pivot(
    columns = 'Measure',
    index = 'Date',
    values = ['Value', 'BDifference']
).reset_index()
print(alcan_bus_date_pivot)

#Bus Passengers trends:
alcan_bpassnger_trends_df = alcan[alcan.Measure == 'Bus Passengers'].reset_index(drop = True)
alcan_bpassnger_trends_df['PDifference'] = alcan_bpassnger_trends_df['Value'].diff(periods = -1).fillna(0)
alcan_bp_date_df = alcan_bpassnger_trends_df[['Date', 'Measure', 'Value', 'PDifference']].reset_index(drop = True)
alcan_pb_date_pivot = alcan_bp_date_df.pivot(
    columns = 'Measure',
    index = 'Date'
).reset_index()
print(alcan_pb_date_pivot)

#Merging tables bus df tables:
alcan_bus_trends = pd.merge(alcan_bus_date_pivot, alcan_pb_date_pivot, how='left')
print(alcan_bus_trends)
#Question: What percentage of the time does higher passenger mean higher bus traffic through Alcan per month?:
#alcan_bus_trends['RR'] = ((alcan_bus_trends.BDifference.Buses > 0) & (alcan_bus_trends.PDifference['Bus Passengers'] > 0)).astype(int)
#alcan_bus_trends['RF'] = ((alcan_bus_trends.BDifference.Buses > 0) & (alcan_bus_trends.PDifference['Bus Passengers'] < 0)).astype(int)
#alcan_bus_trends['FR'] = ((alcan_bus_trends.BDifference.Buses < 0) & (alcan_bus_trends.PDifference['Bus Passengers'] > 0)).astype(int)
#alcan_bus_trends['FF'] = ((alcan_bus_trends.BDifference.Buses < 0) & (alcan_bus_trends.PDifference['Bus Passengers'] < 0)).astype(int)
    #Instances when it nets to 0:
#alcan_bus_trends['00'] = ((alcan_bus_trends.BDifference.Buses == 0) & (alcan_bus_trends.PDifference['Bus Passengers'] == 0)).astype(int)
#alcan_bus_trends['R0'] = ((alcan_bus_trends.BDifference.Buses > 0) & (alcan_bus_trends.PDifference['Bus Passengers'] == 0)).astype(int)
#alcan_bus_trends['0R'] = ((alcan_bus_trends.BDifference.Buses == 0) & (alcan_bus_trends.PDifference['Bus Passengers'] > 0)).astype(int)
#alcan_bus_trends['F0'] = ((alcan_bus_trends.BDifference.Buses < 0) & (alcan_bus_trends.PDifference['Bus Passengers'] == 0)).astype(int)
#alcan_bus_trends['0F'] = ((alcan_bus_trends.BDifference.Buses == 0) & (alcan_bus_trends.PDifference['Bus Passengers'] < 0)).astype(int)

#---->Alternative way of setting it up:
alcan_bus_trends['BR'] = alcan_bus_trends.iloc[1:].BDifference.Buses.apply(lambda x: 'R' if x > 0 else ('0' if x == 0 else 'F'))
alcan_bus_trends['PR'] = alcan_bus_trends.iloc[1:].PDifference['Bus Passengers'].apply(lambda x: 'R' if x > 0 else ('0' if x == 0 else 'F'))
bus_alcan_crosstab = pd.crosstab(alcan_bus_trends['BR'], alcan_bus_trends['PR'], normalize=True).round(2)

#print("RR: " + str(alcan_bus_trends.RR.sum()))
#print("FF: " + str(alcan_bus_trends.FF.sum()))
#print("RF: " + str(alcan_bus_trends.RF.sum()))
#print("FR: " + str(alcan_bus_trends.FR.sum()))
#print("00: " + str(alcan_bus_trends['00'].sum()))
#print("R0: " + str(alcan_bus_trends['R0'].sum()))
#print("0R: " + str(alcan_bus_trends['0R'].sum()))
#print("F0: " + str(alcan_bus_trends['F0'].sum()))
#print("0F: " + str(alcan_bus_trends['0F'].sum()))

#Just for kicks, what is the percentage breakdown of the correlary between rising buses to pasnger traffic?:
print(bus_alcan_crosstab)

#Has Alcan bus traffic declined over the years?: from 1996-2018 --> the answer is yes, Alcan border bus traffic has on average has declined over the years.

def annual_avg(series):
    mean_list = []
    annual_sum = 0
    series_to_list = list(series)
    for index, i in enumerate(series_to_list):
        annual_sum += i
        if index % 12 == 0 and index != 0:
            mean_list.append(round((annual_sum/12), 2))
            annual_sum = 0
    return mean_list
print(annual_avg(alcan_bus_trends.Value.Buses))

#Has Alcan pasnger bus traffic declined over the years?: from 1996-2018 --> Yes, ditto ^^^!
print(annual_avg(alcan_bus_trends.Value['Bus Passengers']))

print(alcan_bus_trends)


