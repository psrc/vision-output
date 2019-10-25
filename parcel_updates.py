import pandas as pd
import os
import time

input_directory = os.path.join(os.getcwd(),'inputs')
output_directory = os.path.join(os.getcwd(),'outputs')

stc_dir = 'L:/vision2050/opusgit/urbansim_data/data/psrc_parcel/runs/awsmodel03/KEEP DSEIS STC run_6.run_2018_10_23_11_15/indicators'
rug_dir = 'L:/vision2050/opusgit/urbansim_data/data/psrc_parcel/runs/awsmodel04/KEEP DSEIS RUG run_5.run_2018_10_25_09_07/indicators'
tfg_dir = 'L:/vision2050/opusgit/urbansim_data/data/psrc_parcel/runs/awsmodel05/KEEP DSEIS TFG run_8.run_2018_10_29_15_01/indicators'

all_scenarios = [('STC',stc_dir),('RUG',rug_dir),('TFG',tfg_dir)]

start_of_production = time.time()

for scenario in all_scenarios:
    
    print('Working on the ' + scenario[0] + ' scenario')

    print('Open CSV file in Pandas for Parcels around Ferry Terminals')
    ferry_parcels = pd.read_csv(os.path.join(input_directory,'ferry-terminal-buffers.csv'), sep = ',')

    print('Open CSV file in Pandas for Parcel Capacity around Ferry Terminals')
    parcel_capacity = pd.read_csv(os.path.join(input_directory,'parcel_level_capacity.csv'), sep = ',')
    cols_to_keep = ['parcel_id','DUcapacity50','JOBSPcapacity50','DUdiff50','JOBSPdiff50']
    parcel_capacity = parcel_capacity.loc[:,cols_to_keep]
    parcel_capacity.rename(columns={'DUdiff50': 'remaining_dwelling_unit_capacity','JOBSPdiff50': 'remaining_job_capacity','DUcapacity50': 'dwelling_unit_capacity','JOBSPcapacity50': 'job_capacity'}, inplace=True)

    print('Open CSV file in Pandas for Parcel Results around Ferry Terminals for the Base Year for the ' + scenario[0] + ' scenario')
    parcel_outputs_base = pd.read_csv(os.path.join(scenario[1],'parcel__dataset_table__households_jobs__2017.tab'), sep = '\t')
    cols_to_keep = ['parcel_id','population','employment','households']
    parcel_outputs_base = parcel_outputs_base.loc[:,cols_to_keep]
    parcel_outputs_base.rename(columns={'population': 'population_2017','employment': 'employment_2017','households': 'households_2017'}, inplace=True)

    print('Open CSV file in Pandas for Parcel Results around Ferry Terminals for the Future Year for the ' + scenario[0] + ' scenario')
    parcel_outputs_future = pd.read_csv(os.path.join(scenario[1],'parcel__dataset_table__households_jobs__2050.tab'), sep = '\t')
    cols_to_keep = ['parcel_id','population','employment','households']
    parcel_outputs_future = parcel_outputs_future.loc[:,cols_to_keep]
    parcel_outputs_future.rename(columns={'population': 'population_2050','employment': 'employment_2050','households': 'households_2050'}, inplace=True)

    print('Merge the Capacity, Population and Jobs with the Ferry Parcel Table for the ' + scenario[0] + ' scenario')
    ferry_parcels = pd.merge(ferry_parcels,parcel_capacity,on='parcel_id')
    ferry_parcels = pd.merge(ferry_parcels,parcel_outputs_base,on='parcel_id')
    ferry_parcels = pd.merge(ferry_parcels,parcel_outputs_future,on='parcel_id')

    print('Export the ' + scenario[0] + ' dataframe to csv')
    ferry_parcels.to_csv(os.path.join(output_directory,'ferry-terminal-buffers-' + scenario[0] + '.csv'),index=False)

end_of_production = time.time()
print ('The Total Time for all processes took', (end_of_production-start_of_production)/60, 'minutes to execute.')
