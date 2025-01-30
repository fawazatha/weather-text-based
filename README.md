# 🌦️ Weather Data Analysis Chatbot
A Streamlit-powered chatbot that allows users to **retrieve weather data, forecast, store data into database, and read it back all using query** dynamically using **LangChain, OpenWeather API, AstraDB, OpenAI API, and Pandas**. The system **intelligently understands user queries** and executes **Pandas-based data analysis** using **LLM-generated code** to read back the data.

---

## 🚀 **Live Demo**
🎯 **[Access the Streamlit App Here](https://chat-weather-bot.streamlit.app/)**  

---

## 📌 **Features**
✔ **Real-time Weather Queries** - Fetch live weather data from OpenWeather API.  
✔ **Stored Weather Data Retrieval** - Query previously saved weather data from AstraDB.  
✔ **AI-Powered Data Analysis** - Uses LLMs to generate **optimized Pandas queries** dynamically.  
✔ **Natural Language Understanding** - Automatically detects user intent.    

---

## 🛠️ **Tech Stack**
| **Technology** | **Usage** |
|---------------|----------|
| **Python** | Core programming language |
| **Streamlit** | Web-based UI for user interaction |
| **LangChain** | LLM-powered query conversion & execution |
| **OpenWeather API** | Fetches real-time weather data |
| **AstraDB (Cassandra)** | Stores historical weather data |
| **Pandas** | Performs **AI-driven** data analysis |
| **OpenAI API** | Models to handle all the intent |

---

## ⚙️ **How to Run the Project Locally**
### **1️⃣ Clone the Repository**
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
### **2️⃣ Install Dependencies**
pip install -r requirements.txt
### **3️⃣ Set Up Environment Variables**
you can set up from .env or .streamlit/secrets.toml
.env : 
OPENWEATHER_API_KEY=your_openweather_api_key
ASTRADB_APPLICATION_TOKEN=your_astradb_token
ASTRADB_API_ENDPOINT=your_astradb_endpoint
STREAMLIT_DEPLOYMENT_URL=your_streamlit_app_url
secrets.toml:
[api]
OPENWEATHER_API_KEY=your_openweather_api_key
ASTRADB_APPLICATION_TOKEN=your_astradb_token
ASTRADB_API_ENDPOINT=your_astradb_endpoint
STREAMLIT_DEPLOYMENT_URL=your_streamlit_app_url
then get it using like api_key = st.secrets['api']
weather_key = api_key["weather_key"]  
### **4️⃣ Run the Streamlit App**
streamlit run chat_weather_ui.py

## 🎯 **How It Works**
### User Queries a Weather-Related Question
"how's the weather condition in london"
### User's Queries a forecast
"give me the forecast for city kuala lumpur"
### User's Queries saved the data
"save the data for me"
### User's Queries to read back the data and get analysis
"find me data weather for city is london and humidity more than 10"

