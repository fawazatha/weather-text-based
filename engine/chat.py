# ********** IMPORT FRAMEWORK **********
from langchain_core.prompts             import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables           import RunnableParallel 
from pydantic                           import Field, BaseModel
from langchain_core.output_parsers      import JsonOutputParser, StrOutputParser
from langchain_community.callbacks      import get_openai_callback
from langchain_core.messages            import HumanMessage, AIMessage, BaseMessage

# ********** IMPORT LIBRARIES **********
import requests
import sys 
import os
from typing     import List, Dict, Tuple
from operator   import itemgetter
import re
import pandas   as pd

# ********** IMPORT **********
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from setup      import (SetupApi, 
                        LOGGER, 
                        LIST_COLUMNS_FILTER, 
                      )

# ********** IMPORT MODEL **********
from model.llms import LLM

# ********** IMPORT HELPER **********
from helper.response_error_helper   import json_clean_output
from helper.data_client_helper      import create_data, connection_col, WeatherDataManager
from helper.llm_prompt_template     import (prompt_convert_text_to_filter,
                                            prompt_response_format_weather, 
                                            prompt_unrelated_question,
                                            prompt_incomplete_filters, 
                                            prompt_topic_creation,
                                            prompt_generate_decision,
                                            prompt_extract_data,
                                            prompt_response_insert_data,
                                            prompt_template_query_df, 
                                            prompt_response_data_analysis,
                                            LIST_DATA_COLUMNS
                                            )

# ********** IMPORT VALIDATOR **********
from validator.data_type_validation import (validate_string_input, 
                                            validate_dict_input, 
                                            validate_int_input,
                                            validate_list_input)


# ********** Function to handle query user to code generation **********
def handle_query_to_code(question: str, description_columns: dict, chat_history: List[dict]) -> str:
    """Generates Python code based on a natural language query about data analysis.
    
    Args:
        question (str): The natural language query about what analysis to perform
        description_columns (list): List of column names and their descriptions
        chat_history (list): Previous conversation context between user and system
    
    Returns:
        str: Generated Python code that performs the requested data analysis
    """
    
    prompt = prompt_template_query_df()
    
    # ********* Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "question": itemgetter('question'),
                                    "description_columns": itemgetter('description_columns'),
                                    "chat_history": itemgetter('chat_history')
                                }
                            )
    
    # ********* chaining prompt with llm
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM() |
             StrOutputParser()
             )
    
    # ********* Invoke the chain
    filter_response = chain.invoke(
                                    {
                                        "question": question, 
                                        "description_columns": description_columns,
                                        "chat_history": chat_history
                                    }
                                )
    
    return filter_response
     
# ********** Function to handle response for data analysis **********
def handle_response_data_analysis(data: str) -> str:
    """
    Processes analyzed data and generates a natural language response describing the results.
    
    Args:
        data (pd.DataFrame): DataFrame containing the analyzed weather data results
    
    Returns:
        str: Natural language response describing the analysis results and insights
    """
    
    if not validate_string_input(data, "data"):
        LOGGER.error("input must be a string")
    
    prompt = prompt_response_data_analysis()
    
    # ********* Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "data": itemgetter('data'),
                            
                                }
                            )
    
    # ********* chaining prompt with llm
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM() |
             StrOutputParser()
             )
    
    # ********* Invoke the chain
    filter_response = chain.invoke(
                                    {
                                        "data": data, 
                                        
                                    }
                                )
    
    return filter_response
    
# *************** Function helper for help engine to convert chat history to chat messages
def convert_chat_history(chat_history: list) -> list[BaseMessage]:
    """
    Convert chat history to the chat messages for inputted to LLM.

    Args:
        chat_history (list): List of chat messages, each containing human and AI content.

    Returns:
        list: Converted chat history with alternating HumanMessage and AIMessage objects.
    """
    
    # *************** Validate inputs chat_history is alist
    if not validate_list_input(chat_history, 'chat_history', False):
        LOGGER.error("'chat_history' must be a list of message.")
    
    # *************** Initialize formatted history
    history_inputted = []
    
    # *************** Add messages to formatted history
    for chat in chat_history:
        if chat['type'] == 'human':
            history_inputted.append(HumanMessage(content=chat['content']))
        elif chat['type'] == 'ai':
            history_inputted.append(AIMessage(content=chat['content']))
    
    if history_inputted:
        LOGGER.info(f"Chat History is Converted to BaseMessages: {len(history_inputted)} messages")  
    else:
        LOGGER.warning("No Chat History Inputted")

    # *************** Return formatted history
    return history_inputted

