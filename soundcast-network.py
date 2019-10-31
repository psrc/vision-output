# This file joins parcel geography ids to the shapefile and dissolves to create a viewable file for maps

import pandas as pd
import os
import geopandas as gp
from shapely.geometry import Point, LineString
import shutil

def create_network_shapefiles(inputs_location, outputs_location, current_tod):

    cols_to_keep = ['ij','vc','spd','spr','length','num_lanes','@tveh','@bveh','volume_delay_func']
    upd_cols = ['ij','vc','spd','spr','len','lanes','vehicles','buses','vdf']
    wgs_proj = os.path.join("C:/coding/vision-output/inputs","wgs1984.prj")
    network_file = os.path.join(inputs_location,"network_shape.csv")
    metric_file = os.path.join(inputs_location,"network_results.csv")

    print('Open csv files into a pandas dataframes')
    df_shape = pd.read_csv(network_file, sep = ',')
    df_output = pd.read_csv(metric_file, sep = ',')
    
    print('Pull out only links with lanes and vehicle capacity for the ' + current_tod + ' timeperiod')
    df_tod = df_output[(df_output['tod'] == current_tod) & (df_output['num_lanes'] > 0) & (df_output['data1'] > 0)]
    df_tod['vc'] = df_tod['@tveh'] / (df_tod['num_lanes'] * df_tod['data1'])
    df_tod['spd'] = (df_tod['length'] / df_tod['auto_time'])*60
    df_tod['spr'] = df_tod['spd'] / df_tod['data2']
    df_tod = df_tod.loc[:,cols_to_keep]
    df_tod.columns = upd_cols

    print('Add Metrics to the shapes for the '+ current_tod + ' timeperiod')
    df_current_shape = pd.merge(df_shape,df_tod,on='ij')

    print('Convert the ' + current_tod + ' timeperiod Network Shape CSV to a GeoDataframe')
    df_current_shape['geometry'] = df_current_shape.apply(lambda row: Point(row.lon, row.lat), axis=1)
    df_current_shape  = gp.GeoDataFrame(df_current_shape)

    print('Create a dataframe with network outputs by ij pair for the ' + current_tod + ' timeperiod')
    df_results = df_current_shape.loc[:,upd_cols]
    df_results = df_results.groupby(['ij']).quantile(0.5)

    print('Group the Paths by the IJ pair for the ' + current_tod + ' timeperiod')
    df_lines = df_current_shape.groupby(['ij'])['geometry'].apply(lambda x: LineString(x.tolist()))
    df_lines = gp.GeoDataFrame(df_results, geometry=df_lines, columns=['vc','spd','spr','len','lanes','vehicles','buses','vdf'])

    print('Write Out the GeoDataframe for the ' + current_tod + ' timeperiod to a Shapefile')
    df_lines.to_file(os.path.join(outputs_location,"network_shape_"+ current_tod +".shp"))
    working_projection = os.path.join(outputs_location,"network_shape_"+ current_tod +".prj")
    shutil.copyfile(wgs_proj, working_projection)
