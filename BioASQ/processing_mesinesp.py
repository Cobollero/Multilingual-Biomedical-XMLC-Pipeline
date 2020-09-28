# -*- coding: utf-8 -*-
"""
Processes the data file given by the MESINESP organizers and splits it into 
smaller files to be used by X-BERT or X-Transformer. 
It also generates the vocabulary file. 

@author: André Neves
"""

import os
import json
import logging
import argparse
import pandas as pd
from pandas import json_normalize

import text_files_utils as tfu
import mer_utils as mu
import stem_utils as su

def main(args):
    finput = args.input_file
    finput_decs = args.input_decs_file
    out_path = args.output_path
    xmlc_alg = args.xmlc_alg
    trn_rat = args.train_ratio
    tst_rat = args.test_ratio
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
    decs_data = pd.read_csv(finput_decs, sep='\t')
    
    #Stores the terms in spanish and the respective DeCS Code in lists        
    l_term_spanish = decs_data['Term_Spanish'].astype(str).values.tolist()
    l_decs_code = decs_data['#DeCS_code'].astype(str).values.tolist()
    
    #Generates vocab and label_correspondence files
    tfu.gen_vocab(l_term_spanish, l_decs_code, out_path)
    
    #Generates dict with label correspondence
    dict_labels = tfu.gen_dict_label_corr(l_term_spanish, l_decs_code)
    
    logging.info('Reading MESINESP data \'%s\' ...' % finput)
    print('Reading MESINESP data \'%s\'...' % finput)
    with open(finput, 'r', encoding='utf-8') as json_input:
        data = json.load(json_input)
        df_data = json_normalize(data)
    df_size = len(df_data)
    
    l_abs_mesinesp = df_data['abstractText'].values.tolist()
    l_title_mesinesp = df_data['title'].values.tolist()
    l_decs_mesinesp = df_data['decsCodes'].values.tolist()
    #l_decs_mesinesp = tfu.convert_labels(l_decs_mesinesp, dict_labels)
    l_decs_mesinesp, l_decs_names = tfu.convert_labels(l_decs_mesinesp, dict_labels)

    #Checks if all titles have text. Otherwise, they are exchanged by the abstracts
    #so that MER doesn't break     
    for i in range(df_size):
        if l_title_mesinesp[i] == None or len(l_title_mesinesp[i]) <= 0:
            if l_abs_mesinesp[i] != None and len(l_abs_mesinesp[i]) > 0:
                l_title_mesinesp[i] = l_abs_mesinesp[i]
                
    logging.info('Spliting the data into different sets...')
    print('Spliting the data into different sets...')
    trn_limit = int(df_size * trn_rat / 100)
    tst_limit = int(df_size * tst_rat / 100)
    
    l_train_decs, l_train_decs_names, l_train_abs, l_train_title,\
    l_test_decs, l_test_decs_names, l_test_abs, l_test_title,\
    l_valid_decs, l_valid_abs, l_valid_title = tfu.split_data(l_decs_mesinesp,\
                                                              l_abs_mesinesp,\
                                                              l_title_mesinesp,\
                                                              df_size,\
                                                              trn_limit, tst_limit,\
                                                              xmlc_alg,\
                                                              l_decs_names)
                                                              
    #For titles
    if xmlc_alg == 'X-Transformer': 
        l_lists = [(l_train_abs, l_train_title, l_train_decs, out_path+'train', 'train', l_train_decs_names),
                   (l_test_abs, l_test_title, l_test_decs, out_path+'test', 'test', l_test_decs_names)]
    else: #X-BERT
        l_lists = [(l_train_abs, l_train_title, l_train_decs, out_path+'train', 'train'),
                   (l_test_abs, l_test_title, l_test_decs, out_path+'test', 'test'),
                   (l_valid_abs, l_valid_title, l_valid_decs, out_path+'valid', 'valid')]
    
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
            if lexicon == 'decslex':
                l_mer = mu.call_simple_mer(l[0], n_cores)
            else:
                l_mer = mu.call_custom_mer(l[0], lexicon, n_cores)
    
            #appends to the titles the corresponding MER terms iddentified earlier
            for i in range(len(l[1])):
                l[1][i] = l[1][i] + ' ' + str(l_mer[i])
            
        logging.info('Stemming...')
        print('Stemming...')
        l_stem_text = su.list_stemming(l[1], stemmer)

        logging.info('Writing %s file' % l[3])
        print('Writing %s file' % l[3])
        tfu.write_file(l_stem_text, l[2], l[3])
        
        if xmlc_alg == 'X-Transformer':
            logging.info('Writing %s raw file' % l[3])
            print('Writing %s raw file' % l[3])
            tfu.write_raw_files(l_stem_text, l[5], l[3])
    
#Begin
parser = argparse.ArgumentParser()

#Required parameters
parser.add_argument('-i1', '--input-file', type=str, required=True,
                    help='Path to the JSON file containing the data to split and proccess')
parser.add_argument('-i2', '--input-decs-file', type=str, required=True,
                    help='Path to the TSV file containing the DeCS terms data')
parser.add_argument('-o', '--output-path', type=str, required=True,
                    help='Path to the directory that will contain the output files')
parser.add_argument('-xmlc', '--xmlc_alg', type=str, default='X-Transformer',
                    help='XMLC algorithm to use. Possible values: X-BERT, X-Transformer')
parser.add_argument('-trn', '--train-ratio', type=int,
                    default=70,
                    help='Percentage of the file that will be used as training set (value =< 100). \
                    Default = 60 for X-BERT, 70 for X-Transformer.')
parser.add_argument('-tst', '--test-ratio', type=int,
                    default=30,
                    help='Percentage of the file that will be used as test set (value =< 100). \
                    Default = 20 for X-BERT, 30 for X-Transformer.\
                    In X-BERT, the remaining percentage will be used as validation set. Default = 20.')

#Optional
parser.add_argument('--mer', type=bool, default=False, 
                    help='True to run MER on the data. \n'
                    'The entities found will be appended to the end of each title/abstract.')
parser.add_argument('--mer_lex', type=str, 
                    default='decslex', 
                    help='Lexicon to be used by MER. \n'
                    'Available lexicons: decslex, decsparlex. \n'
                    'Default = decslex.')
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