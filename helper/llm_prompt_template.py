# ********** IMPORT FRAMEWORK **********
from langchain_core.prompts             import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers      import JsonOutputParser, StrOutputParser
from pydantic                           import Field, BaseModel


LIST_DATA_COLUMNS = {
           "Location": "The city or place where the weather information is relevant. E.g., 'New York, NY'.",
            "Coordinates_Latitude": "The latitude of the location. E.g., '40.7143'.",
            "Coordinates_Longitude": "The longitude of the location. E.g., '-74.006'.",
            "Weather_Conditions": "A description of the current weather conditions. E.g., 'Overcast clouds'.",
            "Temperature_Current": "The current temperature at the location in Celsius. E.g., '-2.84'.",
            "Temperature_Feels_Like": "The perceived temperature (considering wind and humidity). E.g., '-2.40'.",
            "Temperature_Minimum": "The minimum temperature observed at the location in Celsius. E.g., '1.90'.",
            "Temperature_Maximum": "The maximum temperature observed at the location in Celsius. E.g., '3.89'.",
            "Pressure_hPa": "The atmospheric pressure at the location, measured in hectopascals (hPa). E.g., '1002'.",
            "Humidity_Percent": "The humidity at the location, expressed as a percentage. E.g., '48'.",
            "Visibility_km": "The visibility at the location, measured in kilometers. E.g., '10'.",
            "Wind_Speed_m_s": "The speed of the wind at the location, measured in meters per second. E.g., '8.75'.",
            "Wind_Direction_Degrees": "The wind direction at the location, measured in degrees. E.g., '250'.",
            "Wind_Gusts_m_s": "The gust speed of the wind at the location, measured in meters per second. E.g., '12.86'.",
            "Cloud_Cover_Percent": "The percentage of cloud cover at the location. E.g., '100'.",
            "Sunrise": "The time of sunrise at the location, not yet converted. E.g., '07:20 AM'.",
            "Sunset": "The time of sunset at the location, not yet converted. E.g., '05:30 PM'.",
            "Timezone": "The timezone of the location. E.g., 'UTC-5'."
    }

# *************** Expected format for function convert text to filter
class FilterExpect(BaseModel): 
    """
    FilterExpect defines the expected structure for filter_created.
    """
    filter_created: list = Field(description=[{ 
                                               "field_name": "one of the 'filter_used'",
                                               "value_target": "the value of field expect"
                                               }])
    
# *************** Expected format for function generate decision intent
class IntentDetected(BaseModel):
    """
    IntentDetected defines the expected structure for intent_detected.
    """
    intent_detected: list = Field(description=[{"intent": "The detected intent of the user input.",
                                               "reason": "The reason for the detected intent."
                                              }])

class DataExtracted(BaseModel):
    """
    DataExtracted defines the expected extracted data from llm response.
    """
    extracted_data: list = Field(description=[{
           "Location": "The city or place where the weather information is relevant. E.g., 'New York, NY'.",
            "Coordinates_Latitude": "The latitude of the location. E.g., '40.7143'.",
            "Coordinates_Longitude": "The longitude of the location. E.g., '-74.006'.",
            "Weather_Conditions": "A description of the current weather conditions. E.g., 'Overcast clouds'.",
            "Temperature_Current": "The current temperature at the location in Celsius. E.g., '-2.84'.",
            "Temperature_Feels_Like": "The perceived temperature (considering wind and humidity). E.g., '-2.40'.",
            "Temperature_Minimum": "The minimum temperature observed at the location in Celsius. E.g., '1.90'.",
            "Temperature_Maximum": "The maximum temperature observed at the location in Celsius. E.g., '3.89'.",
            "Pressure_hPa": "The atmospheric pressure at the location, measured in hectopascals (hPa). E.g., '1002'.",
            "Humidity_Percent": "The humidity at the location, expressed as a percentage. E.g., '48'.",
            "Visibility_km": "The visibility at the location, measured in kilometers. E.g., '10'.",
            "Wind_Speed_m_s": "The speed of the wind at the location, measured in meters per second. E.g., '8.75'.",
            "Wind_Direction_Degrees": "The wind direction at the location, measured in degrees. E.g., '250'.",
            "Wind_Gusts_m_s": "The gust speed of the wind at the location, measured in meters per second. E.g., '12.86'.",
            "Cloud_Cover_Percent": "The percentage of cloud cover at the location. E.g., '100'.",
            "Sunrise": "The time of sunrise at the location, not yet converted. E.g., '07:20 AM'.",
            "Sunset": "The time of sunset at the location, not yet converted. E.g., '05:30 PM'.",
            "Timezone": "The timezone of the location. E.g., 'UTC-5'."
    }])
    
