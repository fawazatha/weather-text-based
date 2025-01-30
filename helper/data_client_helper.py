# ********** IMPORT FRAMEWORK **********
from setup      import (SetupApi, 
                        LOGGER, 
                      )

from astrapy    import DataAPIClient
from typing     import List
import pandas   as pd 

def connection_col():
    client = DataAPIClient(SetupApi.ASTRADB_TOKEN_KEY)
    database = client.get_database(SetupApi.ASTRADB_API_ENDPOINT)
    collection = database.get_collection(SetupApi.ASTRADB_COLLECTION_NAME)
    return collection 

def create_data(data):
    client = DataAPIClient(SetupApi.ASTRADB_TOKEN_KEY)
    database = client.get_database(SetupApi.ASTRADB_API_ENDPOINT)
    collection = database.get_collection(SetupApi.ASTRADB_COLLECTION_NAME)
    
    data = data.get("extracted_data")
    result = collection.insert_many(data)
    inserted_count = len(result.inserted_ids)  
    inserted_count = (f"Inserted {inserted_count} documents successfully.")
    return inserted_count
    
class WeatherDataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WeatherDataManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.df = self._initial_load()
    
    def _initial_load(self) -> pd.DataFrame:
        """Initial load of weather data from AstraDB"""
        try:
            coll = self._get_collection()
            cursor = coll.find({})
            data = list(cursor)
            
            if not data:
                LOGGER.info("No weather data found.")
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df = df.drop(columns=['_id'], errors='ignore')
            
            LOGGER.info(f"Initially loaded {len(df)} weather records into DataFrame.")
            return df
            
        except Exception as e:
            LOGGER.error(f"Error in initial data load: {str(e)}")
            return pd.DataFrame()
    
    def _get_collection(self):
        """Get AstraDB collection"""
        client = DataAPIClient(SetupApi.ASTRADB_TOKEN_KEY)
        database = client.get_database(SetupApi.ASTRADB_API_ENDPOINT)
        return database.get_collection(SetupApi.ASTRADB_COLLECTION_NAME)
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the current DataFrame"""
        return self.df, self.df.head()
    
    def update_with_new_data(self, new_data: list[dict]) -> None:
        """Update DataFrame with new records"""
        try:
            new_df = pd.DataFrame(new_data)
            if self.df.empty:
                self.df = new_df
            else:
                self.df = pd.concat([self.df, new_df], ignore_index=True)
            
            LOGGER.info(f"Added {len(new_df)} new records. Total records: {len(self.df)}")
            
        except Exception as e:
            LOGGER.error(f"Error updating DataFrame: {str(e)}")