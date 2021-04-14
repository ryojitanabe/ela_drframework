#!/usr/bin/env python
import os
import numpy as np
import statistics as stat

def avg_accuracy(class_res_dir_path, high_level_label, dim):
    scores = []
    
    for fun_id in range(1, 24+1):
        res_class_file_path = os.path.join(class_res_dir_path, 'accuracy_{}_f{}_DIM{}.csv'.format(high_level_label, fun_id, dim))        
        with open(res_class_file_path, 'r') as fh:
            s_score = fh.read()
            scores.append(float(s_score))
            
    return stat.mean(scores)
                        
if __name__ == '__main__':
    class_res_dir_path = './classification_results/lhs_multiplier50_sid0_basic_ela_distr_pca_limo_ic_disp_nbc_tpca2_ela_level_tpca2_ela_meta_dims3_5_10_20_40_80_160_320_640'
    
    for high_level_label in ['multimodality', 'globalstructure', 'separability', 'variablescaling', 'homogeneity', 'basinsizes', 'glcontrast']:
        print("-"*60)
        print("High level classification property={}".format(high_level_label))
        for dim in [3, 5, 10, 20, 40, 80, 160, 320, 640]:
            res = avg_accuracy(class_res_dir_path, high_level_label, dim)
            print("Dimension={}, accuracy={}".format(dim, res))
