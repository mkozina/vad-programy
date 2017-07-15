#!/bin/bash

# parametry:
# 1. folder z mowa i wyrownaniami
# 2. rozszerzenie plikow z mowa
# 3. folder z szumem
# 4. rozszerzenie plikow z szumem
# 5. ile wygenerowac plikow
# 6. odstepy - x albo rbeta|rgamma|rnorm|runif x y 
# 7. SNR dB

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

if [[ ! ($# -eq 7 || $# -eq 9) ]]; then
	exit 1
fi

rm -f log.txt
touch log.txt
chmod 766 log.txt

speech=$(find ./$1 -maxdepth 1 -type f -iname '*.'"$2" -exec basename {} \;)
noise=$(find ./$3 -maxdepth 1 -type f -iname '*.'"$4" -exec basename {} \;)
nooffiles=$5
digits=${#nooffiles}

# podzial plikow z mowa na fragmenty z wyrownaniami, przy odstepie pomiedzy mowa co najmniej 0.5s
mkdir $1/proc
for f in $speech
do
	no=$((0))
	column1=$((0))
	flines=$(wc -l < $1/"${f%.*}".txt)
	currentline=$((1))
	line=$(sed -n $currentline'p' $1/"${f%.*}".txt)
	while [ $currentline -le $flines ]; do
		touch $1/proc/$f-$no.txt
		chmod 766 $1/proc/$f-$no.txt
		start=$(echo $line | cut -f1)
		startline=$currentline
		while true; do
			column2=$(echo $line | cut -f2)
			endline=$currentline
			procf1=$(echo $line | cut -f1)
			procf2=$(echo $line | cut -f2)
			procf3=$(echo $line | cut -f3)
			procf1=$(echo "$procf1 $start" | awk '{printf "%.2f", $1 - $2}')
			procf2=$(echo "$procf2 $start" | awk '{printf "%.2f", $1 - $2}')
			echo -e "$procf1\t$procf2\t$procf3" >> $1/proc/$f-$no.txt
			currentline=$((currentline+1))
			line=$(sed -n $currentline'p' $1/"${f%.*}".txt)
			if [ $currentline -le $flines ]; then
				column1=$(echo $line | cut -f1)
			fi
			if [[ $currentline -gt $flines || $(echo "$column1-$column2>=0.5" | bc -l) == 1 ]]; then
				sox $1/$f $1/proc/$f-$no.$2 trim $start =$column2
				no=$((no+1))
				break
			fi
		done
	done
done
procspeech=$(find ./$1/proc -maxdepth 1 -type f -iname '*.'"$2" -exec basename {} \;)

re="[0-9]+"
if [[ $6 =~ $re ]]; then
	opt="fixed"
	silence=$6
	snr=$7
elif [ ${6:0:1} == "r" ]; then
	opt="random"
	dist=$6
	param1dist=$7
	param2dist=$8
	snr=$9
fi

# 10*log(Psignal/Pnoise) = SNRdB		/ /10
# log(Psignal/Pnoise) = SNRdB/10
snr=$(echo "$snr" | awk '{printf "%.2f", $1 / 10}')
# Psignal/Pnoise = 10^(SNRdB/10)
snr=$(echo "$snr" | awk '{printf "%.6f", 10^$1}')

# glowna petla, generuje plik z wyrownaniem
for ((file=1;file<=nooffiles;file++))
do

	output=()
	speecharr=($procspeech)
	# losowy wybor liczby plikow z mowa, ktore maja byc uzyte do wygenerowania pliku
	usespeech=$(( ( RANDOM % ${#speecharr[@]} )  + 1 ))

	# generowanie przerw w mowie zgodnie z wybranym rozkladem
	if [ "$opt" == "random" ]; then
		silencedist=$(python3.5 rdist.py $(($usespeech-1)) $dist $param1dist $param2dist)
		silencedistarr=()
		while read -r line; do
			silencedistarr+=("$line")
		done  <<< "$silencedist"
	fi

	digitsact=${#file}
	zeros=$((digits-digitsact))
	pre=$(head -c $zeros < /dev/zero | tr '\0' '0')
	suf=$pre$file

	rm -f ./audio$suf.txt
	touch audio$suf.txt
	chmod 766 ./audio$suf.txt

	echo "--------------------------------------------------" >> log.txt
	echo "#audio$suf.wav" >> log.txt
	echo "--------------------------------------------------" >> log.txt
	echo "##speech" >> log.txt
	echo "--------------------------------------------------" >> log.txt

	# generowanie kolejnosci mowy i przerw oraz pliku z wyrownaniami
	skip=$((0))
	start=$((0))
	position=$((0))
	for ((s=1;s<=usespeech;s++))
	do

		# losowy wybor pliku z mowa
		randomf=$(( RANDOM % ${#speecharr[@]} ))
		f=${speecharr[$randomf]}
		output+=("$1/proc/$f-temp.wav")
		unset speecharr[$randomf]
		speecharr=( "${speecharr[@]}" )
		echo "$f" >> log.txt
		filename="${f%.*}"

		# dopasowanie volume na podstawie wartosci bezwglednej max i min amplitudy oraz SNR
		minamp=$(sox $1/proc/$f -n stat 2>&1 | grep 'Maximum amplitude' | cut -d':' -f2 | xargs)
		minamp=$(echo "$minamp" | awk '{printf "%.6f", sqrt($1^2)}')
		maxamp=$(sox $1/proc/$f -n stat 2>&1 | grep 'Minimum amplitude' | cut -d':' -f2 | xargs)
		maxamp=$(echo "$maxamp" | awk '{printf "%.6f", sqrt($1^2)}')
		if [ $(echo "$maxamp>$minamp" | bc -l) == 1 ]; then
			volamp=$maxamp
		else
			volamp=$minamp
		fi
		if [ $(echo "$snr<1.0" | bc -l) == 1 ]; then
			adjv=$snr
		else
			adjv=$(echo "1.0" | awk '{printf "%.2f", $1}')
		fi
		vol=$(echo "$volamp $adjv" | awk '{printf "%.2f", 0.3*($2 / $1)}')
		sox -v $vol $1/proc/$f $1/proc/$f-tempv.wav

		sox $1/proc/$f-tempv.wav $1/proc/$f-temp.wav highpass 10

		stop=$(sox $1/proc/$f-temp.wav -n stat 2>&1 | grep 'Length' | cut -d':' -f2 | xargs | awk '{printf "%.2f", $1}')
		stop=$(echo "$position $stop" | awk '{printf "%.2f", $1 + $2}')

		while IFS= read -r line; do
			procf1=$(echo $line | cut -f1)
			procf2=$(echo $line | cut -f2)
			procf3=$(echo $line | cut -f3)
			procf1=$(echo "$procf1 $start" | awk '{printf "%.2f", $1 + $2}')
			procf2=$(echo "$procf2 $start" | awk '{printf "%.2f", $1 + $2}')
			echo -e "$procf1\t$procf2\t$procf3" >> audio$suf.txt
		done < $1/proc/"${f%.*}".txt

		# wygenerowanie przerwy w mowie
		if [ $s -lt $usespeech ]; then
			if [ "$opt" == "fixed" ]; then
				echo "$silence" >> log.txt
				sox -n -r 16k -e signed-integer -b 16 -c 1 $1/proc/$f-temps.wav trim 0.0 $silence
				output+=("$1/proc/$f-temps.wav")
			else
				echo "${silencedistarr[skip]}" >> log.txt
				sox -n -r 16k -e signed-integer -b 16 -c 1 $1/proc/$f-temps.wav trim 0.0 ${silencedistarr[skip]}
				output+=("$1/proc/$f-temps.wav")
			fi
		fi

		rm $1/proc/$f-tempv.wav
		skip=$((skip+1))
		start=$(sox $1/proc/$f-temp.wav -n stat 2>&1 | grep 'Length' | cut -d':' -f2 | xargs | awk '{printf "%.2f", $1}')
		starts=$(sox $1/proc/$f-temps.wav -n stat 2>&1 | grep 'Length' | cut -d':' -f2 | xargs | awk '{printf "%.2f", $1}')
		start=$(echo "$position $start $starts" | awk '{printf "%.2f", $1 + $2 + $3}')
		position=$(echo "$start" | awk '{printf "%.2f", $1}')
	done

	echo "--------------------------------------------------" >> log.txt
	echo "##noise" >> log.txt
	echo "--------------------------------------------------" >> log.txt

	noisearr=($noise)
	# losowy wybor pliku z szumem
	randomf=$(( RANDOM % ${#noisearr[@]} ))
	f=${noisearr[$randomf]}
	echo "$f" >> log.txt
	filename="${f%.*}"

	# dopasowanie volume na podstawie wartosci bezwglednej max lub min amplitudy oraz SNR
	minamp=$(sox $3/$f -n stat 2>&1 | grep 'Maximum amplitude' | cut -d':' -f2 | xargs)
	minamp=$(echo "$minamp" | awk '{printf "%.6f", sqrt($1^2)}')
	maxamp=$(sox $3/$f -n stat 2>&1 | grep 'Minimum amplitude' | cut -d':' -f2 | xargs)
	maxamp=$(echo "$maxamp" | awk '{printf "%.6f", sqrt($1^2)}')
	if [ $(echo "$maxamp>$minamp" | bc -l) == 1 ]; then
		volamp=$maxamp
	else
		volamp=$minamp
	fi
	if [ $(echo "$snr<1.0" | bc -l) == 1 ]; then
		adjv=$(echo "1.0" | awk '{printf "%.2f", $1}')
	else
		adjv=$(echo "$snr" | awk '{printf "%.2f", 1 / $1}')
	fi
	vol=$(echo "$volamp $adjv" | awk '{printf "%.2f", 0.3*($2 / $1)}')
	sox -v $vol $3/$f $3/$f-tempv.wav

	sox $3/$f-tempv.wav $3/$f-temp.wav highpass 10

	rmsnoise=$(sox $3/$f-temp.wav -n stat 2>&1 | grep 'RMS     amplitude' | cut -d':' -f2 | xargs)
	# Pnoise = Anoise^2
	pnoise=$(echo "$rmsnoise" | awk '{printf "%.6f", $1^2}')
	# Asignal = sqrt(SNR*Pnoise)
	rmssignal=$(echo "$snr $pnoise" | awk '{printf "%.6f", sqrt($1*$2)}')

	# dopasowanie dlugosci szumu do pliku z mowa
	r=$((-1))
	positionn=$((0))
	while [ $(echo "$positionn>$position" | bc -l) == 0 ]; do
		stopn=$(sox $3/$f-temp.wav -n stat 2>&1 | grep 'Length' | cut -d':' -f2 | xargs | awk '{printf "%.2f", $1}')
		positionn=$(echo "$positionn+$stopn" | bc)
		r=$((r+1))
	done
	# generowanie pliku z szumem
	sox $3/$f-temp.wav noise.wav repeat $r

	# generowanie pliku z mowa i przerwami
	for i in "${output[@]}"
	do
		ext="${i#*.}"
		if [ "${ext: -5:5}" != "s.wav" ]; then
			#  
			rmsact=$(sox $i -n stat 2>&1 | grep 'RMS     amplitude' | cut -d':' -f2 | xargs)
			wsp=$(echo $rmssignal $rmsact | awk '{printf "%.2f", $1 / $2}')
			sox -v $wsp $i $i.wav
			rm $i
			mv $i.wav $i
		fi
	done
	sox ${output[@]} speech.wav

	# plik z mowa i szumem o wybranym SNRdB
	sox -m speech.wav noise.wav -r 16k -e signed-integer -b 16 -c 1 audio$suf.wav

	echo "--------------------------------------------------" >> log.txt
	echo -e "" >> log.txt

	rm ./$1/proc/*-temp.wav
	rm -f ./$1/proc/*-temps.wav
	rm ./$3/*-temp.wav
	rm ./$3/*-tempv.wav
	rm ./noise.wav ./speech.wav

done

rm -rf $1/proc

IFS=$SAVEIFS

exit 0