def save_chat_history(chat_history: list, user_input: str, response: str) -> list[dict]:
    """
    Save user input and AI response to the chat history.

    Args:
        chat_history (list): The existing chat history.
        user_input (str): The user's input.
        response (str): The AI's response.

    Returns:
        list: Updated chat history.
    """
    chat_history.extend([
    {"type": "human", "content": user_input},
    {"type": "ai", "content": response}
    ])
    return chat_history

def process_history_entry(entry: Dict | BaseMessage) -> Tuple[str, str]:
    """
    Process a single history entry.
    
    Args:
        entry (Dict | BaseMessage): The history entry to process.

    Returns:
        Tuple[str, str]: The human and AI content from the history entry.
    """
    if isinstance(entry, dict):
        return entry['human'], entry['ai']
    return entry.content, entry.content
    
def context_window(chat_history: list[BaseMessage], window_size: int = 2) -> list[BaseMessage]:
    """
    Create a context window of the chat history.

    Args:
        chat_history (list): List of chat messages.
        window_size (int): The size of the context window.

    Returns:
        list: The context window of chat messages.
    """
    # *************** Validate inputs chat_history is alist
    if not validate_list_input(chat_history, 'chat_history', False):
        LOGGER.error("'chat_history' must be a list of message.")
    
    # *************** Validate inputs window_size is an integer
    if not validate_int_input(window_size, 'window_size'):
        LOGGER.error("'window_size' must be an integer.")
    
    # *************** Initialize context window
    context_window = []
    
    # *************** Add messages to context window
    for i in range(0, len(chat_history)):
        if i + 1 >= len(chat_history):
            break 
        
        # *************** Process history entry
        human_msg, ai_msg = process_history_entry(chat_history[i])
        context_window.extend([
            HumanMessage(content=human_msg),
            AIMessage(content=ai_msg)
        ])
    
    # *************** Return context window
    window_start = max(0, len(context_window) - (window_size * 2))
    return chat_history[window_start:]
        
# *************** Function to convert text to filter for weather api
def convert_text_to_filter(text_input: str, field_names: list|dict, chat_history:list[dict]) -> dict[list]:
    """
    Convert the user input text into filters to use with the OpenWeather API.

    Args:
        text_input (str): User's input text
        field_names (list | dict): List columns filter to use with the OpenWeather API.

    Returns:
        dict[list]: 
    """
    # *************** Validate inputs text_input not an empty string
    if not validate_string_input(text_input, 'text_input_filter'):
        LOGGER.error("'text_input' must be a string.")
        
    prompt = prompt_convert_text_to_filter()
    
    # ********* Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "text_input": itemgetter('text_input'),
                                    "field_names": itemgetter('field_names'),
                                    "chat_history": itemgetter('chat_history')
                                }
                            )
    
    # ********* chaining prompt with llm
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM()
             )
    
    # ********* Invoke the chain
    filter_response = chain.invoke(
                                    {
                                        "text_input": text_input, 
                                        "field_names": field_names,
                                        "chat_history": chat_history
                                    }
                                )
    
    # ********* Clean the output and logger info
    clean_result = json_clean_output(filter_response)
    LOGGER.info(f"Filter Creation:\n {clean_result}")
    
    return clean_result

# *************** Function to call weather api
def call_weather_api(filters: dict, intent_detected: str) -> List[Dict]:
    """
    Call the OpenWeather API to get the current weather data for multiple locations.

    Args:
        filters (dict): The filters to use in the API call.

    Returns:
        list: A list of responses from the OpenWeather API (one for each input).
    """
    # *************** Validate the filters
    if not validate_dict_input(filters, 'filters'):
        LOGGER.error("'filters' must be a dict.")
        return [{"error": "'filters' must be a non-empty dictionary."}]
    
    required_fields = {"q", "zip", "lat", "lon", "cnt"}
    extracted_params = []
    
    # *************** Flatten filter_created into individual query parameters
    for filter_item in filters.get("filter_created", []):
        field_name = filter_item.get("field_name")
        value_target = filter_item.get("value_target")
        if field_name in required_fields or field_name in {"lang", "units"}:
            extracted_params.append({field_name: value_target})
    
    # *************** Ensure at least one valid input
    if not any(param for param in extracted_params if any(key in required_fields for key in param)):
        LOGGER.error("At least one of 'q', 'zip', 'lat', or 'lon' must be provided.")
    
    # *************** Call OpenWeather API for each valid input
    if intent_detected == "current_weather":
        url = "https://api.openweathermap.org/data/2.5/weather"
    elif intent_detected == "forecast":
        url = "https://api.openweathermap.org/data/2.5/forecast"
    responses = []
    for params in extracted_params:
        try:
            # *************** Add API key to parameters
            full_params = {"appid": SetupApi.weather_key, **params}
            response = requests.get(url, params=full_params)
            response.raise_for_status()
            responses.append(response.json())
        except requests.exceptions.RequestException as e:
            # *************** Log error if API call fails
            LOGGER.error(f"Error calling OpenWeather API: {e}")
            responses.append({"error": f"Error calling OpenWeather API: {e}"})
    
    return responses

