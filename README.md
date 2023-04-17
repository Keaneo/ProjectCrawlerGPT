# ProjectCrawlerGPT

A simple GPT-4 API caller with very basic conversational memory.
Asks for a folder, searches for code & text files, feeds them to GPT-4 along with a user prompt.
The goal here is to understand all the scripts you've written and give GPT-4 the ability to help you write more or document the project.
This saves time when trying to feed information into the Web UI version of ChatGPT, while retaining all the same features.

The only caveat is that this isn't free - and requires GPT-4 API access for now.
This isn't cheap either given the volume of tokens you need to pass to the API each time you run the script, this could very quickly hit the token limit.
