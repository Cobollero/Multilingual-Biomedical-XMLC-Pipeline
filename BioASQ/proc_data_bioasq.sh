#!/bin/bash
#Executes the code to process the data given by BioASQand stores it in the format required for X-BERT
#
#Example run: ./proc_data_bioasq.sh
#

#The default number of CPUs in this script is set to 15.
#To change the number of CPUs, specify them here and change the number in --mer_cores to correspond to the number of CPUs in usage
CPUS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14

#Processes the text data given and uses MER to find entities in the text
nohup taskset -c ${CPUS} python processing_bioasq.py \
	-i1 bioasq_data/ \
	-i2 bioasq_data/MeSH_name_id_mapping.txt \
	-o proc_bioasq_data/ \
	--mer True --mer_cores 15 > processing_bioasq_log.txt

#Creates the directory for the BioASQ in the X-BERT datasets folder
mkdir -p ../X-BERT/datasets/BioASQ/mlc2seq/

#Then, copies the files required by X-BERT to the directory
cp proc_bioasq_data/label_vocab.txt ../X-BERT/datasets/BioASQ/mlc2seq/label_vocab.txt
cp proc_bioasq_data/train.txt ../X-BERT/datasets/BioASQ/mlc2seq/train.txt
cp proc_bioasq_data/test.txt ../X-BERT/datasets/BioASQ/mlc2seq/test.txt
cp proc_bioasq_data/valid.txt ../X-BERT/datasets/BioASQ/mlc2seq/valid.txt