# *************** Template prompt for function convert text to filter
def prompt_convert_text_to_filter() -> PromptTemplate:
    """
    Prompt to generate filter to use with weather api call

    Returns:
        PromptTemplate: _description_
    """
        
    template = """
    You are Filter Creation. Your task is to convert user input into filters. 
    
    Input: 
    "text_input": {text_input}
    "filter_used": {field_names} 
    "chat_history": {chat_history}
    
    Instructions:
    1. Analyze "text_input" for new filters.
    2. Validate all filters against "filter_used".
    3. Use "chat_history" to see if the user has already provided enough information in previous messages.
    4. Always use "chat_history" to see type "human" and "ai" to determine if the "filter_used" information already exists. If so, update that information.
    5. Deep thinking the context of "text_input" and previous messages "chat_history" to create correct filter based on follow-up question.
    
    few shots example of handling follow up "text_input": 
    - first "text_input" : "how's the weather condition in yogyakarta?" 
    - second "text_input" : "i'm also need the forecast" 
    - Means for the second "text_input" you need to create yogyakarta as the filters 
    
    Output:
    Return filters as a JSON list with "field_name", and "value_target".
    {format_instructions}
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["text_input", "field_names", "chat_history"],
        partial_variables={"format_instructions": JsonOutputParser(pydantic_object=FilterExpect).get_format_instructions()}
    )
    
    
# *************** Template prompt for response format weather
def prompt_response_format_weather() -> PromptTemplate:
    """
    Prompt to generate filter to use with weather api call

    Returns:
        PromptTemplate: _description_
    """
        
    template = """
    You are Professional Weather analyst. 
    Your task is to convert the weather_information from the weather mess information list dict into a readable format analysis information. 
    
    Input: 
    "weather_information": {response}
    
    Instructions:
    1. Analyze the "weather_information" for all important weather elements (e.g location, coordinates, current weather, temperature, humidity, pressure, wind, cloud coverage, visibility, sunrise, sunset, timezone).
    2. Summarize these elements in a **brief** but **complete** manner.
    3. Avoid lengthy explanations; focus on **key facts** and **important figures**.
    4. If multiple data points exist (e.g., a 5-day forecast), provide a short overview or bullet-point highlights rather than an exhaustive list.
    5. Explain brief summary the condition weather based on all the information "weather_information"
    6. If got "weather_information" contain ERROR state that the data is not available and assist the user to change the filter, format response using readable format (e.g "The data is not available try to change the location or zip").
    
    Note: 
    - DO NOT use jargon terchinal terms.
    Output:
    Return the weather_information in a structured format.
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["response"],
    )
    
# *************** Prompt to handle question unrelated to weather
def prompt_unrelated_question() -> PromptTemplate:
    """
    Prompt to handle unrelated user's input.
    
    Returns:
        PromptTemplate: The prompt template for generating the decision.
    """
    
    template = """ 
    You are a Weather expert assistant chatbot. 
    Your task is to respond professionally based on the 'input_text' and 'user_intent' with no greetings. 

    Input: 
    "input_text": {input_text}
    "user_intent": {user_intent}
    
    Instructions:
    1. Analyze the "input_text" and "user_intent".
    2. If the "input_text" is a general greeting, respond politely to assist the user.'
    3. If the "input_text" is unrelated to weather, respond professionally stating that the topic is out of scope, with no greetings or jargon technical terms.
    """
    
    return PromptTemplate(template=template, 
                          input_variable = ["input_text", "user_intent"])
    
