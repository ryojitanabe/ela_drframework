# A Dimensionality Reduction Framework for Exploratory Landscape Analysis

This repository provides the source code to reproduce results shown in the following paper:

> Ryoji Tanabe, **Towards Exploratory Landscape Analysis for Large-scale Optimization: A Dimensionality Reduction Framework**, GECCO2021, pdf, [exdata](https://drive.google.com/drive/folders/1MRiiirvi-bJmaO56h3xlZrGITR4oERIP?usp=sharing)

The weighting strategy-based PCA procedure in PCA-BO is used for dimensionality reduction. I used [the code of PCA-BO](https://github.com/wangronin/Bayesian-Optimization) provided by Dr. Hao Wang. Details of PCA-BO can be found in the following paper:

> Elena Raponi, Hao Wang, Mariusz Bujny, Simonetta Boria, Carola Doerr: **High Dimensional Bayesian Optimization Assisted by Principal Component Analysis**, Parallel Problem Solving from Nature (PPSN) 2020: 169-183, [link](https://arxiv.org/abs/2007.00925)

The source code highly depends on the flacco package:

> Pascal Kerschke and Heike Trautmann, **Comprehensive Feature-Based Landscape Analysis of Continuous and Constrained Optimization Problems Using the R-package flacco**. In Applications in Statistical Computing - From Music Data Analysis to Industrial Quality Improvement, 93-123 (2019), [link](https://arxiv.org/abs/1708.05258)
 
The source code is also based on the COCO framework:

> Nikolaus Hansen, Anne Auger, Raymond Ros, Olaf Mersmann, Tea Tu\check{s}ar, and Dimo Brockhoff, **COCO: A Platform for Comparing Continuous Optimizers in a Black-Box Setting**, Optimization Methods and Software, 36(1): 114-144 (2021), [link](https://arxiv.org/abs/1603.08785)

# Requirements

This code require R (=>3.6), Python (=>3.8), numpy, sklearn, and pyDOE. In addition, this code require the [flacco](https://github.com/kerschke/flacco) package (R), the [pflacco](https://github.com/Reiyan/pflacco) interface (Python), and the [cocoex](https://github.com/numbbo/coco) module (Python). Optionally, this code require [the Torque manager](https://github.com/adaptivecomputing/torque) for a pseudo parallel processing.

# Usage

The overall process is divided into the following four steps. Below, I explain each process step by step.
 
## 1. Create samples

First of all, samples (i.e., a set of solutions X) are needed for each function instance. The following command creates samples with the size 50 * dimensions on the BBOB functions with 2, 3, 5, 10, 20, 40, 80, 160, 320, 640 dimensions by the Latin hypercube sampling method, not the improved Latin hypercube sampling method. The results are saved in the "./sample_data" directory.

```
$ python sample.py
```

## 2. Compute features

Next, features are computed based on the sample for each function instance. The following command computes all features in the 'basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'ela_level', and 'ela_meta' classes on the BBOB functions with 2, 3, 5, 10, 20, 40, 80, 160, 320, 640 dimensions. Only for 'ela_level' and 'ela_meta', dimensionality reduction is performed. The resulting feature set is identical to "C7-D2" in the GECCO2021 paper. The results are saved in the "./ela_feature_dataset" directory.

```
$ python feature_computation.py
```

Although the above command performs a feature computation in a sequential manner, it is very slow. Optionally, features can be computed in a pseudo parallel manner by using [the Torque manager](https://github.com/adaptivecomputing/torque). After setting "run_by_torque" (line 71 in feature_computation.py) to True, please run the following command:

```
$ python throw_job_fc.py
```

I like Torque so much, but I do not know how many researchers in the evolutionary computation community have installed Torque on their computers. It would have been better if I implemented parallel computing by multiprocessing, instead of Torque.

## 3. Create feature table

After the features have been computed, it is needed to summarize them as table data. The following command create a table that consists of the 'basic', 'ela_distr', 'pca', 'limo', 'ic', 'disp', 'nbc', 'tpca2_ela_level', and 'tpca2_ela_meta' classes on the BBOB functions with 3, 5, 10, 20, 40, 80, 160, 320, 640 dimensions. Here, "tpca2" means the corresponding feature has been computed after the PCA transformation with m=2. The results are saved in the "./feature_table_data" directory.

```
$ python feature_aggregation.py
```

## 4. Classify the high-level properties of the 24 BBOB functions.

The following command performs a classification of the high-level properties of the 24 BBOB functions with 3, ..., 640 dimensions in the LOPO-CV manner. A random forest classification model will be applied to the above-mentioned feature table. The accuracy score will be saved in the "./classification_results" directory.

```
$ python property_classification.py
```

Classification can also be performed in a pseudo parallel manner by Torque. After setting "run_by_torque" (line 66 in property_classification.py) to True, please run the following command:

```
$ python throw_job_fc.py
```

## Note

For each function in the noiseless BBOB function set ('bbob'), I named the instance IDs to 1, ..., 15. However, they actually represent the instance IDs 1, 2, 3, 4, 5, 71, 72, 73, 74, 75, 76, 77, 78, 79, and 80, respectively. This is to keep a consistency with the large-scale BBOB function set ('bbob-largescale').
