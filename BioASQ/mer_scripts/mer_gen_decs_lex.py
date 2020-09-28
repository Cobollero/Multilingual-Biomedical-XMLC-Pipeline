# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:57:57 2020

@author: André
"""

import merpy
import pandas as pd

decs_data = pd.read_csv('../mesinesp_data/DeCS_data.tsv', sep='\t')

conv_dict = {}
for index, row in decs_data.iterrows():
    l_terms = str(row['Synonyms']).split('|')
    if row['Term_Spanish'] not in l_terms:
        l_terms.append(row['Term_Spanish'])
                                
    for i in l_terms:
        conv_dict[i] = str(row['#DeCS_code'])

merpy.create_lexicon(conv_dict.keys(), "decslex")
merpy.create_mappings(conv_dict, "decslex")
merpy.show_lexicons()
merpy.process_lexicon("decslex")

#DEBUG
merpy.get_entities("lo nervio abducens es una aurelia aurita", "decslex")