# -*- coding: utf-8 -*-
"""
Created on Mon May 11 16:22:10 2020

@author: André
"""
import os
import json
import logging
import argparse
import pandas as pd

import text_files_utils as tfu
import mer_utils as mu
import stem_utils as su

def main(args):
    finput = args.input_file
    finput_decs = args.input_decs_file
    out_path = args.output_path
    xmlc_alg = args.xmlc_alg
    mer = args.mer
    lexicon = args.mer_lex
    n_cores = args.mer_cores
    
    #Checks if input files/paths exist
    assert os.path.exists(finput), "Input file/path doesn't exist"
    assert os.path.exists(finput_decs), "DeCS file/path doesn't exist"
    assert os.path.splitext(finput)[-1].lower() == '.json', "Input file isn't a \'.json\' file. Json file is required."
    assert os.path.splitext(finput_decs)[-1].lower() == '.tsv', "DeCS input file isn't a \'.tsv\' file. Tsv file is required."
    assert xmlc_alg == 'X-BERT' or xmlc_alg == 'X-Transformer', "Invalid XMLC algorithm. Valid values: X-BERT, X-Transformer."
    
    if not os.path.exists(out_path): 
        logging.info('Creating path %s' % out_path)
        print('Creating path %s' % out_path)
        os.mkdir(out_path)
    
    #Reads the DeCS terms file and stores them on separate lists
    logging.info('Reading DeCS terms file \'%s\' ...' % finput_decs)
    print('Reading DeCS terms file \'%s\' ...' % finput_decs)
    #decs_data = pd.read_csv('DeCS.2019.both.v5.tsv', sep='\t')
    decs_data = pd.read_csv(finput_decs, sep='\t')
    
    #Stores the terms in spanish and the respective DeCS Code in lists        
    l_term_spanish = decs_data['Term_Spanish'].astype(str).values.tolist()
    l_decs_code = decs_data['#DeCS_code'].astype(str).values.tolist()
    
    #Generates vocab and label_correspondence files and returns dict with label correspondence
    dict_labels = tfu.gen_dict_label_corr(l_term_spanish, l_decs_code)
    
    if xmlc_alg == 'X-Transformer':
        CON_TEST_SIZE = 95598
    else:
        CON_TEST_SIZE = 63732 
    
    logging.info('Reading MESINESP data \'%s\' ...' % finput)
    print('Reading MESINESP data \'%s\'...' % finput)

    with open(finput, 'r', encoding='utf-8') as json_input:    
        data = json.load(json_input)
        df_data = pd.json_normalize(data['articles'])
    df_size = len(df_data)
    
    l_abs_mesinesp = df_data['abstractText'].values.tolist()
    l_title_mesinesp = df_data['title'].values.tolist()
    l_decs_mesinesp = [0] * df_size
    l_journal_mesinesp = df_data['journal'].values.tolist()

    #Checks if all abstracts have text. If not, they are exchanged by the titles of the articles
    cnt_debug = 0
    for i in range(df_size):
        if l_abs_mesinesp[i] == 'No disponible' or l_abs_mesinesp[i] == 'No disponibl' or l_abs_mesinesp[i] == None or len(l_abs_mesinesp[i]) <= 0:
            if l_title_mesinesp[i] != 'No disponible' and l_title_mesinesp[i] != 'No disponibl' and l_title_mesinesp[i] != None and len(l_title_mesinesp[i]) > 0:
                l_abs_mesinesp[i] = l_title_mesinesp[i]
            else:
                l_abs_mesinesp[i] = l_journal_mesinesp[i]
            cnt_debug += 1
            
    #Checks if all titles have text. Otherwise, they are exchanged by the abstracts
    #so that MER doesn't break    
    cnt_debug = 0
    for i in range(df_size):               
        if l_title_mesinesp[i] == None or len(l_title_mesinesp[i]) <= 0:
            if l_abs_mesinesp[i] != None and len(l_abs_mesinesp[i]) > 0:
                l_title_mesinesp[i] = l_abs_mesinesp[i]
                cnt_debug += 1

    #Reads and adds extra data
    logging.info('Reading extra data ...')
    print('Reading extra data ...')
    
    with open('pubmed_extra_1.json', 'r', encoding='utf-8') as json_input_extra:
        extra_data = json.load(json_input_extra)
        df_extra_data = pd.json_normalize(extra_data['articles'])
    
    with open('pubmed_extra_2.json') as json_input_extra:
        extra_data = json.load(json_input_extra)
        df_extra_data = df_extra_data.append(pd.json_normalize(extra_data['articles']), ignore_index=True)
        
    """
    for i in range(3,9):
        with open('pubmed_extra_'+str(i)+'.json') as json_input_extra:
            extra_data = json.load(json_input_extra)
            df_extra_data = df_extra_data.append(pd.json_normalize(extra_data['articles']), ignore_index=True)
    """
        
    l_abs_extra = df_extra_data['abstractText.ab_es'].values.tolist()
    l_title_extra = df_extra_data['title_es'].values.tolist()
    l_decs_extra = df_extra_data['decsCodes'].values.tolist()
    l_decs_extra, _ = tfu.convert_labels(l_decs_extra, dict_labels)
    
    i=0
    while len(l_abs_mesinesp) < CON_TEST_SIZE:
        l_abs_mesinesp.append(l_abs_extra[i])
        l_title_mesinesp.append(l_title_extra[i])
        l_decs_mesinesp.append(l_decs_extra[i])
        i += 1
        
    #For titles
    l_lists = [(l_abs_mesinesp, l_title_mesinesp, l_decs_mesinesp, out_path+'/test_aval_tits_MER', 'test aval_tits_MER')]
    
    #Generate Stemmer
    su.check_nltk_punkt()
    stemmer = su.set_stemmer('spanish')
    
    for l in l_lists:            
        logging.info('Processing %s data...' % l[4])
        print('Processing %s data...' % l[4])
        l_stem_text = []
        
        if mer:
            l_mer = []
            logging.info('MERing using %s ...' % lexicon)
            print('MERing using %s ...' % lexicon)
            if lexicon == 'decs_lex':
                l_mer = mu.call_simple_mer(l[0], n_cores)
            else:
                l_mer = mu.call_custom_mer(l[0], lexicon, n_cores)
                
            #appends to the text the corresponding MER terms iddentified earlier
            for i in range(len(l[1])): #TITLES
                l[1][i] = l[1][i] + ' ' + str(l_mer[i])
                
            #for i in range(len(l[0])): #ABSTRACTS
            #    l[0][i] = l[0][i] + ' ' + str(l_mer[i])
            
        logging.info('Stemming...')
        print('Stemming...')
        l_stem_text = tfu.list_stemming(l[1], stemmer) #TITLES
        #l_stem_text = tfu.list_stemming(l[0], stemmer) #ABSTRACTS
    
        logging.info('Writing %s file' % l[3])
        print('Writing %s file' % l[3])
        tfu.write_file(l_stem_text, l[2], l[3])

    