# *************** Function to format the response from the OpenWeather API
def response_format_weather(response: List[Dict]): 
    """
    Call the OpenWeather API to get the current weather data for multiple locations.

    Args:
        response (dict): The response from the OpenWeather API call.

    Returns:
        list: A list of responses from the OpenWeather API (one for each input).
    """
    # *************** Validate the filters
    if not validate_list_input(response, 'response'):
        LOGGER.error("'response' must be a list.")
        return [{"error": "'response' must be a non-empty list."}]
    
    prompt = prompt_response_format_weather()
    
    # *************** Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "response": itemgetter('response'),
                                  
                                }
                            )
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM() | 
             StrOutputParser()
             )
    
    filter_response = chain.invoke(
                                    {
                                        "response": response
                                    }
                                )
    
    return filter_response

# *************** Function to handle current weather request
def handle_currrrent_weather(text_input:str, intent_detected: str, chat_history: list[dict]) -> str:
    """
    Handle the user's request for current weather information.

    Args:
        text_input (str): The user's input text.

    Returns:
        response_formatted: The formatted response for the current weather information.
    """
    
    # *************** Validate inputs text_input not an empty string
    if not validate_string_input(text_input, 'text_input'): 
        LOGGER.error("'text_input' must be a string.")
    
    filters = convert_text_to_filter(text_input, LIST_COLUMNS_FILTER, chat_history)
    print(f"\n\n filter: {filters}")
    weather_output = call_weather_api(filters, intent_detected)
    print(f"\n\n weather_api: {weather_output}")
    response_formatted = response_format_weather(weather_output)
    return response_formatted

# *************** Function to handle forecast request
def handle_forecast_weather(text_input:str, intent_detected: str, chat_history: list[dict]) -> str:
    """
    Handle the user's request for weather forecast information.

    Args:
        text_input (str): The user's input text.

    Returns:
        response_formatted: The formatted response for the weather forecast information
    """
    
    # *************** Validate inputs text_input not an empty string
    if not validate_string_input(text_input, 'text_input'):
        LOGGER.error("'text_input' must be a string.")
    
    filters = convert_text_to_filter(text_input, LIST_COLUMNS_FILTER, chat_history)
    print(f"\n\n filter: {filters}")
    weather_ouput = call_weather_api(filters, intent_detected)
    response_formatted = response_format_weather(weather_ouput)
    return response_formatted

# *************** Function to handle question unrelated to weather
def handle_unrelated_question(input_text:str, user_intent:str) -> str:
    """
    Generate response for unrelated user's input.

    Args:
        input_text (str): The input text to analyze.
        user_intent (str): The user's intent for the input text.

    Returns:
        str: The decision generated from the input text.
    """
    # *************** Validate inputs human_input not an empty string
    if not validate_string_input(input_text, 'input_text'):
        LOGGER.error("'input_text' must be a string.")
    if not validate_string_input(user_intent, 'user_intent'):
        LOGGER.error("'user_intent' must be a string.")
        
    template_prompt = prompt_unrelated_question()
    
    # *************** chaining prompt with llm 
    chain_chat = template_prompt | LLM() | StrOutputParser()
    result = chain_chat.invoke({"input_text": input_text, 
                                "user_intent": user_intent})
    return result

# *************** Function to response to incomplete filters user's input
def handle_incomplete_filters(input_text:str, list_filters:dict) -> str:
    """
    Generate the response for incomplete filters in the user's input.

    Args:
        input_text (str): The input text to analyze.
        list_filters (dict): The list of filters to use with the OpenWeather API.

    Returns:
        str: The decision generated from the input text.
    """
    # *************** Validate inputs human_input not an empty string
    if not validate_string_input(input_text, 'input_text'):
        LOGGER.error("'input_text' must be a string.")
    if not validate_dict_input(list_filters, 'list_filters'):
        LOGGER.error("'list_filters' must be a dictionary.")
        
    template_prompt = prompt_incomplete_filters()
    
    # *************** chaining prompt with llm 
    chain_chat = template_prompt | LLM() | StrOutputParser()
    result = chain_chat.invoke({"input_text": input_text, 
                                "list_filters": list_filters})
    return result    
    
