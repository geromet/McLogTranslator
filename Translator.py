import time
import requests
import json
import tkinter as tk
from tkinter import scrolledtext
from tkinter import Entry
from threading import Thread
import subprocess

log_file_location = "/root/.minecraft/logs/latest.log"
use_google_translate = True

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def translate_text(text, target_language="en"):
    if use_google_translate:
        return translate_text_google(text, target_language)
    else:
        return translate_text_self_hosted(text, target_language)

def translate_text_self_hosted(text, target_language="en"):
    payload = {
        "q": text,
        "source": "auto",
        "target": target_language
    }
    headers = {
        "Content-Type": "application/json"
    }
    url = "http://0.0.0.0:5000/translate"
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['translatedText']
    else:
        return f"Translation request failed with status code: {response.status_code}"

def reverse_translate_text():
    time.sleep(3)
    cut_text = subprocess.run(['xclip', '-o', '-selection', 'clipboard'], stdout=subprocess.PIPE, text=True)
    translated_text = translate_text_google(cut_text, "RU")
    subprocess.run(['echo', '-n', translated_text.strip(), '|', 'xclip', '-selection', 'clipboard'], text=True, shell=True)
    subprocess.run(['xclip', '-selection', 'clipboard'], text=True, input='')

def start_reading():
    global log_file_location
    tail_process = subprocess.Popen(['tail', '-f', log_file_location], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in tail_process.stdout:
        if "CHAT" in line:
            if not "Welcome" in line:
                root.after(1, display_translation, line)
def reverse_translate_text():
    input_text = input_text_box.get()  # Get text from the input_text_box
    translated_text = translate_text(input_text, "RU")
    input_text_box.config(state="normal")
    output_text_box.config(state="normal")
    output_text_box.delete(1.0, tk.END)  # Clear the output_text_box
    output_text_box.insert(tk.END, translated_text)  # Insert translated text
    input_text_box.delete(0, tk.END)
    output_text_box.config(state="disabled")
def display_translation(line):
    original_text.config(state="normal")
    translation_text.config(state="normal")
    original = line.split("[CHAT]")[1:]
    extract_username = original[0].split(">")
    username = extract_username[0][2:]
    text_to_translate = extract_username[1:]
    listToStr = ' '.join([str(elem) for i, elem in enumerate(text_to_translate)])
    text_to_translate = listToStr.translate({ord(c): None for c in "'[]:"}).split("/n")[0][1:]
    translated = translate_text(text_to_translate)
    original_text.insert("end", f"{username}: ", 'username')
    translation_text.insert("end", f"{username}: ", 'username')
    original_text.insert("end", f"{text_to_translate}")
    translation_text.insert("end", f"{translated}\n")
    original_text.tag_config('username', foreground='green')
    translation_text.tag_config('username', foreground='green')
    original_text.see("end")
    translation_text.see("end")
    original_text.config(state="disabled")
    translation_text.config(state="disabled")

def create_settings_window():
    global log_file_location
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    log_label = tk.Label(settings_window, text="Log File Location:")
    log_label.pack()
    log_entry = tk.Entry(settings_window)
    log_entry.insert(0, log_file_location)
    log_entry.pack()

    def save_settings():
        global log_file_location
        log_file_location = log_entry.get()
        save_settings_to_file()
        settings_window.destroy()

    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack()

def translate_text_google(text, target_language="en"):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target_language,
        "dt": "t",
        "q": text,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        first_translated_text = data[0][0][0]
        try:
            second_translated_text = data[0][1][0]
            try:
                third_translated_text = data[0][2][0]
                try:
                    fourth_translated_text = data[0][3][0]
                    translated_text = f"{first_translated_text} {second_translated_text} {third_translated_text}{fourth_translated_text}"
                except IndexError:
                    translated_text = f"{first_translated_text} {second_translated_text} {third_translated_text}"
            except IndexError:
                translated_text = f"{first_translated_text} {second_translated_text}"
        except IndexError:
            translated_text = first_translated_text
        return translated_text
    else:
        return f"Translation request failed with status code: {response.status_code}"

def save_settings_to_file():
    with open("settings.txt", "w") as file:
        file.write(f"Log File Location: {log_file_location}\n")

def load_settings_from_file():
    global log_file_location
    global api_key
    global use_google_translate
    try:
        with open("settings.txt", "r") as file:
            for line in file:
                if line.startswith("Log File Location: "):
                    log_file_location = line.split("Log File Location: ")[1].strip()
    except FileNotFoundError:
        pass

root = tk.Tk()
root.title("Minecraft Chat Translation")
load_settings_from_file()

title_bar = tk.Frame(root, bg="gray")
title_bar.pack(fill=tk.X, side=tk.TOP)

settings_button = tk.Button(title_bar, text="Settings", command=create_settings_window)
settings_button.pack(side=tk.RIGHT)

# Create and place the ScrolledText widgets in a Frame using grid
text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True)

original_text = scrolledtext.ScrolledText(text_frame, state="disabled", wrap="word", width=40, height=20)
original_text.grid(row=0, column=0, sticky="nsew")

translation_text = scrolledtext.ScrolledText(text_frame, state="disabled", wrap="word", width=40, height=20)
translation_text.grid(row=0, column=1, sticky="nsew")
input_text_box = Entry(root, width=40)
input_text_box.pack(fill=tk.X)
input_text_box.insert(0, "")
translate_button = tk.Button(root, text="Translate", command=reverse_translate_text)
translate_button.pack()
# Add an output text box to display translations
output_text_box = scrolledtext.ScrolledText(root, state="disabled", wrap="word", width=40, height=5)
output_text_box.pack(fill=tk.X)
# Configure row and column weights to make them expand
text_frame.columnconfigure(0, weight=1)
text_frame.columnconfigure(1, weight=1)
text_frame.rowconfigure(0, weight=1)

Thread(target=start_reading).start()
root.mainloop()
