# download protoroles and untar
if [ ! -e protoroles_eng_udewt.tar.gz ]; then
    mkdir protoroles
    curl -O http://decomp.io/projects/semantic-proto-roles/protoroles_eng_udewt.tar.gz
    gunzip -c protoroles_eng_udewt.tar.gz | tar -C protoroles xopf -
fi

# download factuality and untar
if [ ! -e factuality_eng_udewt.tar.gz ]; then
    mkdir factuality
    curl -O http://decomp.io/projects/factuality/factuality_eng_udewt.tar.gz
    gunzip -c factuality_eng_udewt.tar.gz | tar -C factuality xopf -
fi

# download wordsense and untar
if [ ! -e wordsense_eng_udewt.tar.gz ]; then
    mkdir wordsense
    curl -O http://decomp.io/projects/word-sense/wordsense_eng_udewt.tar.gz
    gunzip -c wordsense_eng_udewt.tar.gz | tar -C wordsense xopf -
fi

# download genericity and unzip
if [ ! -e genericity_eng_udewt_v1.zip ]; then
    mkdir genericity
    curl -O http://decomp.io/projects/genericity/genericity_eng_udewt_v1.zip
    unzip -a genericity_eng_udewt_v1.zip -d genericity
fi

# download time and unzip
if [ ! -e UDS_T_v1.0.zip ]; then
    curl -O http://decomp.io/projects/time/UDS_T_v1.0.zip
    unzip -a UDS_T_v1.0.zip
    mv UDS_T_v1.0 time
fi
