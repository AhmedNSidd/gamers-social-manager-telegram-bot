#! /bin/bash

# This is a shell script that provisions a database based o
# GSM_DB_URL_WITHOUT_USERNAME_AND_PASSWORD='${mongodbatlas_serverless_instance.gsm-db.connection_strings_standard_srv}' GSM_DB_USERNAME='${var.MONGODBATLAS_DB_USER_USERNAME}' GSM_DB_PASSWORD='${random_password.mongodbatlas_password.result}' &&
# ${var.PSN_NPSSO}
# ${var.XBOX_CLIENT_ID}
# ${var.XBOX_CLIENT_SECRET}
source /Users/ahmedsiddiqui/Workspace/Virtual_Environments/gsm-venv/bin/activate
python ../bot/scripts/authentication/playstation_authentication.py -n $PSN_NPSSO
python ../bot/scripts/authentication/xbox_authentication.py -cid $XBOX_CLIENT_ID -cs $XBOX_CLIENT_SECRET
