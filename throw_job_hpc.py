#!/usr/bin/env python

import subprocess

if __name__ == '__main__':

    for target_label in ['multimodality', 'globalstructure', 'separability', 'variablescaling', 'homogeneity', 'basinsizes', 'glcontrast']:
        for dim in [3, 5, 10, 20, 40, 80, 160, 320, 640]:
            for left_fun_id in range(1, 24+1):
                s_arg1 = 'arg1={}'.format(target_label)
                s_arg2 = 'arg2={}'.format(dim)
                s_arg3 = 'arg3={}'.format(left_fun_id)
                s_args = ','.join([s_arg1, s_arg2, s_arg3])
                subprocess.run(['qsub', '-l', 'walltime=72:00:00', '-v', s_args, 'job_hpc.sh'])
