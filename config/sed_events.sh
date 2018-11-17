#!/bin/bash
:<<doc
sed events
doc

for s in sub*
do
for f in ${s}/func/*.tsv
do
sed -e "s/Onset/onset/g" -e "s/Duration/duration/g" -e "s/Intensity/intensity/g" -i ${f}
done
done
