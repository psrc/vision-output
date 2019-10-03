import pandas as pd
import os
import geopandas as gp

geo = "regional_growth_center"
working_directory = os.getcwd()
input_directory = os.path.join(working_directory, 'inputs','shapefiles')
output_directory = os.path.join(working_directory, 'inputs')

# Shapefiles
parcel_file = os.path.join(input_directory,'parcel_centroids.shp')
poly_file = os.path.join(input_directory,'urbcen.shp')
poly_projection = os.path.join(input_directory,'urbcen.prj')
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

print('Join the Parcels and Polygon Buffers')
columns_to_keep = ['PARCELID','NAME']
poly_joins = gp_spatial_join(parcel_file, poly_file, state_plane, columns_to_keep )
updated_names = ['parcel_id','rgc_name']
poly_joins.columns = updated_names               

print('Create a full Parcel file to merge ploygon names with and fill NaN with a blank value')
parcels_df = gp.GeoDataFrame.from_file(parcel_file)
columns_to_keep = ['PARCELID']
parcels = parcels_df.loc[:,columns_to_keep]
updated_names = ['parcel_id']
parcels.columns = updated_names 
parcels = pd.merge(parcels, poly_joins, on='parcel_id',suffixes=('_x','_y'),how='left')
parcels.fillna("",inplace=True)

print('Output CSV file to disk')
parcels.to_csv(os.path.join(output_directory, 'parcels_w_' + geo + '_names.csv'),index=False) 