# *************** Prompt to handle incomplete filters user's input
def prompt_incomplete_filters() -> PromptTemplate:
    """
    Prompt to handle incomple filters user's input.
    
    return:
        PromptTemplate: The prompt template for generating the decision.
    """
    
    template = """
    You are a Weather expert assistant chatbot.
    Your task is to respond back to user's that one of the filters from "list_filters" 
    is missing in the "input_text".
    
    Inputs:
    "input_text": {input_text}
    "list_filters": {list_filters}
    
    Instructions:
    1. Analyze the "input_text" and "list_filters".
    2. Identify the missing filter from "list_filters" in the "input_text".
    3. Respond back to the user that the filter is missing. Don't use JARGON TECHNICAL TERMS.
    4. Provide a suggestion to the user to include the missing filter in the "input_text".
    """
    return PromptTemplate(template=template, 
                          input_variables=["input_text", "list_filters"])
    
    
# *************** Prompt template for topic creation
def prompt_topic_creation() -> PromptTemplate:
    """
    Prompt to create topic creation based on the first conversation
    
    Returns:
        PromptTemplate: Prompt template
    """
    
    template = """
    You are a topic creation assistant expert. 
    Your task is to create a topic based on the response user's input and AI input on a conversation.
    
    Input : 
    Chat : {chat_history}
    
    Instructions:
    - Do not use jargon technical terms
    - Analyze from user's input type "human" and AI response type "ai" before create the topic.
    - Max 4 words for the topic generated.
    """
    return PromptTemplate(template = template,
                          input_variables=["chat_history"])    

# *************** Prompt for intent detection
def prompt_generate_decision() -> PromptTemplate:
    """
    Prompt to generate the decision based on the input text.

    Returns:
        PromptTemplate: The prompt template for generating the decision.
    """
    template = """
    You are a Weather expert assistant chatbot. 
    Your primary tasks: 
    - Detect the user's intent regarding weather information.
    - Classify the intent as one of the following categories:
      1. 'current_weather': If the user asks for current weather conditions or needs weather information (but if the user's have one of the filters in the "input_text").
      2. 'forecast': If the user asks for weather forecasts, or future conditions (but if the user's have one of the filters in the "input_text").
      3. 'historical_weather': If the user asks for past weather data (but if the user's have one of the filters in the "input_text").
      4. 'create': If the user wants to save/create/add/etc the weather data information, analyze "text_input" and "chat_history" first to see if the user already provided one of the filters or not, and to see if the user already got weather information data.
      5. 'read': The user wants to retrieve stored weather data (e.g "Show me weather data for New York", "i wanna see data for city is london")
                Typical phrases include "show me", "find", "view", "retrieve", etc.
      6. 'unknown': If the user question is totally unrelated with the weather topic (state that you cannot answer because the question is out of topic weather analysis ).
      7. 'incomplete': If the user's input is missing *all* required filters for a valid input based on "list_filters".
                          
    Note: 
     - Only *ONE* location filter is mandatory (e.g., 'city name' or 'zip' or 'lat/lon') based on "list_filters".
     - If the user doesn't provide optional fields (like 'units'), default to a suitable value (e.g., 'metric', 'imperial').
     - All other filters are OPTIONAL (e.g units, lang).  
     - Don't classified as incomplete intent if user's input "input_text" and previous message "chat_history" already have enough information at least one filter in "list_filters".
    
    ## Instructions:
      - If the user doesn't provide optional fields (like 'units'), default to a suitable value (e.g., 'metric').
      - Use "chat_history" to see if the user has already provided enough information in previous messages.
        - Look at "chat_history" type 'human' to see if the user has already provided enough information.
        - Look at "chat_history" type 'human' and type "ai" if the user has the context intent and filter they provided
        
    Inputs:
      "input_text": {input_text}
      "list_filters": {list_filters}
      "chat_history": {chat_history}
    
    Output: 
    Response the output must followed this instructions. 
    {format_instructions}
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["input_text", "list_filters", "chat_history"],
        partial_variables= {"format_instructions": JsonOutputParser(pydantic_object=IntentDetected).get_format_instructions()}
    )
    
# *************** Template prompt for response format weather
def prompt_extract_data() -> PromptTemplate:
    """
    Prompt to generate extract data from llm response

    Returns:
        PromptTemplate: _description_
    """
        
    template = """
    You are Professional Weather analyst. 
    Your task is to detect weather data from "weather_information".
    
    Input: 
    - "weather_information": {chat_history}
    
    Note: 
    - Analyze from "type" is ai from "weather_information" and then detect all the data based on "format_instructions"
    
    Instructions:
    1. Analyze the "weather_information" for all important weather data field based on "format_instructions".
    2. Ensure the format is correct based format_instructions
    3. Only put the correct data any data that is not related then don't take it.
    
    Output:
    Response the output must followed this format_instructions!. Do not over created the output structure.
    {format_instructions}
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["chat_history"],
        partial_variables= {"format_instructions": JsonOutputParser(pydantic_object=DataExtracted).get_format_instructions()}
    )
    
