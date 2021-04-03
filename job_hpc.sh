#!/bin/sh

cd $PBS_O_WORKDIR

python property_classification.py $arg1 $arg2 $arg3
