# This file joins parcel geography ids to the shapefile and dissolves to create a viewable file for maps

import pandas as pd
import os
import geopandas as gp
#import time
import shutil

working_directory = os.path.join(os.getcwd(),'inputs','shapefiles')
input_directory = os.path.join(os.getcwd(),'inputs')
output_directory = os.path.join(os.getcwd(),'inputs','shapefiles','areas')

final_ids = [('tod_id',101,"lrt",'yes'),
             ('tod_id',102,"crt",'yes'),
             ('tod_id',103,"ferry",'yes'),
             ('tod_id',104,"brt",'yes'),
             ('tod_id',105,"rgc",'yes'),
             ('rgc_tod_id',101,"lrt",'yes'),
             ('rgc_tod_id',102,"crt",'yes'),
             ('rgc_tod_id',103,"ferry",'yes'),
             ('rgc_tod_id',104,"brt",'yes'),
             ('rgc_tod_id',105,"rgc",'yes'),
             ('hct_id',1,"hct",'yes'),
             ('minority_id',2,"minority",'yes'),
             ('poverty_id',2,"poverty",'yes')]

# Parcels and Shapefiles
lookup_file = os.path.join(input_directory,'parcel_lokups.csv')
parcel_file = os.path.join(working_directory,'parcels_urbansim_wgs84.shp')
parcel_projection = os.path.join(working_directory,'parcels_urbansim_wgs84.prj')

def gp_table_join(update_table,join_shapefile,join_field):
    
    # open join shapefile as a geodataframe
    join_layer = gp.GeoDataFrame.from_file(join_shapefile)

    # table join
    merged = join_layer.merge(update_table, on=join_field)
    
    return merged



def create_geography_files():
    
    print('Open CSV file in Pandas for Table Join to Parcels')
    wrk_lookup = pd.read_csv(lookup_file, sep = ',')

    print('Join parcel lookup with parcel shapefile')
    merged = gp_table_join(wrk_lookup,parcel_file,"parcel_id")
    merged.fillna(0,inplace=True)

    for ids in final_ids:
        print('Working on the '+ids[0] + ' ' +str(ids[1]) +' values')

        if ids[3] == 'yes':
            print('Trimming Out Parcels without activity Units')
            current = merged[(merged.population_2017 > 0) | (merged.population_2050 > 0) | (merged.employment_2017 > 0) | (merged.employment_2050 > 0)]
        
        else:
            print('All Parcels will be used for the dissolve')
            current = merged
        
        print('Trimming out unneccessary columns')
        cols_to_keep = ['parcel_id','geometry',ids[0]]
        current = current[cols_to_keep]    

        print('Removing rows that are not ' + ids[2])
        current = current[(current[ids[0]] == ids[1])]

        print('Dissolving the ' + ids[2] + ' shapefile')
        dissolved_shape = current.dissolve(by=ids[0])
    
        print('Output the dissolved '+ ids[2] + ' shapefile to disk for use in mapping')
        dissolved_shape.to_file(os.path.join(output_directory,ids[0] +'_' + ids[2] + '.shp'))
        working_projection = os.path.join(output_directory,ids[0] +'_' + ids[2] + '.prj')
        shutil.copyfile(parcel_projection, working_projection)

#start_of_production = time.time()
#end_of_production = time.time()
#print ('The Total Time for all processes took', (end_of_production-start_of_production)/60, 'minutes to execute.')
