#!/bin/bash

rm extractions/*.bin
rm proto/*.bin
rm -rf result/raw/*
rm -rf result/xml/*
touch result/raw/names.txt
touch result/raw/misc.txt

cat $1 | tomita-parser proto/config_raw.proto
python3 src/name.py
cat $1 | tomita-parser proto/config_strict_xml.proto

python3 src/clusterize.py result/xml/strict_out.xml
