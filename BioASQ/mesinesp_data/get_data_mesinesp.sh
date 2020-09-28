#!/bin/bash
fileid="1-zJqxy12nlBmFqUPKA1o_aKlY67BN2Mc"
filename="mesinesp_data.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

rm cookie