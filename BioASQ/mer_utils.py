# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:42:17 2020

@author: André
"""

import ast
import merpy

def write_mer_file(file_name, l_mer_terms):
    print('Writing MER terms into file ' + file_name + '_mer.txt')
    with open(file_name+'_mer.txt', 'w', encoding='utf-8') as fmerout:
        for j in range(len(l_mer_terms)):
            str_aux_mer = str(l_mer_terms[j]).replace('[', '').replace(']', '').replace('\'', '')
            fmerout.write('%s\n' % str_aux_mer)
            
def call_mer_2nd_run(l_mer_terms, l_text, lexicon):
    for i in range(len(l_mer_terms)):
        if l_mer_terms[i][0] == ' ':
            l_aux = merpy.get_entities(l_text[i], lexicon)
            
            print('>>>>>', l_aux) #DEBUG
            
            if len(l_aux) > 0:
                l_aux_2 = []
                if lexicon == 'decs_parlex':
                    for i in range(len(l_aux)):
                        #Spanish term
                        try:
                            if l_aux[i][2] not in l_aux_2:
                                l_aux_2.append(l_aux[i][2])
                            
                            try:
                                #black magic to convert from string representation to list
                                l_aux[i][3] = ast.literal_eval(l_aux[i][3])
                                
                                #DEBUG - decs_parlex
                                #print(l_mer_data[0]) #DeCS code
                                #print(l_mer_data[1]) #Parent Info Tuple
                                #print(l_mer_data[1][0]) #Parent DeCS code (if any)
                                #print(l_mer_data[1][1]) #Parent Name (if any)
                                
                                #Spanish Parent
                                if l_aux[i][3][1][1] != '-' and l_aux[i][3][1][1] not in l_aux_2:
                                    l_aux_2.append(l_aux[i][3][1][1])
                            
                            except IndexError:
                                l_aux_2.append(' ')
                                
                        except IndexError:
                            l_aux_2.append(' ')
                            
                l_mer_terms[i][0] = l_aux_2
                
    return l_mer_terms
                            
def call_simple_mer(l_text, num_cores=10, lexicon='decslex'):
    dict_mer_in = {}
    for j in range(len(l_text)):
        dict_mer_in[j] = l_text[j]

    #MERing
    dict_mer_out = {}
    
    #DeCS + synonymns lexicon
    dict_mer_out = merpy.get_entities_mp(dict_mer_in, lexicon, n_cores=num_cores)
    
    #Filters the content returned from MER. Only the term is needed
    l_mer_terms = []
    for j in range(len(dict_mer_out)):
        l_aux = []
        
        for t in dict_mer_out[j]:
            try:                
                if t[2] not in l_aux:
                    l_aux.append(t[2])
            except IndexError:
                #If MER couldn't find entities, it appends an empty space
                l_aux.append(' ') 
                
        l_mer_terms.append(l_aux)
    
    return l_mer_terms

def call_custom_mer(l_text, lexicon, num_cores=10):    
    dict_mer_in = {}
    for j in range(len(l_text)):
        dict_mer_in[j] = l_text[j]

    #MERing
    dict_mer_out = {}

    if lexicon == 'decsparlex':
        #DeCS + MeSH + Parents + En/Es
        dict_mer_out = merpy.get_entities_mp(dict_mer_in, 'decsparlex', n_cores=num_cores)
    
        #Filters the content returned from MER.
        l_mer_terms = []
        for j in range(len(dict_mer_out)):
            l_aux = []
            for t in dict_mer_out[j]:
                try:
                    #Spanish Term
                    if t[2] not in l_aux:
                        l_aux.append(t[2])
                        
                    #Selects the list of additional information
                    l_mer_data = t[3]
                    
                    try:
                        #black magic to convert from string representation to list
                        l_mer_data = ast.literal_eval(l_mer_data)
                        
                        #DEBUG - decs_parlex
                        #print(l_mer_data[0]) #DeCS code
                        #print(l_mer_data[1]) #Parent Info Tuple
                        #print(l_mer_data[1][0]) #Parent DeCS code (if any)
                        #print(l_mer_data[1][1]) #Parent Name (if any)
                        
                        #Spanish Parent
                        if l_mer_data[1][1] != '-' and l_mer_data[1][1] not in l_aux:
                            l_aux.append(l_mer_data[1][1])
                    except ValueError:
                        l_aux.append(' ')                
                except IndexError:
                    l_aux.append(' ')                
            l_mer_terms.append(l_aux)
                       
        return l_mer_terms

                    
def call_mer(l_abst, name, l_tits, lexicon, num_cores=10):    
    dict_mer_in = {}
    for j in range(len(l_abst)):
        dict_mer_in[j] = l_abst[j]

    #MERing
    dict_mer_out = {}

    #DeCS + MeSH + Parents + En/Es
    #dict_mer_out = merpy.get_entities_mp(dict_mer_in, 'decs_mesh_ParEn_lex', n_cores=10)

    #DeCS + MeSH + Parents + En/Es + CTD Entitity Linking (Chems ands Diseases) 
    #dict_mer_out = merpy.get_entities_mp(dict_mer_in, 'decs_mesh_ParEn_lex2', n_cores=20)
    
    #DeCS + synonymns lexicon
    if lexicon == 'decs_lex':
        dict_mer_out = merpy.get_entities_mp(dict_mer_in, 'decslex', n_cores=num_cores)
    
    #Filters the content returned from MER. Only the term is needed
    l_mer_terms = []
    for j in range(len(dict_mer_out)):
        l_aux = []
        l_mesh_aux = []
        for t in dict_mer_out[j]:
            try:
                #ISTO E PARA O DECS_MESH_PAREN_LEX.
                l_mer_data = t[3]
                
                try:
                    #black magic to convert from string representation to list
                    l_mer_data = ast.literal_eval(l_mer_data)
                    
                    #DEBUG - DECS_MESH_PAREN_LEX
                    #print(l_mer_data) #all
                    #print(l_mer_data[2]) #termo ingles
                    #print(l_mer_data[4][1]) #parent ingles
                    #
                    #DEBUG - DECS_MESH_PAREN_LEX2
                    #if l_mer_data[5] != None:
                    #    print(l_mer_data[5]) #Chems info
                    #    print(l_mer_data[5][0]) #Chems synonyms
                    #    print(l_mer_data[5][1]) #Chems drugbank
                    #    print(l_mer_data[5][2]) #Chems parents
                    #
                    #if l_mer_data[6] != None:
                    #    print(l_mer_data[6]) #Diseases info
                    #    print(l_mer_data[6][0]) #Diseases synonyms
                    #    print(l_mer_data[6][1]) #Diseases slimmaps
                    #    print(l_mer_data[6][2]) #Diseases parents
                    
                    #Termo Ingles
                    if l_mer_data[2] not in l_aux:
                        l_aux.append(l_mer_data[2])
                    
                    #Parent Ingles
                    if l_mer_data[4][1] != '-' and l_mer_data[4][1] not in l_aux:
                        l_aux.append(l_mer_data[4][1])                    
                    #l_aux.append(str(l_mer_data[2]) + ' ' + str(l_mer_data[4][1]))
                    
                    #Termo MeSH
                    #if l_mer_data[1] not in l_mesh_aux:
                    #    l_mesh_aux.append(l_mer_data[1])
                    #Termo MeSH Parent
                    #if l_mer_data[4][2] not in l_mesh_aux and l_mer_data[4][2] != '-':
                    #    l_mesh_aux.append(l_mer_data[4][2])
                    
                    #Chems
                    if l_mer_data[5] != None:
                        #Synonyms
                        if l_mer_data[5][0] != None and len(l_mer_data[5][0]) > 0:
                            #appends only the first synonym
                            l_aux.append(l_mer_data[5][0][0])
                            
                            #for d in l_mer_data[5][0]:
                            #    if d not in l_aux:
                            #        l_aux.append(d)
                       
                        #DrugBank
                        #if dict not empty
                        if len(l_mer_data[5][1].keys()) > 0:
                            for k, i in l_mer_data[5][1].items():
                                if i[0] not in l_aux: #common name
                                    l_aux.append(i[0])
                                #appends only first synonym
                                if i[1][0] not in l_aux:
                                    l_aux.append(i[1][0])
                                    
                                #for z in i[1]: #synonyms
                                #    if z not in l_aux:
                                #        l_aux.append(z)
                                    
                        #Parents
                        #if dict not empty
                        if len(l_mer_data[5][2].keys()) > 0:
                            for k, i in l_mer_data[5][2].items():
                                if i[2] not in l_aux:
                                    l_aux.append(i[2])
                                    
                    #Diseases
                    if l_mer_data[6] != None:
                        #Synonyms
                        if l_mer_data[6][0] != None and len(l_mer_data[6][0]) > 0:
                            #appends only the first synonym
                            l_aux.append(l_mer_data[6][0][0])
                            
                            #for d in l_mer_data[6][0]:
                            #    if d not in l_aux:
                            #        l_aux.append(d)
                                    
                        #Slimmaps
                        if l_mer_data[6][1] != None and len(l_mer_data[6][1]) > 0:
                            for d in l_mer_data[6][1]:
                                if d not in l_aux:
                                    l_aux.append(d)
                        #Parents
                        #if dict not empty
                        if len(l_mer_data[6][2].keys()) > 0:
                            for k, i in l_mer_data[6][2].items():
                                if i[2] not in l_aux:
                                    l_aux.append(i[2])
                                    
                except ValueError:
                    l_aux.append('-')
                    l_mesh_aux.append(' ')                    
                #ISTO E PARA O DECS_LEX. 
                #if t[2] not in l_aux:
                #    l_aux.append(t[2])
            except IndexError:
                #If MER couldn't find entities, then it appends the title of the abstract
                l_aux.append(l_tits[j])
                l_mesh_aux.append(' ')

        #l_mer_terms.append(l_aux + l_mesh_aux)
        l_mer_terms.append(l_aux)
    
    #print(l_mer_terms)    
# =============================================================================
#  IN CASE OF JOINING ANOTHER LEXICON     
# =============================================================================
#     #MERing - for CTD parents of terms lexicon
#     dict_mer_out = {}
#     dict_mer_out = merpy.get_entities_mp(dict_mer_in, 'decs_ont_parents', n_cores=10)
#     
#     for j in range(len(dict_mer_out)):
#         l_aux = []
#         for t in dict_mer_out[j]:
#             try:
#                 if t[2] not in l_aux:
#                     l_aux.append(t[2])
#             except IndexError:
#                     l_aux.append(' ')
# 
#         if l_aux[0] != ' ':
#             print(l_mer_terms[j])
#             l_mer_terms[j] = l_mer_terms[j] + l_aux
#             l_mer_terms[j] = list(dict.fromkeys(l_mer_terms[j])) #remove duplicates
#             print(l_mer_terms[j])
# =============================================================================
                   
    return l_mer_terms