# *************** Function to handle topic creation
def topic_creation(chat_history: List[dict]) -> str:
    """

    Args:
        chat_history (List[dict]): Previous chat conversation

    Returns:
        topic (str): topic generated
    """
    
    # *************** Validate input
    if not validate_list_input(chat_history, 'chat_history'):
        LOGGER.error(f"Chat history must be in a list and not empty {chat_history}")
    
    chat_history = convert_chat_history(chat_history)
    prompt = prompt_topic_creation()
    
    # *************** Chain topic creation
    chain = prompt | LLM() | StrOutputParser()
    result = chain.invoke({"chat_history": chat_history})
    return result

# *************** Function to execute the decision intent
def generate_decision(input_text:str, list_filters:dict, chat_history: list[dict]) -> str:
    """
    Generate the decision based on the input text.

    Args:
        input_text (str): The input text to analyze.
        list_filters (dict): The list of filters to use with the OpenWeather API.
        chat_history (list): The chat history to use for context.

    Returns:
        str: The decision generated from the input text.
    """
    # *************** Validate inputs human_input not an empty string
    if not validate_string_input(input_text, 'input_text'):
        LOGGER.error("'input_text' must be a string.")
    
    formatted_hisotry = convert_chat_history(chat_history)
    context_window_history = context_window(formatted_hisotry)
    
    template_prompt = prompt_generate_decision()
    runnable_chain = RunnableParallel({
        "input_text": itemgetter('input_text'),
        "list_filters": itemgetter('list_filters'),
        "chat_history": itemgetter('chat_history')
    })
    # *************** chaining prompt with llm 
    chain_chat = runnable_chain| template_prompt | LLM() 
    result = chain_chat.invoke({"input_text": input_text,
                                "list_filters": list_filters,
                                "chat_history": context_window_history
                                })
    
    result = json_clean_output(result)
    return result

def extract_python_code(text):
    pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        ans = "\n\n".join(matches)
        #print(f'Extracted python code: {ans}')
        return ans
    return ""

