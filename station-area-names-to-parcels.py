import pandas as pd
import os
import geopandas as gp

working_directory = os.getcwd()
input_directory = os.path.join(working_directory, 'inputs','shapefiles')
output_directory = os.path.join(working_directory, 'inputs')

# Shapefiles
parcel_file = os.path.join(input_directory,'parcel_centroids.shp')
lrt_stations = os.path.join(input_directory,'lrt_station_areas.shp')
lrt_projection = os.path.join(input_directory,'lrt_station_areas.prj')
state_plane = 'epsg:2285'

# Spatial Joing Function
def gp_spatial_join(target_shapefile,join_shapefile,coord_sys,keep_columns):
    
    # open join shapefile as a geodataframe
    join_layer = gp.GeoDataFrame.from_file(join_shapefile)
    join_layer.crs = {'init' :coord_sys}
    
    # open layer that the spaital join is targeting
    target_layer = gp.GeoDataFrame.from_file(target_shapefile)
    target_layer.crs = {'init' :coord_sys}
    
    # spatial join
    merged = gp.sjoin(target_layer, join_layer, how = "inner", op='intersects')
    merged = pd.DataFrame(merged)
    merged = merged[keep_columns]
    
    return merged

print('Join the Parcels and Light Rail Station Area Buffers')
columns_to_keep = ['PARCELID','stop_name']
parcel_stations = gp_spatial_join(parcel_file, lrt_stations, state_plane, columns_to_keep )
updated_names = ['parcel_id','station_name']
parcel_stations.columns = updated_names               

print('Create a full Parcel file to merge station names with and fill NaN with a blank value')
parcels_df = gp.GeoDataFrame.from_file(parcel_file)
columns_to_keep = ['PARCELID']
parcels = parcels_df.loc[:,columns_to_keep]
updated_names = ['parcel_id']
parcels.columns = updated_names 
parcels = pd.merge(parcels, parcel_stations, on='parcel_id',suffixes=('_x','_y'),how='left')
parcels.fillna("",inplace=True)

print('Output CSV file to disk')
parcels.to_csv(os.path.join(output_directory, 'parcels_w_lrt_station_names.csv'),index=False) 