#!/bin/bash

rm -rf result/raw/*
rm -rf result/xml/*
touch result/raw/names.txt
touch result/raw/misc.txt

cat $1 | tomita-parser proto/config_raw.proto
python3 name.py
cat $1 | tomita-parser proto/config_strict_xml.proto
#cat $1 | tomita-parser config_strict_txt.proto

python3 clusterize.py result/xml/strict_out.xml

rm extractions/*.bin
rm proto/*.bin