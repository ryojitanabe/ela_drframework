#!/usr/bin/env python

import numpy as np
from pflacco.pflacco import create_initial_sample
import cocoex  # only experimentation module
# import sobol_seq # this works for up to 80 dimensions
from pyDOE import lhs
import sys
import os
    
# Sample a set of solutions with the size "sample_size". 
def create_sample(fun, sampling_method, sample_size):
    dim = fun.dimension

    # Each solution is generated in the range [0,1]^dim.    
    if sampling_method == 'ilhs':     
        sample = create_initial_sample(n_obs=sample_size, dim=dim, type='lhs')
    elif sampling_method == 'random':     
        sample = np.random.random_sample((sample_size, dim))
    # sobol_seq is available for <= 80 dimensions
    # elif sampling_method == 'sobol':     
    #     sample = sobol_seq.i4_sobol_generate(dim, sample_size)
    elif sampling_method == 'lhs':     
        sample = lhs(dim, sample_size, criterion='center')
    else:
        error_msg = "Error: %s is not defined." %(sampling_method)
        raise Exception(error_msg)

    # Linearly map each solution from [0,1]^dim to [-5,5]^dim
    lbound = np.full(dim, -5.)
    ubound = np.full(dim, 5.)
    sample = (ubound - lbound) * sample + lbound

    # Evaluate each solution in the sample
    obj_values = []
    for x in sample:
        obj_values.append(fun(x))

    return sample, obj_values

# This function is based on https://github.com/numbbo/coco/blob/master/code-experiments/build/python/example_experiment_for_beginners.py
# For each BBOB function, 15 independent runs are perfromed on 15 instances, respectively (instance IDs: 1, 2, 3, 4, 5, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80)
# In contrast, for each large-scale BBOB function, instance IDs are 1, ..., 15.
# For the sake of simplicity, the instance IDs are set to 1, ..., 15 for both the BBOB and large-scale BBOB function sets.
def create_sample_bbob(bbob_suite='bbob', sample_multiplier=50, sampling_method='lhs', sample_dir_path='./sample_data', sample_id=0):
    sample_dir_path = os.path.join(sample_dir_path, '{}_multiplier{}_sid{}'.format(sampling_method, sample_multiplier, sample_id))
    os.makedirs(sample_dir_path, exist_ok=True)

    ### input
    output_folder = 'tmp'

    ### prepare
    suite = cocoex.Suite(bbob_suite, "", "")
    observer = cocoex.Observer(bbob_suite, "result_folder: " + output_folder)
    minimal_print = cocoex.utilities.MiniPrint()

    count_instance_id = 1
    
    ### go
    for problem in suite:  # this loop will take several minutes or longer
        problem.observe_with(observer)  # generates the data for cocopp post-processing

        # In our experiment, we used the noiseless BBOB function set for 2, 3, 5, and 10 dimensions and the large-scale BBOB function set for 20, 40, 80, 160, 320, and 640 dimensions. So, it is not needed to create samples for the noiseless BBOB function set with 20 and 40 dimensions.
        if bbob_suite == 'bbob' and problem.dimension >= 20:
            break

        sample_size = sample_multiplier * problem.dimension        
        sample, obj_values = create_sample(problem, sampling_method, sample_size)

        fun_id = int(problem.info.split('_f')[1].split('_')[0])
        # Actual instance ID
        #instance_id = int(problem.info.split('_i')[1].split('_')[0])
        instance_id = count_instance_id
        
        # Recode each pair of x and f(x) in a csv file    
        sample_data_file_path = os.path.join(sample_dir_path, 'x_f_data_{}_f{}_DIM{}_i{}.csv'.format(bbob_suite, fun_id, problem.dimension, instance_id))
        with open(sample_data_file_path, 'w') as fh:
            for x, obj_val in zip(sample, obj_values):
                data_str = '{},'.format(obj_val)                
                data_str += ','.join([str(y) for y in x])
                fh.write(data_str + '\n')

        count_instance_id += 1
        if count_instance_id > 15:
            count_instance_id = 1
                
        minimal_print(problem, final=problem.index == len(suite) - 1)
        
if __name__ == '__main__':
    # np.random.seed(seed=1)
    # random.seed(1)
    
    ## 1. Sample a set of solutions with the size = 50 * dimension on the noiseless BBOB functions
    create_sample_bbob(bbob_suite='bbob', sample_multiplier=50, sampling_method='lhs', sample_dir_path='./sample_data', sample_id=0)

    ## 2. Sample a set of solutions with the size = 50 * dimension on the large-scale BBOB functions
    create_sample_bbob(bbob_suite='bbob-largescale', sample_multiplier=50, sampling_method='lhs', sample_dir_path='./sample_data', sample_id=0)

    
