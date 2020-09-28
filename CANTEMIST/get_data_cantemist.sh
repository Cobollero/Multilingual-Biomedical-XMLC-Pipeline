#!/bin/bash
fileid="1GpVP8TLiJ5cFMtnPAUsu_sdNjwvilgPk"
filename="cantemist_data.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

rm cookie

unzip ${filename}

rm ${filename}
