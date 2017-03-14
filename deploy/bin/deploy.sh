#!/bin/bash
touch /webapps/schedulr/howdy

sleep 5s

su - schedulr_app << EOF

cd Schedulr
git pull
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic --no-input

EOF

supervisorctl restart schedulr
