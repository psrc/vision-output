# This file joins parcel geography ids to the shapefile and dissolves to create a viewable file for maps

import pandas as pd
import os
import geopandas as gp
import shutil
import time

working_directory = os.path.join(os.getcwd(),'inputs','shapefiles')
input_directory = os.path.join(os.getcwd(),'inputs')

geo_id = 'large_area'
lookup_file = os.path.join(input_directory,'large_area.csv')

# Shapefiles
parcel_file = os.path.join(working_directory,'prcl15_4k.shp')
parcel_projection = os.path.join(working_directory,'prcl15_4k.prj')
state_plane = 'epsg:2285'
working_projection = os.path.join(working_directory, geo_id +'_parcels.prj')

def gp_table_join(update_table,join_shapefile,join_field):
    
    # open join shapefile as a geodataframe
    join_layer = gp.GeoDataFrame.from_file(join_shapefile)

    # table join
    merged = join_layer.merge(update_table, on=join_field)
    
    return merged

start_of_production = time.time()

print('Open CSV file in Pandas for Table Join to Parcels')
wrk_lookup = pd.read_csv(lookup_file, sep = ',')

print('Join parcel lookup with parcel shapefile')
merged = gp_table_join(wrk_lookup,parcel_file,"parcel_id")
merged.fillna(0,inplace=True)

print('Output the dissolved shapefile to disk for use in mapping')
merged.to_file(os.path.join(working_directory,geo_id + '_parcels.shp'))
shutil.copyfile(parcel_projection, working_projection)

end_of_production = time.time()
print ('The Total Time for all processes took', (end_of_production-start_of_production)/60, 'minutes to execute.')
