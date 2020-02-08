#!/usr/bin/env sh



####### given data
M="$1/given_data/M.txt"
T="$1/given_data/T.txt"
T25="$1/given_data/T25.txt"
T50="$1/given_data/T50.txt"
T75="$1/given_data/T75.txt"
T100="$1/given_data/T100.txt"



####### anonymized data
AT="$2/AT_file/AT_$3.txt"




####### utility
for utility in E1-ItemCF-s.py E2-ItemCF-r.py E3-topk.py E4-diff-date.py E5-diff-price.py E6-nrow.py
do
  ruby "$1/tool/tool-ncat.rb" $M $T $AT | python3 "$1/utility/"$utility
done



####### security
### python
for security_py in S1-datenum.py S2-itemprice_sub.py S3-itemnum_sub.py S4-itemdate_sub.py
do
  echo $security_py
  for ratio in 25 50 75 100
  do
    ruby "$1/tool/tool-ncat.rb" $M "$2/S_file/S_$4.txt" "$1/given_data/T"$ratio".txt" | python3 "$1/reidentify/"$security_py > "$2/Fh"$ratio"_$4.txt"
    python3 "$1/tool/tool-compare_and.py" "$2/F_file/F_$4.txt" "$2/Fh"$ratio"_$4.txt"
    rm -f "$2/"*"_$4.txt" "$2/"*"_$4.csv"
  done
done

### ruby
for security_rb in S5-item2pricenum.rb S6-item2datenum.rb
do
  echo $security_rb
  for ratio in 25 50 75 100
  do
    ruby "$1/tool/tool-ncat.rb" $M "$2/S_file/S_$4.txt" "$1/given_data/T"$ratio".txt"  | ruby "$1/reidentify/"$security_rb > "$2/Fh"$ratio"_$4.txt"
    python3 "$1/tool/tool-compare_and.py" "$2/F_file/F_$4.txt" "$2/Fh"$ratio"_$4.txt"
    rm -f "$2/"*"_$4.txt" "$2/"*"_$4.csv"
  done
done
