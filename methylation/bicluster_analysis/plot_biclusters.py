"""
Load the factor matrices, and plot heatmaps of the biggest biclusters.
Also do hierarchical clustering to reorder rows/columns, add this hierarchy to
the plot, and add the healthy vs diseased labels.
"""

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from HMF.methylation.load_methylation import filter_driver_genes_std
from HMF.methylation.load_methylation import load_tumor_label_list

import numpy
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram


''' Plot settings. '''
# Size of figure
figsize = (15, 10) 

# Whether to show a black frame around plots
frame_on_dendrogram = False
frame_on_heatmap = True

# Sizes of the plots - [left,bottom,width,height]
dim_top_dendrogram = [0.15,0.85,0.8,0.15] 
dim_left_dendrogram = [0.,0.125,0.15,0.725]
dim_heatmap = [0.15,0.125,0.8,0.725]
dim_labels = [0.15,0.11,0.8,0.01]

# Font sizes axis ticks and labels
fontsize_ticks = 4
fontsize_labels = 15

# How much padding of heatmap xaxis labels to add for tumour labels
pad_labels = 15

# Image quality
dpi = 300


''' Hierarchical clustering settings. 
    Options for method:
       'single' (Nearest Point), 'complete' (Voor Hees), 'average' (UPGMA),
       'weighted' (WPGMA), 'centroid' (UPGMC), 'median' (WPGMC), 'ward' (increment)
'''
method = 'ward' # 'complete', 'weighted'
metric = 'euclidean'


''' Load in factor matrices. '''
folder_matrices = project_location+'HMF/methylation/bicluster_analysis/matrices/'

F_genes = numpy.loadtxt(folder_matrices+'F_genes')
F_samples = numpy.loadtxt(folder_matrices+'F_samples')
S_ge = numpy.loadtxt(folder_matrices+'S_ge')
S_pm = numpy.loadtxt(folder_matrices+'S_pm')
S_gm = numpy.loadtxt(folder_matrices+'S_gm')


''' Also load in list of genes and samples. '''
_, _, _, genes, samples = filter_driver_genes_std()
labels_tumour = load_tumor_label_list()


''' Method for computing dendrogram. Return order of indices. '''
def compute_dendrogram(R):
    #plt.figure()
    # Hierarchical clustering methods: 
    # single (Nearest Point), complete (Von Hees), average (UPGMA), weighted (WPGMA), centroid (UPGMC), median (WPGMC), ward (incremental)
    Y = linkage(y=R, method='centroid', metric='euclidean') 
    Z = dendrogram(Z=Y, orientation='top', no_plot=True)#False)
    reordered_indices = Z['leaves']
    return reordered_indices


''' Method for plotting specified biclusters. '''
def plot_heatmap_clustering_labels(R_kl, genes, samples, labels, plot_name):
    ''' Set up plot. '''
    fig = plt.figure(figsize=figsize)      

    ''' Do hierarchical clusterings on this matrix for the row and column reorderings. 
        Also plots the hierarchical clustering. '''
    # Set up dendrogram on top   
    ax1 = fig.add_axes(dim_top_dendrogram, frame_on=frame_on_dendrogram) 
    ax1.get_xaxis().set_visible(False)
    ax1.get_yaxis().set_visible(False)
    
    Y_samples = linkage(y=R_kl.T, method=method, metric=metric) 
    Z_samples = dendrogram(Z=Y_samples, orientation='top', no_plot=False)#False)
    reordered_indices_samples = Z_samples['leaves']  

    # Set up dendrogram on left side    
    ax2 = fig.add_axes(dim_left_dendrogram, frame_on=frame_on_dendrogram)
    ax2.get_xaxis().set_visible(False)
    ax2.get_yaxis().set_visible(False)
    
    Y_genes = linkage(y=R_kl, method=method, metric=metric) 
    Z_genes = dendrogram(Z=Y_genes, orientation='left', no_plot=False)#False)
    reordered_indices_genes = Z_genes['leaves']    
    
    ''' Reorder rows, columns, names, labels. '''
    R_kl_reordered = R_kl[reordered_indices_genes,:][:,reordered_indices_samples]
    genes_reordered = [genes[i] for i in reordered_indices_genes]
    samples_reordered = [samples[i] for i in reordered_indices_samples]
    labels_reordered = [labels[i] for i in reordered_indices_samples]
    
    ''' Plot heatmap. '''
    ax3 = fig.add_axes(dim_heatmap, frame_on=frame_on_heatmap) #(left,bottom,width,height)
    ax3.imshow(R_kl_reordered, aspect='auto', cmap=plt.cm.bwr, interpolation='nearest', vmin=-2, vmax=2)
    
    # Flip y-axis to make it align with heatmap
    ax3.invert_yaxis()    
    
    # Axes labels
    ax3.set_xlabel("Samples", fontsize=fontsize_labels)
    ax3.xaxis.set_label_position('bottom') 
    ax3.set_ylabel("Genes", fontsize=fontsize_labels)
    ax3.yaxis.set_label_position('right')   
    
    # Put the major ticks at the middle of each cell
    ax3.set_yticks(numpy.arange(R_kl.shape[0]), minor=False)
    ax3.set_xticks(numpy.arange(R_kl.shape[1]), minor=False)
    
    # Rotate x-labels 90 degrees    
    plt.xticks(rotation=90)
    
    # Show sample and gene names
    ax3.yaxis.tick_right()
    ax3.set_xticklabels(samples_reordered, minor=False, fontsize=fontsize_ticks)
    ax3.set_yticklabels(genes_reordered, minor=False, fontsize=fontsize_ticks)
    
    # Turn off all the ticks
    ax3 = plt.gca()
    for t in ax3.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax3.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
        
    # Move xaxis labels down a bit to make space for tumour labels
    ax3.tick_params(axis='x', which='major', pad=pad_labels)
    
    ''' Add the healthy vs diseased labels. '''
    labels_tumour_matrix = numpy.matrix([labels_reordered])
    ax4 = fig.add_axes(dim_labels, frame_on=frame_on_heatmap)
    ax4.imshow(labels_tumour_matrix, aspect='auto', cmap=plt.cm.coolwarm, interpolation='nearest', vmin=0, vmax=1)
    
    # Turn off axes
    ax4.get_xaxis().set_visible(False)
    ax4.get_yaxis().set_visible(False)
        
    ''' Store plot. '''
    fig.show()
    fig.savefig(plot_name, dpi=dpi)
    

''' Plot the specified biclusters. '''
folder_biclusters = project_location+'HMF/methylation/bicluster_analysis/plots_biclusters/'

biclusters = [ # list of S matrix, bicluster index (k,l), and dataset name
    #(S_ge, (0,1), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    (S_ge, (2,5), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (6,1), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (4,5), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (7,6), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (3,8), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (5,1), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (4,7), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
    #(S_ge, (7,9), 'ge'), #(S_pm, (0,1), 'pm'), (S_gm, (0,1), 'gm'),
]

for S, (k,l), name in biclusters:
    new_S = numpy.zeros(S.shape)
    new_S[k,l] = S[k,l]
    new_R = numpy.dot(F_genes, numpy.dot(new_S, F_samples.T))
    plot_name = folder_biclusters+"bicluster_%s_%s_%s" % (name,k,l)
    plot_heatmap_clustering_labels(new_R, genes, samples, labels_tumour, plot_name)