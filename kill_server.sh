#!/bin/bash

res=$1
for (( i=0; i< $1 ; i++ ))
do
   stuff=$( lsof -i:$((5000+$i))|grep Python )
   # echo $stuff
   IFS=' ' read -ra port <<< "$stuff"
   if [ "${port[1]}" != "" ]; then
    kill ${port[1]}
   fi
   stuff=$( lsof -i:$((5000+$i))|grep python )
   # echo $stuff
   IFS=' ' read -ra port <<< "$stuff"
   if [ "${port[1]}" != "" ]; then
    kill ${port[1]}
   fi
done
