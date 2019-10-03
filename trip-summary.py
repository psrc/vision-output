# This script creates a parcel summary csv file for a specific shapefile
# Created by Puget Sound Regional Council Staff
# May 2018

import pandas as pd
import os

working_scenario = 'quick_kick'
working_directory = os.getcwd()
input_directory = os.path.join(working_directory,'inputs',working_scenario)

print("Reading the " + working_scenario + " scenario into a pandas dataframe")
trip_file = os.path.join(input_directory,'_trip.tsv')
trips = pd.read_csv(trip_file, sep = '\t')

trip_ends = ['opcl','dpcl']
parcels = []
i=0

for ends in trip_ends:
    print("Creating and outputting the " + working_scenario + " scenario " + ends + " by mode and purpose")
    keep_columns = [ends,'dpurp','mode']
    w_trips = trips.loc[:,keep_columns]
    w_trips['trips'] = 1

    w_parcels = w_trips.groupby([ends,'dpurp','mode']).sum()
    w_parcels = w_parcels.reset_index()
    w_parcels.columns = ['parcel_id','purpose','mode','trips']
    w_parcels['type'] = ends
    w_parcels['scenario'] = working_scenario
    
    if i==0:
        parcels = w_parcels
        
    else:
        parcels = parcels.append(w_parcels,ignore_index=True)
        
    i = i + 1
        
print("Outputting the final trip file to csv")
parcels.to_csv(os.path.join(input_directory,'trips_by_mode_and_purpose.csv'),index=False)


