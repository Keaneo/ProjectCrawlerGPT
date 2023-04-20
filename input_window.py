import tkinter as tk
from functionality import Functionality

class InfoWindow(tk.Tk):
    def __init__(self):
        self.func = Functionality()
        super().__init__()
        self.title("Crawler")
        self.geometry("700x300")
        self.maxsize(1200,1000)
        self.minsize(700,300)

        # Version selection
        self.version_var = tk.StringVar(self)
        version_frame = tk.Frame(self)
        version_frame.pack(pady=10)
        tk.Label(version_frame, text="Select version: ").pack(side=tk.TOP)
        gpt4radio = tk.Radiobutton(version_frame, text="GPT-4", variable=self.version_var, value="gpt-4")
        gpt4radio.select()
        gpt4radio.pack(side=tk.LEFT)
        tk.Radiobutton(version_frame, text="GPT-3.5", variable=self.version_var, value="gpt-3.5-turbo").pack(side=tk.LEFT)

        # Text input
        input_frame = tk.Frame(self)
        input_frame.pack(pady=5)
        tk.Label(input_frame, text="Enter your prompt: ").grid(row=0, column=0, sticky=tk.W)
        self.text_input = tk.Text(input_frame, height=5, width=80)
        self.text_input.grid(row=1, column=0, sticky=tk.NSEW)
        tk.Button(input_frame, text="Submit", command=self.submit).grid(row=2, column=0, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Clear Conversation", command=self.clear_conversation).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Clear Result", command=self.clear_result).pack(side=tk.LEFT, padx=10)
        
        # Reply
        reply_frame = tk.Frame(self)
        reply_frame.pack(pady=10)
        self.reply = tk.StringVar(self)
        self.reply_label = tk.Label(reply_frame, text='', wraplength=650)
        self.reply_label.pack(side=tk.BOTTOM, padx=10)

        self.protocol("WM_DELETE_WINDOW", self.cancel)


    def clear_conversation(self):
        #Read the 'conversation.txt' file and clear it
        with open('conversation.json', 'r+') as f:
            f.truncate(0)

    def clear_result(self):
        #Read the 'result.txt' file and clear it
        with open('responses.txt', 'r+') as f:
            f.truncate(0)

    def submit(self):
        version = self.version_var.get()
        text = self.text_input.get("1.0", tk.END)
        print(version, text)
        self.reply = self.func.submit_for_response(version, text)
        self.show_reply()

    def show_reply(self):
        self.reply_label.config(text=self.reply)
        self.update()


    def cancel(self):
        self.destroy()

if __name__ == "__main__":
    window = InfoWindow()
    window.mainloop()