# *************** Template prompt for response insert data
def prompt_response_insert_data() -> PromptTemplate:
    """
    Prompt to response after 

    Returns:
        PromptTemplate: _description_
    """
        
    template = """
    You are Professional Weather analyst. 
    Your task is to response in a proffesional with no greetings for user after saved the data to database.
    
    Input: 
    - "information_succes": {information_msg}

    Instructions:
    1. Analyze "information_succes" if it has len number means inform user saved the data is succesful, and otherwise
    2. DO NOT use jargon techincal terms.
    3. If it succesfully, response to assist the user.
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["information_msg"],
    )
    

def prompt_template_query_df() -> PromptTemplate:
    """
    
    """
    template = """
        You are a data analysis expert!
        Your task is to generate code for data analysis with data is in DataFrame format. 
        
        Input: 
         - "question" : {question}
         - "description_columns" : {description_columns}
         - "previous_message" : {chat_history}
         
        Instructions: 
        - Understand the User's Intent 
            - Analyze the "question" to determine the type of data analysis required.
            - Use "previous_message" to maintain continuity and ensure logical follow-up questions. 
        
        - Ensure Readability & Usability
            - The DataFrame is always referred to as **df**
            - Always include a print statement to display results.
            - Do Not create sample data (the DataFrame `df` already exists).
            - Use contains pandas over exact same match "==" if user want to get exact match.
            - ALL DATA TYPE IS STRING AND DONT FORGET TO RE-ASSIGN TO `df` variable.
        
        - Formatting & Output
            - Return **only executable Python code**, without explanations.
        
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["question","description_columns", "chat_history"],
    )
    

def prompt_response_data_analysis() -> PromptTemplate:
    """

    Returns:
        PromptTemplate: prompt to response after get the data from the code
    """
    
    template = """ 
        You are a weather data analysis expert specializing in providing clear data analysis to provide information.
        
        Your task is to:
            1. First, present the data in a clear, readable format
            2. Then provide a detailed analysis with no "Data Quality Issues", and provide analysis for all available columns.
            
        Input: 
        - weather_data: {data}
            
        Note: 
        - Please provide your analysis in clear, natural language focusing on the most relevant insights for general understanding. Include specific numbers from the data to support your observations. If you notice any potential data quality issues or missing values, mention them as well.
        - Do not use jargon technical terms
        - Keep the data presentation organized and scannable
    """
    return PromptTemplate(
        template=template,
        input_variables=["data"],
    )
    
    