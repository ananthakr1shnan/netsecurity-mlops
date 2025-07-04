from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfigEntity
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()

mongo_db_url=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfigEntity):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
     
    def export_collection_as_dataframe(self):
        try:
             database_name = self.data_ingestion_config.database_name
             collection_name = self.data_ingestion_config.collection_name
             self.mongo_client = pymongo.MongoClient(mongo_db_url)
             collection=self.mongo_client[database_name][collection_name]

             df=pd.DataFrame(list(collection.find({})))
             if "_id" in df.columns.tolist():
                 df.drop(columns=["_id"],axis=1, inplace=True)
             df.replace({"na": np.nan}, inplace=True)
             return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    def export_data_to_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_dir
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False,header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
       
       
    def split_data_as_train_test(self, dataframe: pd.DataFrame): 
        try:
            train_set,test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=42)
            logging.info("Train test split completed successfully")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info("Exporting train and test data to respective file paths")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
            logging.info("Train and test data exported successfully")
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            data_ingestion_artifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)