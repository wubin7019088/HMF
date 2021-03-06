# Bayesian hybrid matrix factorisation for data integration

To appear in: 20th International Conference on Artificial Intelligence and Statistics (AISTATS 2017).

Authors: **Thomas Brouwer**, **Pietro Lio'**.

This project contains an implementation of the Bayesian hybrid matrix factorisation model presented in the paper **Bayesian hybrid matrix factorisation for data integration**. We furthermore provide all datasets used (including the preprocessing scripts), and Python scripts for experiments.

The folder structure is outlined below, giving details of where to find the code, data, and experiments. If you have any comments, please feel free to contact me (tab43 @ cam.ac.uk).


### Folder structure


#### /code/
Code for the HMF model, as well as other matrix factorisation models, helper methods, and more.
- **/Gibbs/** - Folder containing the general matrix factorisation Gibbs sampling updates, draws, and initialisations. This code does most of the heavy lifting.

  - **draws_Gibbs.py** - Code for drawing new values for matrix factorisation models using Gibbs sampling (given the parameter values).
  - **init_Gibbs.py** - Code implementing the different initialisation approaches for the Gibbs sampling parameters (random, expectation, K-means, least squares).
  - **updates_Gibbs.py** - Code for computing the Gibbs sampling posterior parameter updates.

- **/models/** - Classes that implement the actual matrix factorisation models - NMF, NMTF, BNMF, BNMTF, HMF. These use the code in /Gibbs/ extensively.

- **/distributions/** - Python classes that handle computing the mean and variance, and drawing samples, from the probability distributions used in the models.

- **/kmeans/** - Implementation of K-means clustering when the matrix is only partially observed. From [my other Github project](https://github.com/ThomasBrouwer/kmeans_missing).

- **/kernels/** - Classes for computing, storing, and loading, similarity kernels (Jaccard and Gaussian).

- **/statistics/** - Python code for computing the prediction errors of a list or matrix of values, compared to the observed values (MSE, R^2, Rp).

- **/model_selection/** - Classes that help with heuristic model selection of the BNMF and BNMTF models (using line search, grid search, or greedy search - see my [NIPS workshop paper](http://arxiv.org/abs/1610.08127)).

- **/cross_validation/** - Python scripts for performing in-matrix cross-validation experiments for non-probabilistic and Bayesian matrix factorisation models, and HMF. Some scripts also allow you to do model selection (either nested cross-validation, or using heuristics from NIPS workshop paper).

- **/generate_mask/** - Methods for helping generate observation matrices (1 indicating observed entries, 0 indicating unobserved).

- **/generate_toy/** - Method for generating toy/synthetic data for the HMF model.


#### /drug_sensitivity/
Data and scripts for drug sensitivity data integration experiments. Helper methods for loading in the datasets are provided in load_dataset.py.

- **/data/** - Data and preprocessing scripts for drug sensitivity application (GDSC, CTRP, CCLE IC50, CCLE EC50). See description.txt for more details on preprocessing steps.

- **/cross_validation/** - In-matrix cross-validation scripts and results for the different methods, for in-matrix predictions. Used in main paper.

- **/varying_sparsity/** - Experiments measuring the performance of the matrix factorisation methods (NMF, NMTF, BNMF, BNMTF, HMF D-MF, HMF D-MTF) as the sparsity of the GDSC and CTRP drug sensitivity datasets increases. Used in main paper.

- **/runtime/** - Measurements of the runtime performance of the different matrix factorisation models (HMF D-MF, HMF D-MTF, NMF, NMTF BNMF, BNMTF) on the drug sensitivity datasets. Used in supplementary materials.

- **/varying_init/** - Exploration of different initialisation methods for HMF D-MF and HMF D-MTF. Used in supplementary materials.

- **/varying_K/** - Exploration of effectiveness of ARD, by trying the HMF D-MF and HMF D-MTF models with different values of K, on the four drug sensitivity datasets. Used in supplementary materials.

- **/varying_negativity/** - Exploration of the trade-offs between the different negativity constraints (nonnegative, semi-nonnegative, real-valued), on the drug sensitivity datasets. Used in supplementary materials.

- **/varying_negativity_sparsity/** - Exploration of the trade-offs between the different negativity constraints (nonnegative, semi-nonnegative, real-valued), on the CTRP drug sensitivity dataset, when the sparsity of the datasets increases. Used in supplementary materials.

- **/varying_factorisation/** - Exploration of the trade-offs between the different factorisation combinations (all matrix factorisation, all matrix tri-factorisation, and everything in between), on the drug sensitivity datasets. Used in supplementary materials.

- **/bicluster_analysis/** - Analysis of biclusters of running HMF D-MTF on the four drug sensitivity datasets. Very incomplete; not used in paper.


#### /methylation/
Data and code for gene expression and methylation data integration experiments. Helper methods for loading in the datasets are provided in load_methylation.py.

- **/data/**
  - **/data_plots/** - Visualisation of the data sources (raw, standardised, and similarity kernels). Created by plot_distributions.py.
  - **/gene_classes/** - Gene classes for the genes in the methylation data, based on GO terms. See description.txt. Not used in paper.
  - **intogen-BRCA-drivers-data.geneid** - list of Entrez Gene ID's for the genes (in order of other datasets).
  - **matched_sample_label** - list of sample names, and whether they are tumour or healthy (in order of other datasets).
  - **matched_expression** - gene expression data (first row is sample names, first row is gene ids).
  - **matched_methylation_geneBody** - gene body methylation data (first row is sample names, first row is gene ids).
  - **matched_methylation_genePromoter** - promoter-region methylation data (first row is sample names, first row is gene ids).
  - **compute_correlation_datasets.py** - Computes the correlations of the three datasets. Used in supplementary materials.
  - **construct_similarity_kernels_genes.py**, **construct_similarity_kernels_samples.py** - Scripts that computes Gaussian similarity kernels for the three datasets, resulting in files: kernel_ge_std_genes, kernel_ge_std_samples, kernel_gm_std_genes, kernel_gm_std_samples, kernel_pm_std_genes, kernel_pm_std_samples.

- **/convergence/** - Script for running HMF D-MTF on the gene expression and promoter-region methylation data, to check convergence.

- **/cross_validation/** - Cross-validation scripts and results for the different methods, for out-of-matrix predictions. Used in main paper.

- **/varying_K/** - Exploration of effectiveness of ARD, by trying the HMF D-MF and HMF D-MTF models with different values of K, on the methylation and gene expression data. Used in supplementary materials.

- **/varying_negativity/** - Exploration of the trade-offs between the different negativity constraints (nonnegative, semi-nonnegative, real-valued), on the methylation and gene expression data. Used in supplementary materials.

- **/varying_factorisation/** - Exploration of the trade-offs between the different factorisation combinations (all matrix factorisation, all matrix tri-factorisation, and everything in between), on the methylation and gene expression data. Used in supplementary materials.

- **/bicluster_analysis/** - Analysis of biclusters of running HMF D-MTF on the gene expression and methylation datasets. Not used in paper.


#### /tests/
Unit tests (py.test) for a large portion of the implementations in /code/.


#### /toy_experiments/
Very brief tests on the toy dataset, mainly for checking convergence of the model.


### Usage
If you need any help running this code, please reach out!
If you wish to rerun the experiments, do not forget to change the *project_folder* variable in the appropriate files.
