#!/usr/bin/env sh



####### given data
M="$1/given_data/M.txt"
T="$1/given_data/T.txt"



####### anonymized data
AT="$2/AT_file/AT_$3.txt"



####### make template file
cat $AT | python3 "$1/tool/tool-createPBdata.py" "$2/S_file/S_$4.txt"



####### make F(answer)
python3 "$1/tool/tool-kameimap.py" $M $T $AT "$2/F_file/F_$4.txt"