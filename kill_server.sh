#!/bin/bash

res=$1
for((i=0;i<res;i++))
do
#   echo "Welcome $((5000+$i)) times"
   stuff=$(lsof -i:$((5000+$i))|grep Python)
   IFS=' ' read -ra port <<< "$stuff"
#   echo ${port[1]}
   if [ "${port[1]}" != "" ]; then
    kill ${port[1]}
   fi
#   stuff=$(lsof -i:$((5000+$i))|grep Python)
#   IFS=' ' read -ra port <<< "$stuff"
#   echo ${port[1]}
done
