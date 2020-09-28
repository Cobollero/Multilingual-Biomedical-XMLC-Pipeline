#!/bin/bash
#Executes the code to process the data given by MESINESP and stores it in the format required for X-BERT/X-Transformer.
#This script requires the name of the XMLC algorithm to use (X-BERT or X-Transformer) and a name to identify the dataset.
#
#HOW TO RUN: ./proc_data_mesinesp.sh XMLC_ALG DATASET_NAME
#
#Example run: ./proc_data_mesinesp.sh X-Transformer mesinesp
#

ALG=$1
DATASET=$2

#The default number of CPUs in this script is set to 15.
#To change the number of CPUs, specify them here and change the number in --mer_cores to correspond to the number of CPUs in usage
CPUS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14

if [ $ALG == 'X-Transformer' ]; then
	#Processes the MESINESP data for X-Transformer and uses MER to find entities in the text
	nohup taskset -c ${CPUS} python processing_mesinesp.py \
	-i1 mesinesp_data/MESINESP_data.json \
	-i2 mesinesp_data/DeCS_data.tsv \
	-o proc_mesinesp_data/ \
	--mer True --mer_cores 15 \
	--mer_lex decsparlex > processing_mesinesp_X-Transf_log.txt
	
	#Creates the directory for the BioASQ in the X-BERT datasets folder
	mkdir -p ../X-Transformer/datasets/${DATASET}

	#Then, copies the files required by X-BERT to the directory
	cp proc_mesinesp_data/label_map.txt ../X-Transformer/datasets/${DATASET}/mapping/label_map.txt
	cp proc_mesinesp_data/label_vocab.txt ../X-Transformer/datasets/${DATASET}/label_vocab.txt

	cp proc_mesinesp_data/train.txt ../X-Transformer/datasets/${DATASET}/train.txt
	cp proc_mesinesp_data/train_raw_labels.txt ../X-Transformer/datasets/${DATASET}/train_raw_labels.txt
	cp proc_mesinesp_data/train_raw_texts.txt ../X-Transformer/datasets/${DATASET}/train_raw_texts.txt

	cp proc_mesinesp_data/test.txt ../X-Transformer/datasets/${DATASET}/test.txt
	cp proc_mesinesp_data/test_raw_labels.txt ../X-Transformer/datasets/${DATASET}/test_raw_labels.txt
	cp proc_mesinesp_data/test_raw_texts.txt ../X-Transformer/datasets/${DATASET}/test_raw_texts.txt

elif [ $ALG == 'X-BERT' ]; then
	#Processes the MESINESP data for X-BERT and uses MER to find entities in the text
	nohup taskset -c ${CPUS} python processing_mesinesp.py \
	-i1 mesinesp_data/MESINESP_data.json \
	-i2 mesinesp_data/DeCS_data.tsv \
	-o proc_mesinesp_data/ \
	-xmlc X-BERT -trn 60 -tst 20 \
	--mer True --mer_cores 15 \
	--mer_lex decsparlex > processing_mesinesp_X-BERT_log.txt
	
	#Creates the directory for the BioASQ in the X-BERT datasets folder
	mkdir -p ../X-BERT/datasets/${DATASET}/mlc2seq

	#Then, copies the files required by X-BERT to the directory
	cp proc_mesinesp_data/label_vocab.txt ../X-BERT/datasets/${DATASET}/mlc2seq/label_vocab.txt
	cp proc_mesinesp_data/train.txt ../X-BERT/datasets/${DATASET}/mlc2seq/train.txt
	cp proc_mesinesp_data/test.txt ../X-BERT/datasets/${DATASET}/mlc2seq/test.txt
	cp proc_mesinesp_data/valid.txt ../X-BERT/datasets/${DATASET}/mlc2seq/valid.txt
else
	echo ${1} 'is not a valid XMLC algorithm. Valid values: X-Transformer, X-BERT'
fi

