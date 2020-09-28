#!/bin/bash
fileid="1lsmPOL6AsK56wRs7uOQ3HVuLG9nd1UmT"
filename="scibert_scivocab_uncased.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

rm cookie

unzip ${filename}

rm ${filename}
