# -*- coding: utf-8 -*-
"""
Processes the predictions made by the X-BERT/X-Transformer model and stores them in 
a json file with the required format by the MESINESP competition. 

@author: André Neves
"""

import os
import argparse
import logging
import numpy as np

import aval_utils as au
import text_files_utils as tfu

def main(args):
    vocab_path = args.vocab_path
    npz_file = args.npz_file
    out_path = args.output_path
    
    if not os.path.exists(out_path): 
        print('Creating path %s' % out_path)
        os.mkdir(out_path)

    with open(vocab_path + 'test.txt', 'r', encoding='utf-8') as ftest:
        test_lines = ftest.readlines()
        
    with open(vocab_path + 'label_correspondence.txt', 'r', encoding='utf-8') as flabels:
        labels = flabels.readlines()    
    
    #Stores test file labels
    print('processing labels...')
    l_test_labs = []
    for i in range(len(test_lines)):
        spli = test_lines[i].split('\t')
        l_test_labs.append(spli[0].split(','))
        test_lines[i] = spli[1]
        
    #Remove possible duplicates
    for i in range(len(l_test_labs)):
        l_test_labs[i] = list(dict.fromkeys(l_test_labs[i]))
            
    #Converts the labels of each article into int and sorts them inside the list
    l_aux = []
    for i in range(len(l_test_labs)):
        for j in l_test_labs[i]:
            l_aux.append(int(j))
        l_test_labs[i] = l_aux
        l_test_labs[i].sort()
        l_aux = []
    
    #Creates dictionary with the correspondence between the XBERT labels and the 
    #DeCS labels
    dict_labels, dict_labels_rev = {}, {}
    for i in range(len(labels)):
        dict_labels[labels[i].split('=')[0]] = (labels[i].split('=')[1], 
                   labels[i].split('=')[2].replace('\n',''))
        dict_labels_rev[labels[i].split('=')[1]] = (labels[i].split('=')[0], 
               labels[i].split('=')[2].replace('\n',''))
    
    #loads npz prediction file and stores the predictions in list. 
    data = np.load(npz_file)
    
    count = 0
    l_probs, l_aux = [], []
    for i, j in zip(data['indices'], data['data']):
        if count == 19: #number of predictions made by X-BERT/X-Transformer for each article
            l_probs.append(l_aux)
            l_aux = []
            count = 0
        else:
            l_aux.append((i,j))
            count += 1
    
    #Finds the best confidence threshold value to achieve the best score in the measures
    prob_baseline = 0
    prob_best_prec, prob_best_rec, prob_best_f1 = au.check_prob_min(l_probs, l_test_labs)
    #prob_best_rec = au.check_prob_min(l_probs, l_test_labs, 'rec')
    #prob_best_f1 = au.check_prob_min(l_probs, l_test_labs, 'f1')
    
    #Writes the predictions with a confidence value >= to the confidence threshold
    print('Writing files...')
    l_pred_labs = au.make_pred_list(l_probs, prob_baseline)
    tfu.write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, 'baseline', 'MESINESP')
        
    l_pred_labs = au.make_pred_list(l_probs, prob_best_prec)
    tfu.write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, 'prec', 'MESINESP')
    
    l_pred_labs = au.make_pred_list(l_probs, prob_best_rec)
    tfu.write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, 'rec', 'MESINESP')
    
    l_pred_labs = au.make_pred_list(l_probs, prob_best_f1)
    tfu.write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, 'f1', 'MESINESP')


#Begin
parser = argparse.ArgumentParser()

#Required parameters
parser.add_argument('-npz', '--npz-file', type=str, required=True,
                    help='Path to the .npz file containing the X-BERT/X-Transformer predictions.')
parser.add_argument('-i', '--vocab-path', type=str, required=True,
                    help='Path to the folder that contains the label_correspondence file and \
                    the .txt file for which the predictions were made')
parser.add_argument('-o', '--output-path', type=str, required=True,
                    help='Path to the directory that will contain the output prediction files')

args = parser.parse_args()
print(args)
main(args)
print('Finished processing')