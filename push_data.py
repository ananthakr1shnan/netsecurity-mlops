import os
import sys
from dotenv import load_dotenv
import json
import certifi
from pymongo.mongo_client import MongoClient
load_dotenv()

url = os.getenv("MONGO_DB_URL")
ca=certifi.where()

import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging  

class NetworkDataExtract():
    def __init__(self):
        try:
            self.client = MongoClient(url, tlsCAFile=ca)
            self.db = self.client['NetworkSecurity']
            self.collection = self.db['network_data']
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json(self, csv_file):
        try:
            df = pd.read_csv(csv_file)
            df.reset_index(drop=True, inplace=True)
            records=list(json.loads(df.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records,database, collection):
        try:
            self.records = records
            self.mongo_client=pymongo.MongoClient(url)
            self.database = self.mongo_client[database]
            self.collection = self.database[collection]
            self.collection.insert_many(self.records)
            return len(self.records)
    
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH = "Data\phishingData.csv"
    DATA_BASE = "NetworkSecurity"
    COLLECTION = "network_data"
    network_obj = NetworkDataExtract()
    records = network_obj.csv_to_json(FILE_PATH)
    no_of_records = network_obj.insert_data_mongodb(records=records, database=DATA_BASE, collection=COLLECTION)
    logging.info(f"Number of records inserted: {no_of_records}")
    