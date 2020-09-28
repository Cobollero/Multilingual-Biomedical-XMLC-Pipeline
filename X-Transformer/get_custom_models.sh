#!/bin/bash
fileid="1Ur0N6mDG5LZIvg4TLBjEHa-j8tmnsOCP"
filename="custom_models.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

rm cookie

unzip ${filename}

rm ${filename}
