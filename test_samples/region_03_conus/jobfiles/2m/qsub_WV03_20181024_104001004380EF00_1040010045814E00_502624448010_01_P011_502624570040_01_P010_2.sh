#!/bin/bash

SRC=${0%.sh}

OUT="$SRC.out"

rm -f $OUT
echo "===================================" >> $OUT
echo "Running on $(hostname -f)" >> $OUT
uname -a >> $OUT
echo "===================================" >> $OUT
env >> $OUT
echo "===================================" >> $OUT


