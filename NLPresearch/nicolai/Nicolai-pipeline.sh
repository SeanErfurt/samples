#!/bin/bash
## change 'demo_data/' below to point to your wiktionary data directory. 	##
data=demo_data/

## =max or True to use maximal paradigm only, 							##
#  =default or False to use all lemmas
#  =inc (incomplete) to use all lemmas and find missing paradigm slots
mode=default

## change to the number of cores if running in parallel.				##
cores=1

#start local python environment
. ~/bin/activate

#set encoding to utf-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

#set permissions
perm=$(umask)
umask -p 0022

#create intermediate directory to hold alignable data
mkdir -p en_fin_N
#create output directory
mkdir -p output

## dont run this if all the files have been generated already 	  		##
python wiktToNicolai.py "$data" en_fin_N/ "$mode"

#run Nicolai for each lang,pos pair in en_fin_N/
for File in $(ls en_fin_N/); do
	#find largest train file for each language_pos
	if [[ "$File" == *train.txt ]]; then
		#split filename up using '_'
		str=(${File//_/ })
		#get length of language name in words
		len=$[ ${#str[@]} - 2 ]
		#extract language name
		lang=${str[@]:0:$len}
		lang=${lang[@]// /_}
		#extract part of speech
		pos=${str[@]:$len:1}
		pos=${pos[0]}
		#set up output directory
		mkdir -p output/"${lang}"

		#create aligned filename
		align="${lang}"_"${pos}".align
		#run aligner
		./m2m-aligner --maxX 2 --maxY 2 --maxTag 4 --maxFn joint \
		--copy --delX -i en_fin_N/"$File" -o output/"$lang"/"$align" || \
		./m2m-aligner --maxX 2 --maxY 2 --maxTag 4 --maxFn joint \
		--copy --delX -i en_fin_N/"${lang}"_"${pos}"_train_500.txt -o output/"$lang"/"$align"

		#create model filename
		model="${lang}"_"${pos}".model
		#train transducer
		printf "\n" | ./directlpCopy --order 1 --linearChain --cs 9 --ng 19 --jointMgram 5 \
		--copy  --inChar ':' -f output/"$lang"/${align} --mo output/"$lang"/${model}

		#find second-to-last model file
		mFile=$(find output/"$lang" -regex "output/"$lang"/"${model}".[0-9]+$" | \
			sort -t '.' -k 3,3n | tail -2 | head -1)

		#make testfile name
		test=en_fin_N/"${lang}"_"${pos}"_test.txt
		#make output basename
		out=output/"$lang"/"${lang}"_"${pos}"

		#test with model
		./directlpCopy --order 1 --linearChain --cs 9 --ng 19 --jointMgram 5 --copy \
		--inChar '|' --outChar ' ' -t "${test}" --nBestTest 10 -a "${out}" --mi "${mFile}"

		#make reranking filenames
		phrases="${out}".phraseOut
		paradigms="${out}"_paradigms.txt
		gold=en_fin_N/"${lang}"_"${pos}"_gold.txt
		tags=en_fin_N/"${lang}"_"${pos}"_tags.txt

		#java reranking
		java -jar Reranker.jar extract "${phrases}" "${paradigms}" "${tags}"
		java -jar Reranker.jar construct "${phrases}" "${paradigms}" "${tags}" \
		"${gold}" 10 False "${out}"_LLtrain.txt
		java -jar Reranker.jar construct "${phrases}" "${paradigms}" "${tags}" \
		"${gold}" 10 True "${out}"_LLtest.txt

		#liblinear reranking
		cp -p train llnrpredictr.py output/"$lang"/
		cd output/"$lang"/
		if [[ "$cores" < 2 ]]; then
			./train "${lang}"_"${pos}"_LLtrain.txt && \
			./llnrpredictr.py "${lang}"_"${pos}"_LLtest.txt "${lang}"_"${pos}"_LLtrain.txt.model > \
			"${lang}"_"${pos}"_reranked.txt
		else
			./train -n "$cores" "${lang}"_"${pos}"_LLtrain.txt && \
			./llnrpredictr.py "${lang}"_"${pos}"_LLtest.txt "${lang}"_"${pos}"_LLtrain.txt.model > \
			"${lang}"_"${pos}"_reranked.txt
		fi
		rm train llnrpredictr.py
		cd -
	fi
done

#reset umask
umask -p "$perm"

#archive output
gunzip -q output.tar.gz
tar -uvf output.tar output/ || tar -cvf output.tar output/
gzip output.tar

exit