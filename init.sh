#!/usr/bin/bash

BASH_PATH=$(readlink -f $0)
ROOT_PATH=`dirname $BASH_PATH`

VENV_EXE="#!$ROOT_PATH/env/bin/python3

"
ECHO_VENV=$(echo $VENV_EXE | sed -e 's/\r//g')
: '
echo "Adding $ECHO_VENV line on aws_uploads.py script."
echo "$VENV_EXE" | cat - aws_uploads.py > temp && mv temp aws_uploads.py

echo "Adding $ECHO_VENV line on aws_utils.py script."
echo "$VENV_EXE" | cat - aws_utils.py > temp && mv temp aws_utils.py

echo "Adding $ECHO_VENV line on dwn_sb_logs.py script."
echo "$VENV_EXE" | cat - dwn_logs.py > temp && mv temp dwn_logs.py

echo "Making those 2 scripts executable."
'

for MAIN_FILE in {aws_upload,dwn}.py
do
    echo "Adding $ECHO_VENV line on $MAIN_FILE script."
    #sed -i -e "1s/$VENV_EXE\n\n/" "dwn_sb_logs.py"
    echo "$VENV_EXE" | cat - $MAIN_FILE > temp && mv temp $MAIN_FILE
    echo "Making $MAIN_FILE executable."
    chmod +x $MAIN_FILE
done


#chmod +x aws_uploads.py
#chmod +x aws_utils.py
#chmod +x dwn_logs.py


APILOGS_UPLOADS_PATH='apilogs/uploads'
APILOGS_DOWNLOADS_PATH='apilogs/downloads'

if [ ! -d $APILOGS_UPLOADS_PATH ]; then
    echo "Creating $APILOGS_UPLOADS_PATH on this path."
    mkdir -p $APILOGS_UPLOADS_PATH
else
    echo "$APILOGS_UPLOADS_PATH already exists!"
fi

if [ ! -d $APILOGS_DOWNLOADS_PATH ]; then
    echo "Creating $APILOGS_DOWNLOADS_PATH on this path."
    mkdir -p $APILOGS_DOWNLOADS_PATH
else
    echo "$APILOGS_DOWNLOADS_PATH already exists!"
fi

echo ">>> All transformations are now done! <<<"
