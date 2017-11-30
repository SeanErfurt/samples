README written by Sean Erfurt.
August, 2015.

Notes for Implementation of Garrett Nicolai, Colin Cherry, and Grzegorz Kondrak: Inflection Generation as Discriminative String Transduction. NAACL HLT 2015.
View paper at: https://webdocs.cs.ualberta.ca/~nicolai/publications/inflection.pdf

For demonstration purposes, download the zip files under demo_data and
unzip them. They will be used as the wiktionary data referenced below.

The following installation instructions are for Linux and assume Python 2.7 is already installed.
Installation:
    If you haven't already, install virtualenv:
        Download
        $ curl -s https://pypi.python.org/packages/source/v/virtualenv/virtualenv-13.0.3.tar.gz | tar zx
        Navigate to directory
        $ cd virtualenv-13.0.3
        Run
        $ python virtualenv.py ~/

    Now you can add pandas to the virtual environment:
        Start up environment
        $ . ~/bin/activate
        Use pip as normal to install pandas and dependencies.
        $ pip install pandas

    SVMlight:
        Get SVMlight source at http://download.joachims.org/svm_light/current/svm_light.tar.gz

        $ curl -s http://download.joachims.org/svm_light/current/svm_light.tar.gz | tar xz
        $ cd svm_light
        $ make all

        NOTES:
            If you get a connection-refused error, copy over from repo via scp.
            Running make doesn't seem to be necessary, but doesn't hurt.

    STLport:
        $ git clone git://git.code.sf.net/p/stlport/code stlport-code
        $ cd stlport-code
        $ git checkout -b STLport-5.2 origin/STLport-5.2
        $ ./configure --prefix=/[YOURPATH]/STLport --enable-static --disable-shared
        $ make && (cd build/test/unit && make)
        $ sudo make install

        NOTE: [YOURPATH] must begin from root and not use '~'

    m2m-aligner:
        copy over repo version, and in the 'm2m' directory, run:
        $ make

        NOTE: can use STLport to be faster, didnt work for me.
            Try editing the makefile where indicated to point
            to /[YOURPATH]/STLport from step above.

    DirecTL+:
        Copy over repo version, and in the 'DTL' directory:
        Point makefile to your svm_light directory and the parent of
        'include/stlport' (usually '/[YOURPATH]/STLport'), then run:
        $ make

    Multicore Liblinear:
        download from http://ntucsu.csie.ntu.edu.tw/~cjlin/libsvmtools/multicore-liblinear/
        In the unzipped directory, run:
        $ make

        NOTE: You need the multicore version to parallelize.

