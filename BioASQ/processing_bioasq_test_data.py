# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:03:12 2019

@author: André
"""

import os
import ast
import json
import logging
import argparse
from pandas.io.json import json_normalize

import mer_utils as mu
import stem_utils as su
import text_files_utils as tfu

def gen_dict_corr(terms, codes):
    l_vocab, l_corr = [], []
    for i in range(len(terms)):
        l_vocab.append(str(i) + '\t' + terms[i].lower().replace(' ', '_').replace(',',''))
        l_corr.append(str(i) + '=' + codes[i] + '=' + terms[i])
            
    #Creates a dict to be returned with the label correspondence
    #Dict Format = {MeSH Term: (label number, MeSH Code)}
    dict_corr = {}
    for i in range(len(l_corr)):
        dict_corr[l_corr[i].split('=')[2]] = (l_corr[i].split('=')[0], 
                   l_corr[i].split('=')[1])
    
    return dict_corr


def convert_labels(l_labels, dict_labels):
    for i in range(len(l_labels)):
        for l in range(len(l_labels[i])):
            l_labels[i][l] = dict_labels.get(l_labels[i][l])[0]

    return l_labels


def main(args):
    finput_folder = args.input_folder
    finput_mesh = args.input_mesh_file
    finput_bioasq = args.bioasq_file
    out_path = args.output_path
    dtype = args.dtype
    mer = args.mer
    n_cores = args.mer_cores
    
    assert os.path.exists(finput_folder), "Folder does not exist"
    assert os.path.exists(finput_mesh), "MeSH file/path doesn't exist"
    assert os.path.splitext(finput_mesh)[-1].lower() == '.txt', "MeSH input file isn't a \'.txt\' file. Txt file is required."
    assert dtype == 'txt' or dtype == 'json', "Invalid data type. Valid values: txt, json"
    
    if not os.path.exists(out_path): 
        logging.info('Creating path %s' % out_path)
        print('Creating path %s' % out_path)
        os.mkdir(out_path)
        
    with open(finput_mesh) as mesh_file: #MeSH_name_id_mapping.txt
        mesh_data = mesh_file.readlines()

        l_mesh_term, l_mesh_code = [], []
        for i in range(len(mesh_data)):
            l_mesh_term.append(mesh_data[i].split('=')[0])
            l_mesh_code.append(mesh_data[i].strip('\n').split('=')[1])
    
    #Generates vocab and label_correspondence files
    tfu.gen_vocab(l_mesh_term, l_mesh_code, out_path)
    
    #Generates dict with label correspondence {MeSH Term: (label number, MeSH Code)}
    dict_labels = gen_dict_corr(l_mesh_term, l_mesh_code)

    with open(finput_bioasq, 'r', encoding='utf-8') as bioasq_input:
        data = json.load(bioasq_input)
        df_bioasq = json_normalize(data['documents'])
    
    df_size = len(df_bioasq)

    l_mesh_bioasq = [0] * df_size
    l_abs_bioasq = df_bioasq['abstractText'].values.tolist()
    l_title_bioasq = df_bioasq['title'].values.tolist()     

    l_mesh, l_title, l_abs = [], [], []
    if dtype == 'json':            
        with open(finput_folder + 'bioasq_data_3.json', 'r', encoding='utf-8') as json_file:
            logging.info('Loading json file 3...')
            print('Loading json file 3...')
            data = json.load(json_file)
            df = json_normalize(data)
            
        df = df.dropna()
        
        #stores the values of the codes, abstracts and titles into different lists
        l_mesh = df['meshMajor'].values.tolist()
        l_abs = df['abstractText'].values.tolist()
        l_title = df['title'].values.tolist()
    
    else: #txt
        with open(finput_folder + 'bioasq_data_extra.txt', 'r', encoding='utf-8') as txt_file:
            logging.info('Loading txt file...')
            print('Loading txt file...')
            data = txt_file.readlines()
            for l in range(len(data)):
                aux = data[l].split('\t')
                l_mesh.append([aux[0]])
                l_title.append(aux[1])
                l_abs.append(aux[2])
    
            #Converts from string to list 
            for i in range(len(l_mesh)):
                l_mesh[i] = ast.literal_eval(l_mesh[i][0])

    logging.info('Converting labels...')
    print('Converting labels...')
    l_mesh = convert_labels(l_mesh, dict_labels)

    logging.info('Preparing data...')
    print('Preparing data...')
    CON_TEST_SIZE = 63732 #This value needs to change if the size of the test.txt file used to train the X-BERT model changes
    
    for i in range(0, CON_TEST_SIZE):
        if i < df_size:
            l_mesh_bioasq[i] = l_mesh_bioasq[i]
            l_abs_bioasq[i] = l_abs_bioasq[i].replace(',','').replace('\n','')
            l_title_bioasq[i] = l_title_bioasq[i].replace('\n','')
        else:
            l_mesh_bioasq.append(l_mesh[i])
            l_abs_bioasq.append(l_abs[i].replace(',','').replace('\n',''))
            l_title_bioasq.append(l_title[i].replace('\n',''))
    
    #Generate Stemmer
    su.check_nltk_punkt()
    stemmer = su.set_stemmer('english')

    l_lists = [(l_abs_bioasq, l_title_bioasq, l_mesh_bioasq, out_path+'test', 'test')]
               
    for l in l_lists:            
        logging.info('Processing %s data...' % l[4])
        print('Processing %s data...' % l[4])
        l_stem_text = []
        
        if mer:
            l_mer = []
            logging.info('MERing using mesh_lex...')
            print('MERing using mesh_lex...')
            l_mer = mu.call_simple_mer(l[0], n_cores, 'meshlex')
    
            #appends to the titles the corresponding MER terms iddentified earlier
            for i in range(len(l[1])):
                l[1][i] = l[1][i] + ' ' + str(l_mer[i])
            
        logging.info('Stemming...')
        print('Stemming...')
        l_stem_text = su.list_stemming(l[1], stemmer)

        logging.info('Writing %s file' % l[3])
        print('Writing %s file' % l[3])
        tfu.write_file(l_stem_text, l[2], l[3])

#Begin
parser = argparse.ArgumentParser()

#Required parameters
parser.add_argument('-i1', '--input-folder', type=str, required=True,
                    help='Path to the folder containing the BioASQ data')
parser.add_argument('-i2', '--input-mesh-file', type=str, required=True,
                    help='Path to the txt file containing the MeSH terms data')
parser.add_argument('-i3', '--bioasq-file', type=str, required=True,
                    help='Path to the BioASQ file given each week')
parser.add_argument('-o', '--output-path', type=str, required=True,
                    help='Path to the directory that will contain the output files')

#Optional
parser.add_argument('--dtype', '--data-type', type=str, default='txt',
                    help='To use the JSON files split from the original file given by BiOASQ or the converted .txt file with 318,658 articles.\
                    Default = txt. Possible values: json, txt.')             
parser.add_argument('--mer', type=bool, default=False, 
                    help='True to run MER on the data. \n'
                    'The entities found will be appended to the end of each abstract. \n'
                    'It is recommended the specification of the X cores when running the program with this option.\n'
                    'Example: \'taskset -c 0,1,2,3,4,5,6,7,8,9 python processing.py -i data.json (...) --mer True \'')
parser.add_argument('--mer_cores', type=int, 
                    default=10, 
                    help='Number of cores available to run MER using multiprocessing.\n'
                    'It is recommended the specification of the X cores when running the program with this option.\n'
                    'Example with 10 cores: \'taskset -c 0,1,2,3,4,5,6,7,8,9 python processing.py -i data.json (...) --mer True --mer_cores=10 \' \n'
                    'Default = 10.')

args = parser.parse_args()
print(args)
main(args)
print('Finished processing')