# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 18:03:05 2020

@author: André
"""
import json

def gen_vocab(terms, codes, path):
    l_vocab, l_corr = [], []
    for i in range(len(terms)):
        l_vocab.append(str(i) + '\t' + terms[i].lower().replace(' ', '_'))
        l_corr.append(str(i) + '=' + codes[i] + '=' + terms[i])
          
    #Label_vocab:
    #Label number  DeCSTerm    
    with open(path+'/label_vocab.txt', 'w', encoding='utf-8') as f:
        for i in l_vocab:
            f.write('%s\n' % i)

    #Label_correspondence:
    #Label number=DeCS Code=DeCSTerm          
    with open(path+'/label_correspondence.txt', 'w', encoding='utf-8') as f:
        for i in l_corr:
            f.write('%s\n' % i)
            
    #Creates a dict to be returned with the label correspondence
    #Dict Format = {DeCS Code: (label number, DeCS Term)}
    #dict_corr = {}
    #for i in range(len(l_corr)):
    #    dict_corr[l_corr[i].split('=')[1]] = (l_corr[i].split('=')[0], 
    #               l_corr[i].split('=')[2])

    #Label_map:
    #DeCSTerm -> sorted alphabetical
    with open(path+'/label_map.txt', 'w', encoding='utf-8') as f:
        terms.sort()
        for i in range(len(terms)):
            f.write('%s\n' % terms[i].lower().replace(' ', '_'))
            
    #return dict_corr


def gen_dict_label_corr(terms, codes):
    l_vocab, l_corr = [], []
    for i in range(len(terms)):
        l_vocab.append(str(i) + '\t' + terms[i].lower().replace(' ', '_'))
        l_corr.append(str(i) + '=' + codes[i] + '=' + terms[i])
            
    #Creates a dict to be returned with the label correspondence
    #Dict Format = {DeCS Code: (label number, DeCS Term)}
    dict_corr = {}
    for i in range(len(l_corr)):
        dict_corr[l_corr[i].split('=')[1]] = (l_corr[i].split('=')[0], 
                   l_corr[i].split('=')[2])
    
    return dict_corr

  
def convert_labels(l_labels, dict_labels):
    l_labels_name = []
    for i in range(len(l_labels)):
        #print(l_labels[i]) #DEBUG
        l_aux = []
        for l in range(len(l_labels[i])):
            #print(l_labels[i][l]) #DEBUG
            l_aux.append(dict_labels.get(l_labels[i][l])[1].lower().replace(' ', '_'))
            l_labels[i][l] = dict_labels.get(l_labels[i][l])[0]
        l_labels_name.append(l_aux)
    return l_labels, l_labels_name


def split_data(l_decs, l_abs, l_titles, df_size, trn_limit, tst_limit, xmlc_alg, l_decs_names='[]'):
    l_train_decs, l_train_decs_names, l_train_abs, l_train_title = [], [], [], []
    l_test_decs, l_test_decs_names, l_test_abs, l_test_title = [], [], [], []
    l_valid_decs, l_valid_abs, l_valid_title = [], [], []
    
    if xmlc_alg == 'X-Transformer':    
        for i in range(df_size):
            if i < trn_limit:
                l_train_decs.append(l_decs[i])
                l_train_decs_names.append(l_decs_names[i])
                l_train_abs.append(l_abs[i])
                l_train_title.append(l_titles[i])
            else:
                l_test_decs.append(l_decs[i])
                l_test_decs_names.append(l_decs_names[i])
                l_test_abs.append(l_abs[i])
                l_test_title.append(l_titles[i])
    else: #X-BERT
        for i in range(df_size):
            if i < trn_limit:
                l_train_decs.append(l_decs[i])
                l_train_abs.append(l_abs[i])
                l_train_title.append(l_titles[i])
            elif i < trn_limit + tst_limit:
                l_test_decs.append(l_decs[i])
                l_test_abs.append(l_abs[i])
                l_test_title.append(l_titles[i])    
            else:
                l_valid_decs.append(l_decs[i])
                l_valid_abs.append(l_abs[i])
                l_valid_title.append(l_titles[i])  
    
    return l_train_decs, l_train_decs_names, l_train_abs, l_train_title,\
            l_test_decs, l_test_decs_names, l_test_abs, l_test_title,\
            l_valid_decs, l_valid_abs, l_valid_title

    
def write_raw_files(l_text, l_decs_names, name):
    with open(name+'_raw_texts.txt', 'w', encoding='utf-8') as foutput:
        for i in range(len(l_text)):
            foutput.write('%s\n' % l_text[i])
    
    with open(name+'_raw_labels.txt', 'w', encoding='utf-8') as foutput:
        for i in range(len(l_decs_names)):
            str_final = ''
            for j in range(len(l_decs_names[i])):
                str_final = str_final + l_decs_names[i][j] + ' '
            foutput.write('%s\n' % str_final)

            
def write_file(l_text, l_decs, name):
    with open(name+'.txt', 'w', encoding='utf-8') as foutput:
        for i in range(len(l_text)):
            str_decs = str(l_decs[i]).replace('[', '').replace(']', '').replace(' ', '').replace('\'', '')
            str_final = str_decs + '\t' + l_text[i]
            foutput.write('%s\n' % str_final)
            
            
def write_json_output(out_path, l_pred_labs, l_pmid, dict_labels, eval_type, competition):
    dict_json = {"documents":[]}
    for i, j in zip(l_pred_labs, l_pmid):
        if competition == 'mesinesp':
            dict_aux = {"labels":[], "id":''} # For MESINESP
        else:
            dict_aux = {"labels":[], "pmid":''} #For bioASQ
        
        for z in i:
            dict_aux["labels"].append(str(z))
        
        if competition == 'mesinesp':
            dict_aux["id"] = j
        else:
            dict_aux["pmid"] = j
            
        dict_json["documents"].append(dict_aux)
        
    with open(out_path + competition + '_prediction_' + eval_type + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(dict_json, outfile, ensure_ascii=False, indent=4)