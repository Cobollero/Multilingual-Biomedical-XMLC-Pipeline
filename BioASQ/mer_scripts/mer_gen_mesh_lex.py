# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 16:04:44 2020

@author: André
"""

import merpy

with open('../bioasq_data/MeSH_name_id_mapping.txt', encoding='utf-8') as finput_terms:
    l_terms = finput_terms.readlines()

dict_terms = {}    
for i in l_terms: 
    aux = i.split('=')
    dict_terms[aux[0].strip()] = aux[1].replace('\n','')

with open('../bioasq_data/mesh_terms_synonyms.txt', encoding='utf-8') as finput_terms:
    l_terms_syn = finput_terms.readlines()

dict_terms_synonyms = {}    
for i in l_terms_syn: 
    aux = i.split('\t')
    dict_terms_synonyms[aux[0]] = aux[1].replace('\n','')

conv_dict = {}
for key, values in dict_terms_synonyms.items():
    l_synonyms = values.split(',')
    if key not in l_synonyms:
        l_synonyms.append(key)

    for i in l_synonyms:
        conv_dict[i.strip()] = dict_terms.get(key)

merpy.create_lexicon(conv_dict.keys(), "meshlex")
merpy.create_mappings(conv_dict, "meshlex")
merpy.show_lexicons()
merpy.process_lexicon("meshlex")

#DEBUG
print(merpy.get_entities("I like abdominal injuries", "meshlex"))
print(merpy.get_entities("I like Calcimycin", "meshlex"))
print(merpy.get_entities("I like Calcimycin it is a good aurelia aurita and Temefos is awesome! abate lowercase", "meshlex"))