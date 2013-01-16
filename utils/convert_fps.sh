#!/bin/bash

TMPFILE=`mktemp`
ffmpeg -i $1 -f rawvideo -b:v 50000000 -pix_fmt yuv420p -vcodec rawvideo -s 1920x1080 -y $TMPFILE
ffmpeg -f rawvideo -b:v 50000000 -pix_fmt yuv420p -r $2 -s 1920x1080 -i $TMPFILE -vcodec mjpeg -y $1.output.$2.avi
rm $TMPFILE