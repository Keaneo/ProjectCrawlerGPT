import tkinter as tk

def yes_no_dialog(title, message, yes_text='Yes', no_text='No'):  
    def on_version_one_click():
        dialog.grab_release()
        dialog.destroy()
        return_value.set(False)

    def on_version_two_click():
        dialog.grab_release()
        dialog.destroy()
        return_value.set(True)

    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.grab_set()

    return_value = tk.BooleanVar(dialog)

    message_label = tk.Label(dialog, text=message)
    message_label.pack(padx=20, pady=10)

    version_one_button = tk.Button(dialog, text=no_text, command=on_version_one_click)
    version_one_button.pack(fill=tk.X, padx=20, pady=5)

    version_two_button = tk.Button(dialog, text=yes_text, command=on_version_two_click)
    version_two_button.pack(fill=tk.X, padx=20, pady=5)

    root.wait_window(dialog)

    root.update()

    return return_value.get()

