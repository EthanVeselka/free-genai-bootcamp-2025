from groq import Groq
import json
from duckduckgo_search import DDGS
# Initialize the Groq client 
from dotenv import load_dotenv
import os
import requests
from html2text import HTML2Text
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import argparse

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Initialize Groq client
client = Groq(
    api_key=groq_api_key
)

# Initialize DDGS with a persistent session
ddgs = DDGS(timeout=60)  # Increase timeout and keep session persistent

# Define models
ROUTING_MODEL = "llama-3.3-70b-versatile"
TOOL_USE_MODEL = "llama-3.3-70b-versatile"
GENERAL_MODEL = "llama-3.3-70b-versatile"
JAPANESE_MODEL = "mixtral-8x7b-32768"  # Use Mixtral for Japanese kanji enhancement

# Initialize request counter
ddgs_request_count = 0

def search_web(query):
    """Tool to search the web"""
    global ddgs_request_count
    max_retries = 1
    base_delay = 5
    
    print(f"\n=== Search Web Called ===")
    print(f"Query: {query}")
    
    for attempt in range(max_retries):
        try:
            ddgs_request_count += 1
            print(f"Making DDGS request #{ddgs_request_count} (Attempt {attempt + 1}/{max_retries})")
            
            # Use the persistent DDGS instance
            results = ddgs.text(
                query,
                max_results=5,
                backend="lite"  # Use lite backend which is more reliable
            )
            
            if results:
                print(f"Search successful! Found {len(list(results))} results")
                formatted_results = [
                    {
                        "title": result["title"],
                        "url": result["href"]
                    }
                    for result in results
                ]
                print(f"First result: {formatted_results[0] if formatted_results else 'None'}")
                return formatted_results
            print("Search returned no results")
            return []
            
        except Exception as e:
            print(f"Search attempt {attempt + 1} failed with error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if attempt == max_retries - 1:
                print("All search attempts failed. Returning empty results.")
                return []

# Tool 1
def get_page_content(url):
    """Tool to get the content of a page"""
    response = requests.get(url)
    h = HTML2Text()
    h.ignore_links = False
    content = h.handle(response.text)
    return content[:5000] if len(content) > 5000 else content

# Tool 2
def extract_vocabulary(text):
    """Tool to extract vocabulary from a text"""
    words = set(text.lower().split())
    vocabulary = [word for word in words if word.isalpha()]
    return sorted(vocabulary)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_groq_call(messages, model, **kwargs):
    """Make a Groq API call with retry logic"""
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
    except Exception as e:
        error_str = str(e)
        if "tool_use_failed" in error_str:
            # Extract just the error message without the function call details
            error_msg = error_str.split("failed_generation")[0].strip()
            print(f"Error calling Groq API: {error_msg}")
        else:
            print(f"Error calling Groq API: {error_str}")
        raise

def route_query(query):
    """Routing logic to let LLM decide if tools are needed"""
    routing_prompt = f"""
    Given the following instructions, determine if any tools are needed to complete it.
    Available tools:
    1. search_web - Search the web for information
    2. get_page_content - Get content from a webpage URL
    3. extract_vocabulary - Extract vocabulary words from text
    
    
    If a tool is needed, respond with 'TOOL: [TOOL_NAME]'.
    If no tools are needed, respond with 'NO TOOL'.

    User query: {query}

    Response:
    """
    
    response = make_groq_call(
        messages=[
            {
                "role": "system", 
                "content": """You are a routing assistant. Your main task is to determine which tool to use next."""
            },
            {"role": "user", "content": routing_prompt}
        ],
        model=ROUTING_MODEL,
        max_completion_tokens=20
    )
    
    routing_decision = response.choices[0].message.content.strip().upper()
    print(f"\nRouting decision: {routing_decision}")
    
    # # Force search_web for song-related queries if not explicitly routed elsewhere
    # if "SONG" in query.upper() and "LYRICS" not in routing_decision:
    #     print("Query contains 'song' - forcing search_web route")
    #     return "search_web"
    
    if "TOOL: SEARCH_WEB" in routing_decision:
        return "search_web"
    elif "TOOL: GET_PAGE_CONTENT" in routing_decision:
        return "get_page_content"
    elif "TOOL: EXTRACT_VOCABULARY" in routing_decision:
        return "extract_vocabulary"
    else:
        return "no tool needed"

def run_with_tool(query):
    """Use the tool use model to perform operations with available tools"""
    messages = [
        {
            "role": "system",
            "content": """You are a language learning assistant agent specialized in analyzing song lyrics and generating vocabulary lists.
You have access to these tools:
1. search_web - Use this first to find the song lyrics
2. get_page_content - Use this to extract the actual lyrics from the url found with search_web
3. extract_vocabulary - Use this to get a basic list of words from the lyrics

Important:
1. Follow the given instructions and use the tools to complete the task.
2. DO NOT generate your own url in the get_page_content tool call, only use the ones provided by the results of the search_web tool.
3. Use the messages context to determine if you have already used a tool succesfully, so you do not repeat it, if a tool call fails 
or produces empty outoput, you will need to try again.
  ```""",
        },
        {
            "role": "user",
            "content": query,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        }
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_page_content",
                "description": "Get content from a webpage URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the webpage",
                        }
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "extract_vocabulary",
                "description": "Extract vocabulary words from text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to extract vocabulary from",
                        }
                    },
                    "required": ["text"],
                },
            },
        }
    ]
    
    max_turns = 5
    turn = 0
    has_used_tool = False
    
    while turn < max_turns:
        turn += 1
        print(f"\nTurn {turn}")
        try:
            response = make_groq_call(
                messages=messages,
                model=TOOL_USE_MODEL,
                tools=tools,
                tool_choice="auto",
                max_completion_tokens=4096
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                messages.append(response_message)
                break
            
            print(f"Tool calls: {[tool_call.function.name for tool_call in tool_calls]}")
            
            messages.append(response_message)
            for tool_call in tool_calls:
                print(f"Tool call: {tool_call.function.name}")
                try:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_web":
                        function_response = json.dumps(search_web(function_args.get("query")))
                        # print(f"Function response: {function_response}")
                    elif function_name == "get_page_content":
                        function_response = get_page_content(function_args.get("url"))
                    elif function_name == "extract_vocabulary":
                        function_response = json.dumps(extract_vocabulary(function_args.get("text")))
                    # has_used_tool = True
                    
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                except Exception as e:
                    error_message = f"Tool {function_name} failed: {str(e)}"
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps({"error": error_message}),
                        }
                    )
                    break
                    
        except Exception as e:
            if "tool_use_failed" in str(e):
                # Extract error message without the function call details
                error_msg = str(e).split("failed_generation")[0].strip()
                messages.append(
                    {
                        "role": "system",
                        "content": f"Tool use error: {error_msg}. Please try again."
                    }
                )
                continue
            else:
                raise
    
    return response_message.content

