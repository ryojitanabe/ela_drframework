#!/usr/bin/env python

import numpy as np
from pflacco.pflacco import create_feature_object, calculate_feature_set, calculate_features
import sys
import os

# For PCA-BO
from scipy.stats import rankdata, norm
from sklearn.decomposition import PCA

# This module is derived from the code of PCA-BO (https://github.com/wangronin/Bayesian-Optimization)
def scale_X(X, func_vals):
    X_mean = X.mean(axis=0)
    X_ = X - X_mean

    r = rankdata(func_vals)
    N = len(func_vals)
    w = np.log(N) - np.log(r)
    w /= np.sum(w)
    return X_ * w.reshape(-1, 1)

def compute_features(ela_feature_class, sample_data_file_path, feature_file_path, dim_redu='none', n_pca_components=None):
    bbob_lower_bound = -5
    bbob_upper_bound = 5
    
    n_cell_blocks = None
    if ela_feature_class in ['cm_angle', 'cm_conv', 'cm_grad', 'gcm']:
        n_cell_blocks = 3
    
    data_set = np.loadtxt(sample_data_file_path, delimiter=",", comments="#", dtype=np.float)
    sample_f = data_set[:, 0]
    sample_x = data_set[:, 1:]

    if dim_redu == 'pca' and len(sample_x[0]) <= n_pca_components:
        print("Warning. It is impossible to reduce the original dimension {} to a higher dimension {}, so skipped".format(len(sample_x[0]), n_pca_components))
        return 0    
    
    # Dimensionality reduction by the weighted PCA strategy in PCA-BO
    # https://github.com/wangronin/Bayesian-Optimization
    if dim_redu == 'pca':
        sample_x = scale_X(sample_x, sample_f)
        pca = PCA(n_components=n_pca_components, svd_solver='full')
        sample_x = pca.fit_transform(sample_x, sample_f)        

    if dim_redu == 'pca' and ela_feature_class in ['cm_angle', 'cm_conv', 'cm_grad', 'gcm']:
        # Normalize each point x in the sample X into the range [0,1]^m
        min_values = np.min(sample_x, axis=0)
        max_values = np.max(sample_x, axis=0)
        sample_x = (sample_x - min_values) / (max_values - min_values)
        bbob_lower_bound = 0
        bbob_upper_bound = 1        
        
    feat_object = create_feature_object(x=sample_x, y=sample_f, minimize=True, lower=bbob_lower_bound, upper=bbob_upper_bound, blocks=n_cell_blocks)    

    try:
        # The calculate_feature_set function returns a dictionary object 
        feature_dict = calculate_feature_set(feat_object, ela_feature_class)
    except rpy2.rinterface_lib.embedded.RRuntimeError as e:
        print(e)

    with open(feature_file_path, 'w') as fh:
        for key, value in feature_dict.items():
            fh.write('{},{}\n'.format(key, value))            
            
if __name__ == '__main__':
    # Compute features by using pflacco
    sample_method = 'lhs_multiplier50_sid0'
    sample_dir_path = os.path.join('./sample_data', sample_method)

    run_by_torque = False
    
    # Example 1. A sequential approach    
    if run_by_torque == False:
        all_feature_classes = ['basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'ela_level', 'ela_meta']
        #all_feature_classes = ['cm_angle', 'cm_conv', 'cm_grad', 'gcm']
        n_pca_components = 2

        for ela_feature_class in all_feature_classes:
            dim_redu = 'none'
            # Only for 'ela_level' and 'ela_meta', dimensionality reduction is performed
            # If you want to compute the 'ela_level' and 'ela_meta' features as is, please comment out the following three lines:
            if ela_feature_class in ['ela_level', 'ela_meta']:
            #if ela_feature_class in ['cm_angle', 'cm_conv', 'cm_grad', 'gcm']:
                dim_redu = 'pca'

            for dim in [2, 3, 5, 10, 20, 40, 80, 160, 320, 640]:
                bbob_suite = 'bbob'
                if dim >= 20:
                    bbob_suite = 'bbob-largescale'

                for fun_id in range(1, 24+1):
                    for instance_id in range(1, 15+1):                    
                        sample_data_file_path = os.path.join(sample_dir_path, 'x_f_data_{}_f{}_DIM{}_i{}.csv'.format(bbob_suite, fun_id, dim, instance_id))
                        feature_dir_path = os.path.join('./ela_feature_dataset', sample_method)                    
                        os.makedirs(feature_dir_path, exist_ok=True)
                        feature_file_path = os.path.join(feature_dir_path, '{}_{}_f{}_DIM{}_i{}.csv'.format(ela_feature_class, bbob_suite, fun_id, dim, instance_id))
                        if dim_redu == 'pca':
                            feature_file_path = os.path.join(feature_dir_path, 'tpca{}_{}_{}_f{}_DIM{}_i{}.csv'.format(n_pca_components, ela_feature_class, bbob_suite, fun_id, dim, instance_id))

                        compute_features(ela_feature_class, sample_data_file_path, feature_file_path, dim_redu, n_pca_components)
                        print("Done: Feature={}, dimension={},  f={}, instance ID={}".format(ela_feature_class, dim, fun_id, instance_id))                    
    else:
        # Example 2. A pseudo parallel approach    
        ela_feature_class = sys.argv[1]
        dim = int(sys.argv[2])
        fun_id = int(sys.argv[3])
        #dim_redu = sys.argv[4]
        #n_pca_components = int(sys.argv[5])
        n_pca_components = 2

        dim_redu = 'none'
        # Only for 'ela_level' and 'ela_meta', dimensionality reduction is performed
        # If you want to compute the 'ela_level' and 'ela_meta' features as is, please comment out the following three lines:
        if ela_feature_class in ['ela_level', 'ela_meta']:
            #if ela_feature_class in ['cm_angle', 'cm_conv', 'cm_grad', 'gcm']:
            dim_redu = 'pca'

        bbob_suite = 'bbob'
        if dim >= 20:
            bbob_suite = 'bbob-largescale'

        for instance_id in range(1, 15+1):                    
            sample_data_file_path = os.path.join(sample_dir_path, 'x_f_data_{}_f{}_DIM{}_i{}.csv'.format(bbob_suite, fun_id, dim, instance_id))

            feature_dir_path = os.path.join('./ela_feature_dataset', sample_method)                    
            os.makedirs(feature_dir_path, exist_ok=True)
            feature_file_path = os.path.join(feature_dir_path, '{}_{}_f{}_DIM{}_i{}.csv'.format(ela_feature_class, bbob_suite, fun_id, dim, instance_id))
            if dim_redu == 'pca':
                feature_file_path = os.path.join(feature_dir_path, 'tpca{}_{}_{}_f{}_DIM{}_i{}.csv'.format(n_pca_components, ela_feature_class, bbob_suite, fun_id, dim, instance_id))

            compute_features(ela_feature_class, sample_data_file_path, feature_file_path, dim_redu=dim_redu, n_pca_components=n_pca_components)
            print("Done: Feature={}, dimension={},  f={}, instance ID={}".format(ela_feature_class, dim, fun_id, instance_id))
        
