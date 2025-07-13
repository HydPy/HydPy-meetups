import csv
import time
import random
import logging
import os
from dataclasses import dataclass, field
from faker import Faker
from google.cloud import storage
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

BUCKET_NAME = os.getenv('BUCKET_NAME')
DESTINATION_BLOB_PREFIX = os.getenv('DESTINATION_BLOB_PREFIX')
SERVICE_JSON = os.getenv('SERVICE_JSON')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 5))
SLEEP_TIME = int(os.getenv('SLEEP_TIME', 60))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Configure logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("StreamDataPipeline")

@dataclass
class DataGenerator:
    """Generates fake nation data."""
    fake: Faker = field(default_factory=Faker)

    def generate(self, num_records=5, start_nationkey=1):
        data = []
        for i in range(num_records):
            nationkey = start_nationkey + i
            name = self.fake.country()
            regionkey = random.randint(1, 5)
            comment = self.fake.sentence()
            data.append({
                'NATIONKEY': nationkey,
                'NAME': name,
                'REGIONKEY': regionkey,
                'COMMENT': comment
            })
        logger.debug(f"Generated {num_records} records starting from NATIONKEY {start_nationkey}")
        return data

class CSVWriter:
    """Writes data to a CSV file."""
    @staticmethod
    def write(data, filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['NATIONKEY', 'NAME', 'REGIONKEY', 'COMMENT'])
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Wrote {len(data)} records to {filename}")

@dataclass
class GCSUploader:
    """Uploads files to Google Cloud Storage."""
    bucket_name: str
    service_json: str
    storage_client: storage.Client = field(init=False)
    bucket: storage.Bucket = field(init=False)

    def __post_init__(self):
        self.storage_client = storage.Client.from_service_account_json(self.service_json)
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def upload(self, source_file_name, destination_blob_name):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        logger.info(f"Uploaded {source_file_name} to gs://{self.bucket_name}/{destination_blob_name}")

@dataclass
class StreamDataPipeline:
    """Coordinates the data generation, writing, and uploading."""
    generator: DataGenerator
    writer: CSVWriter
    uploader: GCSUploader
    chunk_size: int = 5
    sleep_time: int = 30
    chunk_number: int = field(default=1, init=False)
    nationkey_counter: int = field(default=1, init=False)

    def run(self):
        logger.info("Starting Stream Data Pipeline...")
        while True:
            filename = f'data_streamer_{self.chunk_number}.csv'
            data = self.generator.generate(self.chunk_size, start_nationkey=self.nationkey_counter)
            self.nationkey_counter += self.chunk_size
            self.writer.write(data, filename)
            destination_blob_name = f"nation_data/{DESTINATION_BLOB_PREFIX}_{self.chunk_number}.csv"
            self.uploader.upload(filename, destination_blob_name)
            self.chunk_number += 1
            logger.info(f"Sleeping for {self.sleep_time} seconds before next chunk...")
            time.sleep(self.sleep_time)

if __name__ == "__main__":
    generator = DataGenerator()
    writer = CSVWriter()
    uploader = GCSUploader(BUCKET_NAME, SERVICE_JSON)
    pipeline = StreamDataPipeline(generator, writer, uploader, chunk_size=CHUNK_SIZE, sleep_time=SLEEP_TIME)
    try:
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("Stream Data Pipeline stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)