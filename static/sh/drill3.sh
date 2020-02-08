#!/usr/bin/env sh

Fh25_user="$2/Fh_file/Fh25_$4.txt"
Fh50_user="$2/Fh_file/Fh50_$4.txt"
Fh75_user="$2/Fh_file/Fh75_$4.txt"
Fh100_user="$2/Fh_file/Fh100_$4.txt"

####### reidentify by user
echo "reidentification by user"
python3 "$1/tool/tool-compare_and.py" "$3/F_file/F_$4.txt" $Fh25_user
python3 "$1/tool/tool-compare_and.py" "$3/F_file/F_$4.txt" $Fh50_user
python3 "$1/tool/tool-compare_and.py" "$3/F_file/F_$4.txt" $Fh75_user
python3 "$1/tool/tool-compare_and.py" "$3/F_file/F_$4.txt" $Fh100_user