def execute_analysis(code: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Execute the generated analysis code on the DataFrame
    
    Args:
        code (str): Python code to execute
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        tuple[pd.DataFrame, str]: Result DataFrame and any error message
    """
    try:
        # Create a local copy of the DataFrame
        local_df = df.copy()
        
        # Add the DataFrame to the local namespace
        local_vars = {'df': local_df, 'pd': pd}
        
        # Execute the code
        exec(code, globals(), local_vars)
        
        # Get the result DataFrame
        result_df = local_vars.get('df', pd.DataFrame())
        return result_df, None
        
    except Exception as e:
        error_msg = f"Error executing analysis: {str(e)}"
        LOGGER.error(error_msg)
        return pd.DataFrame(), error_msg
    
import streamlit as st
# *************** Main function to ask for weather information
def ask_to_chat(text_input: str, chat_history: List[Dict[str, str]], topic:str) -> Tuple[str, List[Dict[str, str]], str]:
    """
    Process chat input and generate appropriate weather-related responses.
    
    Args:
        text_input: User's input text
        chat_history: List of previous chat messages
    
    Returns:
        Tuple containing response information and updated chat history
    """
    try:
        # *************** Validate input
        if not validate_list_input(chat_history, 'chat_history', False):
            LOGGER.error(f"Chat history must be in a list {chat_history}")
        if not validate_string_input(text_input, "text_input"):
            LOGGER.error("'input_text' must be a string.")
        if not validate_string_input(topic, "text_input", False):
            LOGGER.error("'topic' must be a string.")

        # *************** Generate intent
        intent_result = generate_decision(text_input, LIST_COLUMNS_FILTER, chat_history)
        print(f"\n\n intent result: {intent_result}")
        intent_detected = intent_result.get("intent_detected", [{}])[0].get("intent", "unknown")
        
        LOGGER.info(f"Detected intent: {intent_detected}")

        # *************** Intent handlers mapping
        response_information = ""
        data_saved = None
        if intent_detected == "current_weather":
            response_information = handle_currrrent_weather(text_input, intent_detected, chat_history)
        elif intent_detected == "forecast":
            response_information = handle_forecast_weather(text_input, intent_detected, chat_history)
        elif intent_detected == "create":
            data_extracted = handle_extract_data(chat_history)
            print(f"\n\n data_extracted: {data_extracted}")
            data_saved = create_data(data_extracted)
            response_information = handle_response_inserted(data_saved)
        elif intent_detected == "read":
            code_data_analysis = handle_query_to_code(text_input, LIST_DATA_COLUMNS, chat_history)
            code = extract_python_code(code_data_analysis)
            print(f"\n\n code_extracted {code}")
            # At application startup
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 1000)
            weather_manager = WeatherDataManager()

            df, _ = weather_manager.get_dataframe()
            output = execute_analysis(code, df)
            print(f"\n\n output: {output}")
            response_information = handle_response_data_analysis(output)
            
        elif intent_detected == "incomplete":
            response_information = handle_incomplete_filters(text_input, LIST_COLUMNS_FILTER)
        elif intent_detected == "unknown":
            response_information = handle_unrelated_question(text_input, intent_detected)
        
        # *************** Update history
        history = save_chat_history(chat_history, text_input, response_information)
        print(f"\n\nhistory mid {history}")
         # *************** Topic creation
        if topic == "": 
            first_history = []
            for history_chat in chat_history[:2]:
                first_history.append(history_chat)
            topic_created = topic_creation(first_history)
        else: 
            topic_created = "Weather Topic"
        
        return response_information, history, topic_created

    except Exception as e:
        LOGGER.error(f"Error processing chat: {str(e)}")

# *************** Function to chain extract data 
def handle_extract_data(chat_history: List[dict]) -> List[dict]: 
    """
    Call the OpenWeather API to get the current weather data for multiple locations.

    Args:
        response (dict): The response from the OpenWeather API call.

    Returns:
        list: A list of responses from the OpenWeather API (one for each input).
    """
    # *************** Validate the filters
    # if not validate_string_input(response, 'response', False):
    #     LOGGER.error("'response' must be a string.")
    #     return [{"error": "'response' must be a non-empty list."}]
    
    prompt = prompt_extract_data()
    
    # *************** Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "chat_history": itemgetter('chat_history'),
                                }
                            )
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM() 
             )
    
    filter_response = chain.invoke(
                                    {
                                        "chat_history": chat_history
                                    }
                                )
    filter_response = json_clean_output(filter_response)
    return filter_response

# *************** Function to chain extract data 
def handle_response_inserted(response: str) -> str: 
    """
    Function to response after user intent to save the data

    Args:
        response (str): The response len succesful inserted into database

    Returns:
        str
    """
    # *************** Validate the filters
    if not validate_string_input(response, 'response'):
        LOGGER.error("'response' must be a string.")
        return [{"error": "'response' must be a non-empty list."}]
    
    prompt = prompt_response_insert_data()
    
    # *************** Setup Runnable Chain
    runnale_filter = RunnableParallel(
                                {
                                    "information_msg": itemgetter('information_msg'),
                                }
                            )
    chain = ( 
             runnale_filter | 
             prompt | 
             LLM() |
             StrOutputParser()
             )
    
    response_output = chain.invoke(
                                    {
                                        "information_msg": response
                                    }
                                )
    return response_output

if __name__ == "__main__":
    payload = { 
               "text_input": "i want to save the data",
               "chat_history": [{'type': 'human', 'content': 'i need weather condition in kuala lumpur'}, {'type': 'ai', 'content': '**Weather Analysis for Kuala Lumpur, Malaysia**\n\n- **Location:** Kuala Lumpur, Malaysia\n- **Coordinates:** Latitude 3.1431, Longitude 101.6865\n- **Current Weather:** Few clouds\n- **Temperature:** \n  - Current: 298.84 K (approx. 25.7°C)\n  - Feels Like: 299.61 K (approx. 26.5°C)\n  - Min: 298.02 K (approx. 25.9°C)\n  - Max: 299.4 K (approx. 26.3°C)\n- **Humidity:** 82%\n- **Pressure:** 1013 hPa\n- **Wind:** \n  - Speed: 0.51 m/s\n  - Direction: 0° (calm)\n- **Cloud Coverage:** 20% \n- **Visibility:** 10,000 meters\n- **Sunrise:** 06:00 AM (local time)\n- **Sunset:** 06:32 PM (local time)\n- **Timezone:** UTC+8\n\n**Summary of Weather Conditions:**\nKuala Lumpur is currently experiencing mild temperatures with a few clouds in the sky. The humidity is relatively high at 82%, which may contribute to a warmer feel. Wind conditions are calm with minimal movement. Overall, it is a pleasant evening, suitable for outdoor activities, with good visibility.'}],
               "topic": ""
               }
    response, history, topic = ask_to_chat(payload['text_input'], payload['chat_history'], payload['topic'])
    print(f"\n\nresponse: {response}")
    print(f"\n\history: {history}")
