from dotenv import load_dotenv
import os 
import logging
import streamlit as st

load_dotenv()

logging.basicConfig(
    filename='error.log', # Set a file for save logger output 
    level=logging.INFO, # Set the logging level
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

LOGGER = logging.getLogger(__name__)
LOGGER.info("Init Global Variable")

load_dotenv() 

class SetupApi:
    api_key = st.secrets["api"]
    weather_key = api_key["weather_key"]  
    open_ai_key = api_key["OPENAI_API_KEY"]
    ASTRADB_TOKEN_KEY = api_key["ASTRADB_TOKEN_KEY"]
    ASTRADB_API_ENDPOINT = api_key["ASTRADB_API_ENDPOINT"]
    ASTRADB_COLLECTION_NAME = api_key["ASTRADB_COLLECTION_NAME"]
    
    
LIST_COLUMNS_FILTER  = {
        "q": "City name, optionally with a country code (e.g., 'London')",
        "zip": "ZIP or postal code, optionally with a country code (e.g., '10001,us')",
        "lat": "Latitude of the location (e.g., '40.7128')",
        "lon": "Longitude of the location (e.g., '-74.0060')",
        "lang": "Language for weather description (e.g., 'en' for English, 'es' for Spanish)",
        "cnt": "Number of forecast data points to return",
        "units": "Units for temperature (default: 'standard' for Kelvin; 'metric' for Celsius; 'imperial' for Fahrenheit) [OPTIONAL]",
    }

