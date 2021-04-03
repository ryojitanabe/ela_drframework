#!/usr/bin/env python

import subprocess

if __name__ == '__main__':
    all_feature_classes = ['basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'ela_level', 'ela_meta']
    # dim_redu = 'none'
    # #dim_redu = 'pca'
    
    for ela_feature_class in all_feature_classes:
        for dim in [2, 3, 5, 10, 20, 40, 80, 160, 320, 640]:
            for fun_id in range(1, 24+1):
                s_arg1 = 'arg1={}'.format(ela_feature_class)
                s_arg2 = 'arg2={}'.format(dim)
                s_arg3 = 'arg3={}'.format(fun_id)
                # s_arg4 = 'arg4={}'.format(dim_redu)
                s_args = ','.join([s_arg1, s_arg2, s_arg3])
                subprocess.run(['qsub', '-l', 'walltime=72:00:00', '-v', s_args, 'job_fc.sh'])