def run_general(query):
    """Use the general model to answer the query since no tool is needed"""
    response = make_groq_call(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        model=GENERAL_MODEL
    )
    return response.choices[0].message.content

def process_query(query):
    """Process a query using the appropriate model and route"""
    # Determine the route
    route = route_query(query)
    
    # Check if this is a Japanese song query
    is_japanese = "japanese" in query.lower()
    
    try:
        # First step: Use tool calls to get the lyrics and initial vocabulary
        if route in ["search_web", "get_page_content", "extract_vocabulary"]:
            # Get lyrics and initial vocabulary using tool calls with Llama
            tool_response = run_with_tool(query)
            
            # For Japanese songs, enhance the vocabulary with Mixtral for better kanji support
            if is_japanese:
                print("Japanese song detected. Using Mixtral to enhance vocabulary with kanji...")
                
                # Pass the Llama output to Mixtral for enhancement
                mixtral_query = f"""
                I have a vocabulary list for a Japanese song that is missing the correct kanji in the "kanji" sections and is not proprly formatted.
                
                Here is the current list:
                {tool_response}
                
                Please correct this vocabulary list by adding proper kanji characters to all 'kanji' sections where kanji are missing
                
                Important:
                1. DO NOT change the rest of the json structure, only the words within each category
                2. Only modify/add kanji to the "kanji" sections where kanji are missing
                3. Respond with only the updated json structure, no other text
                
                Each vocabulary element should be formatted like this:
                {{
                    "kanji": "偉い",
                    "romaji": "erai",
                    "english": "great",
                    "parts": [
                        {{ "kanji": "偉", "romaji": ["e","ra"] }},
                        {{ "kanji": "い", "romaji": ["i"] }}
                    ]
                }}
                
                """
                
                enhanced_response = make_groq_call(
                    messages=[
                        {"role": "system", "content": "You are a Japanese language expert. Your task is to enhance vocabulary lists with proper kanji characters while maintaining the original JSON structure."},
                        {"role": "user", "content": mixtral_query}
                    ],
                    model=JAPANESE_MODEL
                )
                
                return {
                    "route": "LLAMA+MIXTRAL",
                    "response": enhanced_response.choices[0].message.content
                }
            else:
                # For non-Japanese songs, just return the tool response
                return {
                    "route": route,
                    "response": tool_response
                }
        else:
            # No tools needed, use general model
            response = run_general(query)
            return {
                "route": "GENERAL",
                "response": response
            }
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        # Fallback to direct approach without tool use
        print("Falling back to direct approach without tool use...")
        try:
            fallback_response = run_general(f"I need to generate a vocabulary list for the song lyrics: {query}. Please do your best to find information about this song and create a vocabulary list in JSON format.")
            return {
                "route": "FALLBACK",
                "response": fallback_response
            }
        except Exception as fallback_e:
            print(f"Fallback also failed: {str(fallback_e)}")
            return {
                "route": "ERROR",
                "response": f"Failed to process query. Error: {str(e)}. Fallback error: {str(fallback_e)}"
            }

def read_prompt_file():
    """Read and parse the prompt.md file"""
    with open('prompt.md', 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":
    # Reset counter at start
    ddgs_request_count = 0
    
    parser = argparse.ArgumentParser(description='Extract vocabulary from song lyrics')
    parser.add_argument('--song', required=True, help='Name of the song')
    parser.add_argument('--artist', help='Name of the artist (optional)')
    parser.add_argument('--language', required=True, help='Language of the song')
    parser.add_argument('--output', default='output.json', help='Output JSON file path (default: output.json)')
    
    args = parser.parse_args()
    prompt = read_prompt_file()
    search_query = f"Song: {args.song} Language: {args.language}"
    
    # Create the query
    query = f"""For this song: {search_query} , follow these instructions: {prompt}"""
    
    # Process the query
    result = process_query(query)
    
    try:
        # Parse the response as JSON if it's a string
        if isinstance(result['response'], str):
            # Handle markdown-style JSON formatting
            response_text = result['response']
            if '```json' in response_text and '```' in response_text:
                # Extract content between ```json and ```
                json_content = response_text.split('```json')[1].split('```')[0].strip()
                response_data = json.loads(json_content)
            else:
                # Try parsing as regular JSON
                response_data = json.loads(response_text)
        else:
            response_data = result['response']
            
        # Save the JSON response to file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {args.output}")
        
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse response as JSON. Saving raw response to output.txt")
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(result['response'])
