import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import soundfile as sf
import sounddevice as sd
import os
import pyttsx3

data, modified_data = None, None

def load_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        global data, samplerate
        data, samplerate = sf.read(filepath)
        check_audio_loaded()

def change_pitch(data, samplerate, pitch_factor):
    indices = np.arange(0, len(data), pitch_factor)
    return data[np.floor(indices).astype(int)]

def add_reverb(data, samplerate, reverb_amount):
    reverb_data = np.copy(data)
    decay, delay = reverb_amount / 10.0, int(0.03 * samplerate)
    for i in range(delay, len(data)):
        reverb_data[i] += decay * reverb_data[i - delay]
    return reverb_data

def add_echo(data, samplerate):
    echo_delay = int(0.1 * samplerate)
    echo_data = np.zeros_like(data)
    echo_data[echo_delay:] = data[:-echo_delay]
    return data + 0.5 * echo_data

def add_distortion(data, distortion_amount):
    return np.clip(data * distortion_amount, -1, 1)

def change_speed(data, speed_factor):
    indices = np.round(np.arange(0, len(data), speed_factor)).astype(int)
    return data[indices[indices < len(data)]]

def apply_effects():
    global modified_data
    if data is not None:
        pitch_factor, speed_factor = pitch_scale.get(), speed_scale.get()
        reverb_amount, distortion_amount = reverb_scale.get(), distortion_scale.get()

        modified_data = change_pitch(data, samplerate, pitch_factor)
        modified_data = change_speed(modified_data, speed_factor)
        if reverb_var.get(): modified_data = add_reverb(modified_data, samplerate, reverb_amount)
        if echo_var.get(): modified_data = add_echo(modified_data, samplerate)
        if distortion_var.get(): modified_data = add_distortion(modified_data, distortion_amount)

        modified_data *= volume_scale.get()

def apply_effects_and_play():
    apply_effects()
    if modified_data is not None:
        sd.play(modified_data, samplerate)

def save_file():
    apply_effects()
    if modified_data is not None:
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("FLAC files", "*.flac")])
        if save_path:
            sf.write(save_path, modified_data, samplerate)
            messagebox.showinfo("Success", "File saved successfully!")

def record_audio():
    global data, samplerate
    samplerate = 44100
    data = sd.rec(int(5 * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    check_audio_loaded()

def check_audio_loaded():
    save_button.config(state=tk.NORMAL if data is not None else tk.DISABLED)

def text_to_speech():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0 if voice_var.get() == "Male" else 1].id)
    text = text_entry.get("1.0", tk.END).strip()
    engine.save_to_file(text, 'temp_audio.wav')
    engine.runAndWait()
    global data, samplerate
    data, samplerate = sf.read('temp_audio.wav')
    check_audio_loaded()

root = tk.Tk()
root.title("Voice Changer")
root.iconbitmap('vc.ico' if os.path.exists('vc.ico') else 'default.ico')

reverb_var, echo_var, distortion_var = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
load_record_frame = tk.Frame(root)
load_record_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

load_button = tk.Button(load_record_frame, text="Load Audio File", command=load_file)
record_button = tk.Button(load_record_frame, text="Record Audio", command=record_audio)
text_to_speech_button = tk.Button(load_record_frame, text="Text to Speech", command=text_to_speech)

load_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
record_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
text_to_speech_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

text_entry = tk.Text(load_record_frame, height=5, width=30, wrap="word")
text_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

voice_var = tk.StringVar(value="Male")
voice_menu = tk.OptionMenu(load_record_frame, voice_var, "Male", "Female")
voice_menu.config(width=10)
voice_menu.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

pitch_speed_frame = tk.Frame(root)
pitch_speed_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
pitch_scale = tk.Scale(pitch_speed_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Pitch")
speed_scale = tk.Scale(pitch_speed_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Speed")
pitch_scale.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
speed_scale.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

reverb_frame = tk.Frame(root)
reverb_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
reverb_checkbox = tk.Checkbutton(reverb_frame, text="Add Reverb", variable=reverb_var)
reverb_scale = tk.Scale(reverb_frame, from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Reverb Amount")
reverb_checkbox.pack(side=tk.LEFT, anchor="w")
reverb_scale.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

echo_distortion_frame = tk.Frame(root)
echo_distortion_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
echo_checkbox = tk.Checkbutton(echo_distortion_frame, text="Add Echo", variable=echo_var)
distortion_checkbox = tk.Checkbutton(echo_distortion_frame, text="Add Distortion", variable=distortion_var)
echo_checkbox.pack(side=tk.LEFT, anchor="w")
distortion_checkbox.pack(side=tk.LEFT, anchor="w")

distortion_volume_frame = tk.Frame(root)
distortion_volume_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
distortion_scale = tk.Scale(distortion_volume_frame, from_=1, to=10, resolution=0.1, orient=tk.HORIZONTAL, label="Distortion Amount")
volume_scale = tk.Scale(distortion_volume_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Volume")
volume_scale.set(1.0)
distortion_scale.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
volume_scale.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

play_button = tk.Button(root, text="Apply Effects and Play", command=apply_effects_and_play)
save_button = tk.Button(root, text="Save File", command=save_file)
credit_label = tk.Label(root, text="Made by Washer", font=("Arial", 10))
play_button.grid(row=5, column=0, pady=10, padx=10, sticky="ew")
save_button.grid(row=6, column=0, pady=10, padx=10, sticky="ew")
save_button.config(state=tk.DISABLED)
credit_label.grid(row=7, column=0, pady=10, padx=10, sticky="ew")

root.mainloop()
