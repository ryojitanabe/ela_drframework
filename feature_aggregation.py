#!/usr/bin/env python

import numpy as np
import pandas as pd
import csv
import sys
import os

def create_feature_table_data(table_file_path, feature_dir_path, all_feature_classes, dims):
    all_fun_ids = range(1, 24+1)
    all_instance_ids = range(1, 15+1)
    my_high_level_prop_names = ['multimodality', 'globalstructure', 'separability', 'variablescaling', 'homogeneity', 'basinsizes', 'glcontrast', 'fungroup']
    label_df = pd.read_csv('./high_level_fun_prop.csv', header=0)
    
    # 1. Set the name of each column
    column_names = []
    my_basic_feature_names = ['dim', 'fun', 'instance']
    column_names.extend(my_basic_feature_names)
    column_names.extend(my_high_level_prop_names)    
            
    # Extract the name of all the features
    dim = dims[0]
    instance_id = all_instance_ids[0]
    fun_id = all_fun_ids[0]        

    bbob_suite = 'bbob'
    if dim >= 20:
        bbob_suite = 'bbob-largescale'
    
    for ela_feature_class in all_feature_classes:
        feature_file_path = os.path.join(feature_dir_path, '{}_{}_f{}_DIM{}_i{}.csv'.format(ela_feature_class, bbob_suite, fun_id, dim, instance_id))        
        feature_data_set = np.loadtxt(feature_file_path, delimiter=",", comments="#", dtype=np.str)
        feature_names = feature_data_set[:, 0].tolist()
        column_names.extend(feature_names)   
        
    # 2. Make table data
    table_df = pd.DataFrame(columns=column_names)

    for dim in dims:
        bbob_suite = 'bbob'
        if dim >= 20:
            bbob_suite = 'bbob-largescale'

        for fun_id in all_fun_ids:
            data_dict = {}
            data_dict['dim'] = dim
            data_dict['fun'] = fun_id
            
            for label in my_high_level_prop_names:
                data_dict[label] = label_df.loc[fun_id - 1, label]

            # For each instance, recode the feature values
            for instance_id in all_instance_ids:
                data_dict['instance'] = instance_id
                
                for ela_feature_class in all_feature_classes:
                    feature_file_path = os.path.join(feature_dir_path, '{}_{}_f{}_DIM{}_i{}.csv'.format(ela_feature_class, bbob_suite, fun_id, dim, instance_id))                    
                    feature_data_set = np.loadtxt(feature_file_path, delimiter=",", comments="#", dtype=np.str)
                    for key, value in feature_data_set:
                        data_dict[key] = value                        
                table_df = table_df.append(pd.Series(data_dict), ignore_index=True)

    table_df.to_csv(table_file_path, index=False)    

if __name__ == '__main__':
    # Make table data by aggregating features
    #all_feature_classes = ['basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'ela_level', 'ela_meta']
    all_feature_classes = ['basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'tpca2_ela_level', 'tpca2_ela_meta']    
    dims = [3, 5, 10, 20, 40, 80, 160, 320, 640]

    # If you used another sampling method, please rewrite the following line.
    sample_method = 'lhs_multiplier50_sid0'
    feature_dir_path = './ela_feature_dataset/{}'.format(sample_method)    

    table_dir_path = './feature_table_data'
    os.makedirs(table_dir_path, exist_ok=True)

    features_str = '_'.join(all_feature_classes)
    dims_str = '_'.join([str(d) for d in dims])
    table_file_path = os.path.join(table_dir_path, '{}_{}_dims{}.csv'.format(sample_method, features_str, dims_str))

    create_feature_table_data(table_file_path, feature_dir_path, all_feature_classes, dims)
