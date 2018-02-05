#!bin/bash
## v1.0
##
## This script finds all file extensions in the current dir and all subdirs
## and lists them by extension. Also gives a count list of those extensions
## First cd is for Synology NAS dir only.
## Script created and owned by Richard Rudolph
##
cd /home/ueda/workspace/PSE/code

listfiles() {

printf "##########################\n" > /home/ueda/workspace/PSE/scripts/files.txt
printf "### All files sorted   ###\n" >> /home/ueda/workspace/PSE/scripts/files.txt
printf "### by extension in    ###\n" >> /home/ueda/workspace/PSE/scripts/files.txt
printf "### alphabetical order ###\n" >> /home/ueda/workspace/PSE/scripts/files.txt
printf "##########################\n" >> /home/ueda/workspace/PSE/scripts/files.txt
printf "\n" >> /home/ueda/workspace/PSE/scripts/files.txt

printf "Total file count: $totalcount\n\n" >> /home/ueda/workspace/PSE/scripts/files.txt

extensions=(`find . -type f -name "*.*" | sed "s|.*\.||" | sort -u`)

printf "There are ${#extensions[@]} extensions\n\n" >> /home/ueda/workspace/PSE/scripts/files.txt

for i in "${extensions[@]}"
do
	lines=`find . -type f -name "*.$i" | xargs wc -l | grep 'total' | awk '{ SUM += $1; print $1}'`
	count=`find . -type f -name "*.$i" | wc -l`
	printf "%10s %15s %10s\n" $count $i $lines  >> /home/ueda/workspace/PSE/scripts/files.txt;
done

printf "\n" >> /home/ueda/workspace/PSE/scripts/files.txt

for i in "${extensions[@]}"
do
	printf "### $i files ###\n" >> /home/ueda/workspace/PSE/scripts/files.txt
	printf "\n" >> /home/ueda/workspace/PSE/scripts/files.txt
	find . -type f -name "*.$i" >> /home/ueda/workspace/PSE/scripts/files.txt
	printf "\n" >> /home/ueda/workspace/PSE/scripts/files.txt
done
}



## Control if file number has changed. If not, no rewrite of file necessary
totalcount=`find . -type f | wc -l`
lastcount=`sed -n '7{s/Total file count: // ; p}' '/home/ueda/workspace/PSE/scripts/files.txt'`

if [ $totalcount != $lastcount ]
	then
		listfiles
fi	
	
