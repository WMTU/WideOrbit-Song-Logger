#!/bin/bash

# configuration parameters
API_KEY=$(cat ./key.txt)
LOG_DIR="./test-logs"

if [! -d $LOG_DIR]; then
    mkdir $LOG_DIR
else
    rm -rf $LOG_DIR
fi

#############################################
## SongAPI
#############################################

# log with all parameters
printf "\nTest 1" > $LOG_DIR/SongAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist", "album": "Test Album", "genre": "Test", "location": "WMTU", "cd_id": "XXX"}' \
http://localhost:9190/api/2.0/song \
>> $LOG_DIR/SongAPI.txt

# log with only required parameters
printf "\nTest 2" >> $LOG_DIR/SongAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist"}' \
http://localhost:9190/api/2.0/song \
>> $LOG_DIR/SongAPI.txt

# log without required artist
printf "\nTest 3" >> $LOG_DIR/SongAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song"}' \
http://localhost:9190/api/2.0/song \
>> $LOG_DIR/SongAPI.txt

# log without api key
printf "\nTest 4" >> $LOG_DIR/SongAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"song": "Test Song", "artist": "Test Artist"}' \
http://localhost:9190/api/2.0/song \
>> $LOG_DIR/SongAPI.txt

# log with invalid key
printf "\nTest 5" >> $LOG_DIR/SongAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "123456789012345678901234567890", "artist": "Test Artist"}' \
http://localhost:9190/api/2.0/song \
>> $LOG_DIR/SongAPI.txt


#############################################
## DiscrepancyAPI
#############################################

# log with all parameters
printf "\nTest 1" > $LOG_DIR/DiscrepancyAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist", "dj_name": "Some DJ", "word": "swear", "button_hit": true}' \
http://localhost:9190/api/2.0/discrepancy \
>> $LOG_DIR/DiscrepancyAPI.txt

# log with missing parameters
printf "\nTest 2" >> $LOG_DIR/DiscrepancyAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist", "dj_name": "Some DJ", "word": "swear"}' \
http://localhost:9190/api/2.0/discrepancy \
>> $LOG_DIR/DiscrepancyAPI.txt

# log without api key
printf "\nTest 3" >> $LOG_DIR/DiscrepancyAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"song": "Test Song", "artist": "Test Artist", "dj_name": "Some DJ", "word": "swear", "button_hit": true}' \
http://localhost:9190/api/2.0/discrepancy \
>> $LOG_DIR/DiscrepancyAPI.txt

# log with invalid key
printf "\nTest 4" >> $LOG_DIR/DiscrepancyAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "123456789012345678901234567890", "song": "Test Song", "artist": "Test Artist", "dj_name": "Some DJ", "word": "swear", "button_hit": true}' \
http://localhost:9190/api/2.0/discrepancy \
>> $LOG_DIR/DiscrepancyAPI.txt


#############################################
## RequestAPI
#############################################

# log with all parameters
printf "\nTest 1" > $LOG_DIR/RequestAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist", "album": "Test Album", "rq_name": "WMTU Listener", "rq_message": "This is a test message for the song request API!"}' \
http://localhost:9190/api/2.0/request \
>> $LOG_DIR/RequestAPI.txt

# log with required parameters
printf "\nTest 2" >> $LOG_DIR/RequestAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song", "artist": "Test Artist"}' \
http://localhost:9190/api/2.0/request \
>> $LOG_DIR/RequestAPI.txt

# log with missing parameter
printf "\nTest 3" >> $LOG_DIR/RequestAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "$API_KEY", "song": "Test Song"}' \
http://localhost:9190/api/2.0/request \
>> $LOG_DIR/RequestAPI.txt

# log without api key
printf "\nTest 4" >> $LOG_DIR/RequestAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"song": "Test Song", "artist": "Test Artist", "album": "Test Album", "rq_name": "WMTU Listener"}' \
http://localhost:9190/api/2.0/request \
>> $LOG_DIR/RequestAPI.txt

# log with invalid key
printf "\nTest 5" >> $LOG_DIR/RequestAPI.txt
curl -X POST -H "Content-Type: application/json" \
-d '{"api_key": "123456789012345678901234567890", "song": "Test Song", "artist": "Test Artist", "album": "Test Album", "rq_name": "WMTU Listener"}' \
http://localhost:9190/api/2.0/request \
>> $LOG_DIR/RequestAPI.txt


#############################################
## LogAPI
#############################################

# get a default log
printf "\nTest 1" > $LOG_DIR/LogAPI.txt
curl http://localhost:9190/api/2.0/log >> $LOG_DIR/LogAPI.txt

# get a song
printf "\nTest 2" >> $LOG_DIR/LogAPI.txt
curl http://localhost:9190/api/2.0/log?type=song >> $LOG_DIR/LogAPI.txt

# get a discrepancy
printf "\nTest 3" >> $LOG_DIR/LogAPI.txt
curl http://localhost:9190/api/2.0/log?type=discrepancy >> $LOG_DIR/LogAPI.txt

# get a request
printf "\nTest 4" >> $LOG_DIR/LogAPI.txt
curl http://localhost:9190/api/2.0/log?type=request >> $LOG_DIR/LogAPI.txt


#############################################
## StatsAPI
#############################################

# get a default stats request
printf "\nTest 1" > $LOG_DIR/StatsAPI.txt
curl http://localhost:9190/api/2.0/stats >> $LOG_DIR/StatsAPI.txt


exit 0