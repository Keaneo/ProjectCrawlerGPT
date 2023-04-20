#Imports
import openai
from spinner import Spinner
import os
import tkinter as tk
from tkinter import filedialog
from pprint import pprint
import json
import token_counter
from yes_no_dialog import yes_no_dialog

#====================================================================================================
#=======================================CONFIGURATION===============================================
#====================================================================================================

class Functionality:
    def __init__(self) -> None:
        

        #Set the API key and organization ID
        openai.api_key = os.environ.get('GPT4API')
        openai.organization = os.environ.get('OPENAI_ORG')

        self.messages_to_send = []

        #System Prompt
        #This gives the AI a brief description of what it's supposed to do
        #Not used by GPT-3 - but we have 3.5 now!
        self.system_prompt = {
            "role": "system", "content": """
                Youre an AI designed to crawl the file system of a development project.
                You'll be given the contents of many files (one at a time) and the file extension if it's a binary file (e.g .obj, .jpeg, etc.).
                You'll need to determine the file type of each file.
                After each file, respond with only a brief description of what it is. If it contains code, summarise the purpose and make a list of the function names.
                Once all have been provided, you'll then be asked a question on the project as a whole and you'll need to answer it. This may involve writing multiple new files.
                Reply with the simplest text answer you can.

                IMPORTANT INFORMATION FOR YOUR RESPONSES:
                If you reply with a new code file, reply in this format:
                \{code\}
                \{filenameextension\}
                [THE CODE]

                If you are asked to reply with anything other than just code, reply in this format:
                \{textfile\}
                [THE TEXT]
            """
        }

        #Create the conversation file if it doesn't exist
        if not os.path.exists("conversation.json"):
            with open("conversation.json", 'w', encoding='utf-8') as outfile:
                json.dump({}, outfile)

        #Load the past messages
        with open("conversation.json", "r", encoding='utf-8') as f:
            try:
                self.past_messages = json.loads(f.read())
            except (json.decoder.JSONDecodeError, ValueError) as e:
                pprint(e)
                self.past_messages = []

        #If there are no past messages, crawl the folder
        #Otherwise continue from the past conversation
        if len(self.past_messages) == 0:
            self.crawl_folder(self.get_folder_path())
        else:
            self.messages_to_send.extend(self.past_messages)

    #====================================================================================================
    #=======================================FUNCTIONS====================================================
    #====================================================================================================

    #Get the path of a folder from the user
    def get_folder_path(self):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        folder_path = filedialog.askdirectory()
        return folder_path

    # def pick_gpt_version(self, title, message, yes_text='Yes', no_text='No'):
    #     result = yes_no_dialog(title, message, yes_text, no_text)
    #     return result

    #Send the messages to the API and get a response
    def get_reply(self, messages, model = "gpt-4"):
        with Spinner("Generating response..."):
            response = openai.ChatCompletion.create(
                model = model,            
                messages= messages
            )
            return response
        
    #Crawl a folder and get the contents of each file
    #Note: Tried to exclude config files if this project was used to test this script
    #Kinda not amazing practice? Should probably check relative file path or something
    def crawl_folder(self, folder):
        extensions = (".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".yml", ".yaml", ".xml", ".csv", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".dart", ".scala", ".sh", ".b", ".m",
                    ".r", ".s", ".asm", ".sql", ".ino")
        excluded = ("conversation.json", "responses.txt")
        for file in os.listdir(folder):
            #exclude the conversation file and responses file
            if any(file.endswith(ext) for ext in extensions):
                #If filepath is the folder of this script and the name is not in the excluded list
                if not any(os.path.join(folder, file) == os.path.join(os.getcwd(), name) for name in excluded):
                    with open(os.path.join(folder, file), "r", encoding='utf-8') as f:
                        self.messages_to_send.append({"role": "user", "content": f.read()})

    def submit_for_response(self, model = "gpt-4", user_prompt = "Summarize this in 10 words or less"):
        #Set the system prompt
        self.messages_to_send.append(self.system_prompt)

        #Remove any empty messages
        self.messages_to_send = [obj for obj in self.messages_to_send if obj]

        #Ask the user a question
        user_prompt = {"role": "user", "content": str(user_prompt)}

        #Add the user prompt to the messages to send
        self.messages_to_send.append(user_prompt)

        #Remove the system prompt if it's the first message
        #This prevents there from being two identical system prompts
        #Read: Due to data management and coding practice lol
        if self.messages_to_send[1]["role"] == "system":
            self.messages_to_send = self.messages_to_send[1:]

        #Record messages
        with open("conversation.json", "w+", encoding='utf-8') as f:
            f.write('\n')
            f.write(json.dumps(self.messages_to_send, ensure_ascii=False)[:-1] + ',')

        #Tell the user how many tokens the message will use
        print("Tokens for this message: " + str(token_counter.count_message_tokens(self.messages_to_send, model=model)))

        #Get the response
        response = self.get_reply(self.messages_to_send)

        # Extract and print the assistant's reply
        assistant_reply = response.choices[0]
        print('Response: ')
        print(assistant_reply.message['content'] + '\n')

        #Record responses
        with open("responses.txt", "a+", encoding='utf-8') as f:
            f.write('Question: ' + user_prompt['content'] + '\n')
            f.write('Answer: \n\n' + assistant_reply.message['content'] + '\n\n\n')

        #If the response is a code snippet, print the file extension
        if assistant_reply.message['content'].partition('\n')[0] == f'{{code}}':
            if len(assistant_reply.message['content'].splitlines()) > 1:
                print("code" + assistant_reply.message['content'].splitlines()[1][2:-2])

        #If the response is a code snippet, save it to a file
        #And if the response is a text file, save it to a text file
        if assistant_reply.message['content'].partition('\n')[0] == f'{{code}}':
            with open("code" + assistant_reply.message['content'].splitlines()[1][1:-1], "w+", encoding='utf-8') as f:
                f.write(assistant_reply.message['content'].partition('\n')[2] + '\n')
        elif assistant_reply.message['content'].partition('\n')[0] == f'{{textfile}}':
            with open("textfile.txt", "w+", encoding='utf-8') as f:
                f.write(assistant_reply.message['content'].partition('\n')[1] + '\n')

        #Append the assistant's reply to the conversation & save it
        with open("conversation.json", "a+", encoding='utf-8') as f:
            f.write('\n')
            f.write(json.dumps(assistant_reply.message, ensure_ascii=False) + ']')
        
        return assistant_reply.message['content']