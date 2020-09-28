#!/bin/bash
#Executes the X-BERT algorithm to classify the 'unlabeled' test set to given by the BioASQ competitions.
#
#HOW TO RUN:
# ./run_xbert_aval.sh DATASET_FOLDER_NAME

echo '>>>> BEGIN <<<<'

#set parameters
DATASET=$1

ALGO=5
SEED=0

GPUS=0
CPUS=19,20,21,22,23,24,25,26,27,28,29

DEPTH=6
TRAIN_BATCH_SIZE=3
EVAL_BATCH_SIZE=3
LOG_INTERVAL=1000
EVAL_INTERVAL=20000
NUM_TRAIN_EPOCHS=10
LEARNING_RATE=5e-5
WARMUP_RATE=0.1

#Creates necessary dataset dirs
mkdir  -p datasets/${DATASET}_Aval/
mkdir  -p datasets/${DATASET}_Aval/mlc2seq/

#Moves the training and test files to the X-BERT newly created dataset dirs
cd ..
mv BioASQ/proc_bioasq_aval/train.txt X-BERT/datasets/${DATASET}_Aval/mlc2seq/train.txt
mv BioASQ/proc_bioasq_aval/test.txt X-BERT/datasets/${DATASET}_Aval/mlc2seq/test.txt
mv BioASQ/proc_bioasq_aval/valid.txt X-BERT/datasets/${DATASET}_Aval/mlc2seq/valid.txt
mv BioASQ/proc_bioasq_aval/label_vocab.txt X-BERT/datasets/${DATASET}_Aval/mlc2seq/label_vocab.txt

#label embedding and creating feature files
echo '>>>> LABEL EMBEDING AND DATA MATRICES <<<<'
cd X-BERT/datasets
taskset -c ${CPUS} python label_embedding.py --dataset ${DATASET}_Aval --embed-type elmo
cd ..
taskset -c ${CPUS} python -m datasets.preprocess_tfidf -i datasets/${DATASET}_Aval

# ranker (default: matcher=hierarchical linear)
echo '>>>> RANKER TRAINING <<<<'
MODEL_DIR=save_models/${DATASET}/elmo-a${ALGO}-s${SEED}
AVAL_DIR=save_models/${DATASET}_Aval/elmo-a${ALGO}-s${SEED}

mkdir -p $AVAL_DIR/ranker
taskset -c ${CPUS} python -m xbert.ranker train \
	-x datasets/${DATASET}_Aval/X.trn.npz \
	-y datasets/${DATASET}_Aval/Y.trn.npz \
	-c ${MODEL_DIR}/indexer/code.npz \
	-o ${AVAL_DIR}/ranker

echo '>>>> RANKER PREDICTION <<<<'
taskset -c ${CPUS} python -m xbert.ranker predict \
	-m ${AVAL_DIR}/ranker \
	-x datasets/${DATASET}_Aval/X.tst.npz \
	-y datasets/${DATASET}_Aval/Y.tst.npz \
	-c ${MODEL_DIR}/matcher/xbert/C_eval_pred.npz \
	-o ${AVAL_DIR}/ranker/tst.prediction.npz

echo '>>>> END <<<<'