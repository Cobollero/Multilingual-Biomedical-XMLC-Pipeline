#!/bin/bash
fileid="1m9Hr5KO2J5HKxcRbLA29ZH6CGSYOnL4D"
filename="bioasq_data.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

rm cookie

unzip ${filename}

rm ${filename}
