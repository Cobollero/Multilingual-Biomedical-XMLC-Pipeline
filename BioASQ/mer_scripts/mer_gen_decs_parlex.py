# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 16:17:48 2020

@author: André
"""

import merpy
import pandas as pd

with open('../mesinesp_data/DeCS_2019_parent_child.txt', encoding='utf-8') as finput:
    l_par_child = finput.readlines()

dict_child_par = {}    
for i in l_par_child: 
    aux = i.split(' ')
    dict_child_par[aux[1].replace('\n','')] = aux[0]
    
decs_data = pd.read_csv('../mesinesp_data/DeCS_data.tsv', sep='\t')

l_term_spanish = decs_data['Term_Spanish'].astype(str).values.tolist()
l_decs_code = decs_data['#DeCS_code'].astype(str).values.tolist()

decs_dict = {}
for i in range(len(l_decs_code)):
    decs_dict[l_decs_code[i]] = l_term_spanish[i]

conv_dict = {}
for index, row in decs_data.iterrows():
    l_terms = str(row['Synonyms']).split('|')
    if row['Term_Spanish'] not in l_terms:
        l_terms.append(row['Term_Spanish'])
    
    try:
        parent = dict_child_par.get(str(row['#DeCS_code']))
        if parent == None:
            parent = '-'
            parent_info = '-'
        else:
            parent_info = decs_dict.get(parent)
            if parent_info == None:
                parent_info = '-'
    except KeyError:
        parent = '-'
        parent_info = '-'
        
    parent_tup = (parent, parent_info)
                                
    for i in l_terms:
        conv_dict[i] = str([row['#DeCS_code'], parent_tup])
    
merpy.create_lexicon(conv_dict.keys(), "decsparlex")
merpy.create_mappings(conv_dict, "decsparlex")
merpy.show_lexicons()
merpy.process_lexicon("decsparlex")

#DEBUG
print(merpy.get_entities("lo nervio abducens es un gran temefós", "decsparlex"))