#!/usr/bin/env python

import numpy as np
import pandas as pd
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
# from mlxtend.feature_selection import SequentialFeatureSelector as SFS
# from sklearn.feature_selection import RFE
            
def classification_lopo_cv(res_class_file_path, table_data_file_path, dim, left_fun_id, target_label):
    problem_info_columns = ['dim', 'fun', 'instance']
    high_level_prop_labels = ['multimodality', 'globalstructure', 'separability', 'variablescaling', 'homogeneity', 'basinsizes', 'glcontrast', 'fungroup']
                    
    table_df = pd.read_csv(table_data_file_path, header=0)
    table_df = table_df[table_df['dim'] == dim]
    
    # remove columns that include inf or nan
    table_df =table_df.replace([np.inf, -np.inf], np.nan)
    table_df = table_df.dropna(how='any', axis=1)

    # remove duplicated columns
    dup_columns = []
    # The first len(problem_info_columns) + len(high_level_prop_labels) should be ignored
    n_misc = len(problem_info_columns) + len(high_level_prop_labels)
    all_columns =  table_df.columns.values
    for column in all_columns[n_misc:]:
        unum = table_df[column].nunique()
        if unum == 1:
            dup_columns.append(column)            
    table_df = table_df.drop(dup_columns, axis=1)                

    # Split data sets into train and test datasets
    # Test data
    test_df = table_df[table_df['fun'] == left_fun_id]
    test_df = test_df.drop(columns=problem_info_columns)
    y_test = test_df[target_label].values
    test_df = test_df.drop(columns=high_level_prop_labels)
    X_test = test_df.values

    # train datasets
    train_df = table_df[table_df['fun'] != left_fun_id]
    train_df = train_df.drop(columns=problem_info_columns)
    y_train = train_df[target_label].values
    train_df = train_df.drop(columns=high_level_prop_labels)
    X_train = train_df.values
    
    # train
    estimator = RandomForestClassifier(n_estimators=1000, random_state=0)    
    estimator.fit(X_train, y_train)
    # test
    pred_labels = estimator.predict(X_test)
    score = accuracy_score(y_test, pred_labels)

    with open(res_class_file_path, 'w') as fh:
        fh.write(str(score))
                
if __name__ == '__main__':
    feature_set_name = 'lhs_multiplier50_sid0_basic_ela_distr_pca_limo_ic_disp_nbc_tpca2_ela_level_tpca2_ela_meta_dims3_5_10_20_40_80_160_320_640'
    table_data_file_path = os.path.join('./feature_table_data', '{}.csv'.format(feature_set_name))
    cross_valid_type = 'lopo_cv'
    res_class_dir_path = os.path.join('classification_results', feature_set_name)
    os.makedirs(res_class_dir_path, exist_ok=True)

    run_by_torque = False
    
    # Example 1. A sequential approach    
    if run_by_torque == False:
        for dim in [2, 3, 5, 10, 20, 40, 80, 160, 320, 640]:
            for left_fun_id in range(1, 24+1):
                for target_label in ['multimodality', 'globalstructure', 'separability', 'variablescaling', 'homogeneity', 'basinsizes', 'glcontrast', 'fungroup']:
                    res_class_file_path = os.path.join(res_class_dir_path, 'accuracy_{}_f{}_DIM{}.csv'.format(target_label, left_fun_id, dim))                
                    classification_lopo_cv(res_class_file_path, table_data_file_path, dim, left_fun_id, target_label)
    else:
        # Example 2. A pseudo parallel approach            
        target_label = sys.argv[1]
        dim = int(sys.argv[2])
        left_fun_id = int(sys.argv[3])
        res_class_file_path = os.path.join(res_class_dir_path, 'accuracy_{}_f{}_DIM{}.csv'.format(target_label, left_fun_id, dim))                
        classification_lopo_cv(res_class_file_path, table_data_file_path, dim, left_fun_id, target_label)
