#!/bin/bash
#Creates the MER lexicons for usage in the BioASQ competitions.
#Vocabularies:
# - meshlex: mesh terms and their synonyms
# - decslex: decs terms and their synonyms
# - decsparlex: decs terms, their synonyms and direct ancestors
#
#HOW TO RUN:
# ./gen_mer_lexs.sh

echo 'Generating meshlex...'
python mer_gen_mesh_lex.py

echo 'Generating decslex...'
python mer_gen_decs_lex.py

echo 'Generating decsparlex...'
python mer_gen_decs_parlex.py
