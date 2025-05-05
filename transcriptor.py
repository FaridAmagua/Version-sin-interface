import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
from pydub import AudioSegment
import requests
import time

# Archivo para guardar la API key
KEY_FILE = "api_key.json"

# Convierte un archivo MP4 a WAV
def convertir_video_a_wav():
    ruta_video = filedialog.askopenfilename(filetypes=[("Archivos MP4", "*.mp4")])
    if not ruta_video:
        return

    try:
        audio = AudioSegment.from_file(ruta_video, format="mp4")
        ruta_wav = os.path.splitext(ruta_video)[0] + ".wav"
        audio.export(ruta_wav, format="wav")
        messagebox.showinfo("Conversión completa", f"Audio convertido a WAV:\n{ruta_wav}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir el video:\n{e}")

# Guarda la API key en un archivo local
def guardar_api_key():
    clave = api_key_entry.get()
    if not clave:
        messagebox.showwarning("Falta API key", "Introduce una API key válida.")
        return
    with open(KEY_FILE, "w") as f:
        json.dump({"api_key": clave}, f)
    messagebox.showinfo("Guardado", "API Key guardada correctamente.")

# Carga la API key
def cargar_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
            return data.get("api_key")
    return None

# Transcribe el audio usando AssemblyAI
def transcribir_audio():
    ruta_audio = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.wav *.mp3")])
    if not ruta_audio:
        return

    api_key = cargar_api_key()
    if not api_key:
        messagebox.showerror("Error", "No se encontró una API key guardada.")
        return

    try:
        with open(ruta_audio, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers={"authorization": api_key},
                data=f
            )

        upload_url = upload_response.json()["upload_url"]

        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={"authorization": api_key},
            json={"audio_url": upload_url, "language_code": "es"}
        )

        transcript_id = transcript_response.json()["id"]
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

        while True:
            polling_response = requests.get(polling_url, headers={"authorization": api_key})
            status = polling_response.json()["status"]

            if status == "completed":
                texto = polling_response.json()["text"]
                with open("transcripcion.txt", "w", encoding="utf-8") as f:
                    f.write(texto)
                messagebox.showinfo("Listo", "Transcripción completada. Guardada como 'transcripcion.txt'")
                break
            elif status == "error":
                messagebox.showerror("Error", f"Transcripción fallida: {polling_response.json()['error']}")
                break
            else:
                time.sleep(3)

    except Exception as e:
        messagebox.showerror("Error inesperado", str(e))

# Interfaz de usuario
root = tk.Tk()
root.title("Transcriptor AssemblyAI")

btn_convertir = tk.Button(root, text="1. Convertir MP4 a WAV", command=convertir_video_a_wav)
btn_convertir.pack(pady=10)

tk.Label(root, text="2. Introduce tu API Key:").pack()
api_key_entry = tk.Entry(root, width=50, show="*")
api_key_entry.pack()

btn_guardar_key = tk.Button(root, text="Guardar API Key", command=guardar_api_key)
btn_guardar_key.pack(pady=5)

btn_transcribir = tk.Button(root, text="3. Transcribir Audio", command=transcribir_audio)
btn_transcribir.pack(pady=15)

root.mainloop()