Using the bash script:

    1. After making/installing the above programs, move the
    executables into the same parent directory.
    Also copy Nicolai-pipeline.sh, wiktToNicolai.py, Reranker.jar,
    and llnrpredictr.py from the repo into this directory.

    2. Move your wiktionary data (contained in a subdirectory) into the
    directory with the scripts and executables. Modify Nicolai-pipeline.sh
    to point to the data directory, following the instructions indicated
    by '##'.

    3. Run the script using the command:
        $ bash Nicolai-pipeline.sh &> stderr.txt

        OR
        If running on the grid, you can use the parallelized version with:
        $ qsub -l 'arch=*64*' -l mem_free=50G,ram_free=50G -pe smp [#] -V -cwd -j y -o /[YOURPATH]/err-pll.txt Nicolai-pipeline.sh

        Make sure you modify the parallel script as described above,
        and run the command with your memory needs and directory path.
        Also, specify the number of cores in the above command where
        there is [#], and put that same number in the script where indicated.

        NOTES:
            '&> stderr.txt' is optional, but useful if the pipeline
                script is interrupted for any reason.
            Make sure you don't have any subdirectories named 'en_fin_N' or
                'output' in your working directory, as their contents may be
                overwritten.
            Also make sure that all files have 0755 permissions. You
                can run 'chmod -R 0755 .' from the working directory.
            If you see a 'Segmentation fault' in the log or DTL is
                taking particularly long, you can increase the memory
                request.
            You can specify the host computer with '-l hostname=[ID]'
                to speed up I/O, but if the computer is busy, overall
                speed may be slower.

Manual Data pipeline (in case bash script needs debugging):

    0. move the executables into the same parent directory.
    Also copy Nicolai-pipeline.sh, wiktToNicolai.py, Reranker.jar,
    and llnrpredictr.py from the repo into this directory. Lastly,
    move your wiktionary data (contained in a subdirectory) into this
    same directory.

    wiktToNicolai
    1. Generate training, testing, and tagfiles from wiktionary data.
        With [INPUTPATH] as subdirectory with data, run:
        $ python wiktToNicolai.py [INPUTPATH]/ [OUTPUTPATH]/ [mode]

        where [mode] should be 'True' or 'max' if you want to use the
            maximal paradigm to generate the train-test files,
            'False', '', or 'default' if you want to use all lemmas
            available, and 'inc' if you want to use default behavior
            as well as generate unseen paradigm slots.

    m2m-aligner
    2. Align data with following command, using a training file from
        the previous step as [INPUTFILE]:
        $ ./m2m-aligner --maxX 2 --maxY 2 --maxTag 4 --maxFn joint \
        --copy --delX -i [INPUTFILE] -o [LANG_POS].align

        NOTES:
            -o is optional, names the output file.
            --pScore prints alignment scores in outfile.
            If you get a Segmentation fault at this step, the train
                file was probably too large. Use the *train_500.txt
                file, or increase memory resources.

        Output normally is in:
            [INPUTFILE].m-mAlign.2-2-4.delX.copy.1-best.joint.align
        and of form:
            g|e|b|e:n|+:1SIE*|    g|e|b|_|e

    directlpCopy
    3a. Run DirecTL+ on the aligned data (output of previous step).
        $ ./directlpCopy --order 1 --linearChain --cs 9 --ng 19 \
        --jointMgram 5 --copy  --inChar : -f [ALIGNEDFILE] --mo [LANG_POS].model

        Need file named after --mo for testing step below.
        Normally in:
            [LANG_POS].txt.m-mAlign.2-2-4.delX.copy.1-best.joint.align.10nBest.1order.linearChain.[#]

            where [#] is the second-largest number

        NOTES:
            program will hang and ask for test input from stdin.
            --mo is optional, changes the model file's name.
            make sure to use the second-to-last model.
            If the program terminates with error code: "terminate
            called after throwing an instance of 'std::bad_alloc'",
            increase your memory resources.

    3b. with [LANG_POS]_test.txt generated from step 1 as [TESTFILE]:
        $ ./directlpCopy --order 1 --linearChain --cs 9 --ng 19 \
        --jointMgram 5 --copy  --inChar '|' --outChar ' ' \
        -t [TESTFILE] --nBestTest 10 -a [LANG_POS] --mi [MODEL]

        output is in [LANG_POS] and [LANG_POS].phraseOut

    Reranker
    4. Use ExtractParadigms on the output of DTL to generate
        your 1-best inflection tables.
        $ java -jar Reranker.jar extract predictionFile paradigmFile tagFile

        extract is literally 'extract', signals function,
        predictionFile is [LANG_POS].phraseOut from previous step,
        paradigmFile is the output,
        tagFile is [LANG_POS]_tags.txt generated in step 1.

    5. Now, generate the files for liblinear using
        constructSVMFileShortTwoModels.
        $ java -jar Reranker.jar construct predictionFile \
        paradigmFile tagFile goldFile nBest test outFile

        construct is literally 'construct', signals function,
        predictionFile is [LANG_POS].phraseOut from step 3b,
        paradigmFile is the file generated in step 4,
        tagFile is [LANG_POS]_tags.txt generated in step 1.
        goldFile is [LANG_POS]_gold.txt from step 1,
        nBest is the size of the nBest list,
        test is false for training, true for testing,
        outFile is the file for liblinear

        NOTE: run once in test mode and once in train mode.

    6. Learn model with LIBLINEAR:
        $ ./train (-s 0) (-n 4) [output of step 5 with test=false]

            -s specifies the type of solver, 2 is default
            -n specifies the number of cores to use in parallel

        NOTE: If you get the error "Wrong input format at line _", it
            means the input file has a zero feature vector
            (ex: +1 0:0.0). In this case the predictions cannot be reranked.

    7. Use llnrpredictr.py to rerank:

        $ ./llnrpredictr.py testFile model > rerankedTestFile

        Where:
            testfile is output of step 5 with test=true and
            model is the output of step 6