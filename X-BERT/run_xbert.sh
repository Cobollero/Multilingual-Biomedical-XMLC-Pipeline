#!/bin/bash
#Executes the X-BERT algorithm with all the required steps to produce the .npz file containing the predictions for the given dataset.
#
#HOW TO RUN:
# ./run_xbert.sh DATASET_FOLDER_NAME BERT_MODEL_NAME

echo '>>>> BEGIN <<<<'

#set parameters
DATASET=$1
BERT_MODEL=$2

ALGO=5
SEED=0

GPUS=0
CPUS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14

DEPTH=6
TRAIN_BATCH_SIZE=3
EVAL_BATCH_SIZE=3
LOG_INTERVAL=1000
EVAL_INTERVAL=20000
NUM_TRAIN_EPOCHS=8
LEARNING_RATE=5e-5
WARMUP_RATE=0.1

#label embedding and creating feature files
echo '>>>> LABEL EMBEDING AND DATA MATRICES <<<<'
cd datasets
taskset -c ${CPUS} python label_embedding.py --dataset ${DATASET} --embed-type pifa
cd ..
taskset -c ${CPUS} python -m datasets.preprocess_tfidf -i datasets/${DATASET}

# indexer
echo '>>>> INDEXER <<<<'
OUTPUT_DIR=save_models/${DATASET}/pifa-a${ALGO}-s${SEED}
mkdir -p $OUTPUT_DIR/indexer
python -m xbert.indexer \
	-i datasets/${DATASET}/L.pifa.npz \
	-o ${OUTPUT_DIR}/indexer \
	-d ${DEPTH} --algo ${ALGO} --seed ${SEED} --max-iter 20

# preprocess data_bin for neural matcher
echo '>>>> PREPROCESS <<<<'
OUTPUT_DIR=save_models/${DATASET}/pifa-a${ALGO}-s${SEED}
mkdir -p $OUTPUT_DIR/data-bin-xbert

python -m xbert.preprocess \
	-m xbert \
	-i datasets/${DATASET} \
	-c ${OUTPUT_DIR}/indexer/code.npz \
	-o ${OUTPUT_DIR}/data-bin-xbert \
	--bert_model ${BERT_MODEL}
#	--bert_model bert-base-uncased

# neural matcher
echo '>>>> MATCHER TRAINING <<<<'
OUTPUT_DIR=save_models/${DATASET}/pifa-a${ALGO}-s${SEED}
mkdir -p ${OUTPUT_DIR}/matcher/xbert
#CUDA_VISIBLE_DEVICES=${GPUS} nohup python -m torch.distributed.launch -m --nproc_per_node 2 -m xbert.matcher.bert \

CUDA_VISIBLE_DEVICES=${GPUS} nohup python -u -m xbert.matcher.bert \
	-i ${OUTPUT_DIR}/data-bin-xbert/data_dict.pt \
	-o ${OUTPUT_DIR}/matcher/xbert \
	--bert_model ${BERT_MODEL} \
	--do_train --do_eval --stop_by_dev \
	--learning_rate ${LEARNING_RATE} \
	--warmup_proportion ${WARMUP_RATE} \
	--train_batch_size ${TRAIN_BATCH_SIZE} \
	--eval_batch_size ${EVAL_BATCH_SIZE} \
	--num_train_epochs ${NUM_TRAIN_EPOCHS} \
	--log_interval ${LOG_INTERVAL} \
	--eval_interval ${EVAL_INTERVAL} \
	> ${DATASET}_xbert_a${ALGO}-s${SEED}_log

echo '>>>> RANKER TRAINING <<<<'
OUTPUT_DIR=save_models/${DATASET}/pifa-a${ALGO}-s${SEED}
mkdir -p $OUTPUT_DIR/ranker
taskset -c ${CPUS} python -m xbert.ranker train \
	-x datasets/${DATASET}/X.trn.npz \
	-y datasets/${DATASET}/Y.trn.npz \
	-c ${OUTPUT_DIR}/indexer/code.npz \
	-o ${OUTPUT_DIR}/ranker

echo '>>>> RANKER PREDICTION <<<<'
taskset -c ${CPUS} python -m xbert.ranker predict \
	-m ${OUTPUT_DIR}/ranker \
	-x datasets/${DATASET}/X.tst.npz \
	-y datasets/${DATASET}/Y.tst.npz \
	-c ${OUTPUT_DIR}/matcher/xbert/C_eval_pred.npz \
	-o ${OUTPUT_DIR}/ranker/tst.prediction.npz

echo '>>>> END <<<<'