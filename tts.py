import subprocess

# Declaramos la variable global para el proceso
_tts_process = None

def speak(text):
    global _tts_process
    
    # Inicializa el proceso solo la primera vez que se llama
    if _tts_process is None or _tts_process.poll() is not None:
        _tts_process = subprocess.Popen(
            ["termux-tts-speak"],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True # Permite enviar strings directamente en lugar de bytes
        )
    
    try:
        # Enviamos el texto al flujo de entrada y forzamos la salida imediata
        #print("speak 1")
        _tts_process.stdin.write(text + "\n")
        _tts_process.stdin.flush()
        #print("speak 3")
    except Exception:
        # Si el proceso se rompió por optimización de Android, lo reiniciamos
        _tts_process = None



#import subprocess


#def speak(text):
 #   subprocess.run(["termux-tts-speak", text])



def write(text):
    with open('/data/data/com.termux/files/home/.tts_queue', 'w') as f:
        f.write(text + '\n')