#Begin
parser = argparse.ArgumentParser()

#Required parameters
parser.add_argument('-i', '--input-file', type=str, required=True,
                    help='Path to the JSON file containing the data to proccess')
parser.add_argument('-idecs', '--input-decs-file', type=str, required=True,
                    help='Path to the TSV file containing the DeCS terms data')
parser.add_argument('-o', '--output-path', type=str, required=True,
                    help='Path to the directory that will contain the output files')
parser.add_argument('-xmlc', '--xmlc_alg', type=str, required=True,
                    help='XMLC algorithm to use. Possible values: X-BERT, X-Transformer')

#Optional
parser.add_argument('--mer', type=bool, default=False, 
                    help='True to run MER on the data. \n'
                    'The entities found will be appended to the end of each abstract.')
parser.add_argument('--mer_lex', type=str, 
                    default='decs_lex', 
                    help='Lexicon to be used by MER. \n'
                    'Available lexicons: decs_lex, decs_parlex. \n'
                    'Default = decs_lex.')
parser.add_argument('--mer_cores', type=int, 
                    default=10, 
                    help='Number of cores available to run MER using multiprocessing.\n'
                    'It is necessary to specify the X cores to use when running the program with this option.\n'
                    'Example with 10 cores: \'taskset -c 0,1,2,3,4,5,6,7,8,9 python processing.py -i data.json (...) --mer True --mer_cores=10 \' \n'
                    'Default = 10.')

args = parser.parse_args()
logging.info(args)
print(args)
main(args)
logging.info('Finished processing')
print('Finished processing')