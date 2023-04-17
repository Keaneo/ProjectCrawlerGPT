import openai
from spinner import Spinner
import os
import tkinter as tk
from tkinter import filedialog
from pprint import pprint
import json
import token_counter

openai.api_key = os.environ.get('GPT4API')
openai.organization = os.environ.get('OPENAI_ORG')

def get_folder_path():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory()
    return folder_path

def get_reply(messages):
    with Spinner("Generating response..."):
        response = openai.ChatCompletion.create(
            model = "gpt-4",            
            messages= messages
        )
        return response

messages_to_send = [
    {"role": "system", "content": """
        Youre an AI designed to crawl the file system of a development project.
        You'll be given the contents of many files (one at a time) and the file extension if it's a binary file (e.g .obj, .jpeg, etc.).
        You'll need to determine the file type of each file.
        After each file, respond with only a brief description of what it is. If it contains code, summarise the purpose and make a list of the function names.
        Once all have been provided, you'll then be asked a question on the project as a whole and you'll need to answer it. This may involve writing multiple new files.
        Reply with the simplest text answer you can, or if you're writing code, only include the code and no additional text (unless the code needs environmental changes in order to work).
    """}
]

#Crawl a folder and get the contents of each file
def crawl_folder(folder):
    extensions = (".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".yml", ".yaml", ".xml", ".csv", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".dart", ".scala", ".sh", ".b", ".m")
    for file in os.listdir(folder):
        if any(file.endswith(ext) for ext in extensions):
            with open(os.path.join(folder, file), "r", encoding='utf-8') as f:
                messages_to_send.append({"role": "user", "content": f.read()})

if not os.path.exists("conversation.json"):
    with open("conversation.json", 'w', encoding='utf-8') as outfile:
        json.dump({}, outfile)

with open("conversation.json", "r", encoding='utf-8') as f:
    try:
        past_messages = json.loads(f.read())
    except (json.decoder.JSONDecodeError, ValueError) as e:
        pprint(e)
        past_messages = []


if len(past_messages) == 0:
    crawl_folder(get_folder_path())
    # with open("conversation.json", "w") as f:
    #     f.write(json.dumps(messages_to_send)[:-1] + ',')
else:
    messages_to_send.extend(past_messages)

messages_to_send = [obj for obj in messages_to_send if obj]

user_prompt = {"role": "user", "content": str(input("Ask your question about this project: "))}

messages_to_send.append(user_prompt)

if messages_to_send[1]["role"] == "system":
    messages_to_send = messages_to_send[1:]

for obj in messages_to_send:
    for key, value in obj.items():
        if isinstance(value, str):
            if key == "content":
                value = value.replace("'", "\\'")
            messages_to_send[messages_to_send.index(obj)][key] = value

#Record messages
with open("conversation.json", "w+", encoding='utf-8') as f:
    f.write('\n')
    f.write(json.dumps(messages_to_send, ensure_ascii=False)[:-1] + ',')

print(token_counter.count_message_tokens(messages_to_send))

response = get_reply(messages_to_send)

# Extract and print the assistant's reply
assistant_reply = response.choices[0]
print('Response: ')
print(assistant_reply.message['content'] + '\n')

with open("responses.txt", "a+", encoding='utf-8') as f:
    f.write('Question: ' + user_prompt['content'] + '\n')
    f.write('Answer: \n\n' + assistant_reply.message['content'] + '\n\n\n')

#Append the assistant's reply to the conversation
with open("conversation.json", "a+", encoding='utf-8') as f:
    f.write('\n')
    f.write(json.dumps(assistant_reply.message, ensure_ascii=False) + ']')