from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

#load Env values
env_vars = dotenv_values(".env")

#Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")

Assistantname = env_vars.get("Assistantname")

GroqAPIKey = env_vars.get("GroqAPIKey")

#Initialize the Gron client with the provided API key.

client = Groq(api_key=GroqAPIKey)

#Define the system instructions for the chatbot.

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


#Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:       
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

#Function to perform a Google search and format the results.
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        
    Answer += "[end]"
    return Answer


def AnswerModifier (Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#Predefined chatbot conversation system message and an initial user message.

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]    


def Information():
    data=""
    current_date_time =datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

#Function to handle real-time search and response generation.

def RealtimeSearchEngine (prompt):
    global SystemChatBot, messages
    
    #load chat log from json
    with open(r"Data\ChatLog.json", "r") as f:        
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    #Add Google search results to the system chatbot messages.
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    #Generate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages = SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    ) 
    
    
    Answer = ""
    
    #response chunk from streaming output
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    
    #clean up the response
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})
    
    
    #save the updated back log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
        
    #remove chatbot conversation
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

#main file
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query:")
        print(RealtimeSearchEngine(prompt))
    
           