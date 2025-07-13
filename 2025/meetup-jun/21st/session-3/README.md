# hydpy-demo
This repository is created for hydpy meetup demo

## Instructions
1. Create a gcs bucket.
2. Create a service account in gcp.
3. Create a .json key file to push the data into GCS bucket.
4. Trigger the python progream by running the batch file from command line -> run_streamer.bat
5. Cleanup files created in local by runinng batch file from command line -> clean.bat

## Sample .env
BUCKET_NAME=hydpy_demo
DESTINATION_BLOB_PREFIX=data_streamer
SERVICE_JSON=gcp_hydpy_demo.json
CHUNK_SIZE=5
SLEEP_TIME=60
LOG_LEVEL=INFO

