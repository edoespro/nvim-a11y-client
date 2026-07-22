from tts import speak
from connection import NvimConnection

class NvimMode:

    def __init__(self, name):
        self._name = name
        #print(f"Clase Modo: {self._name}")

    def process_key(self, event):
        #print(f"En mode_papa.process_key: {event}")
        tipo = event[0]
        
        #print(f"{key_name}")
        if tipo == "ESPECIAL":
            key_str = event[1]
            if key_str == "<Down>" or key_str == "<Up>":
                speak(f"{NvimConnection().nvim.current.line}")
            #print(f"line_ {key_name}")
            elif key_str == "<Left>" or key_str =="<Right>":
                row, col = NvimConnection().nvim.api.win_get_cursor(NvimConnection().nvim.current.window.handle)
                caracter = NvimConnection().nvim.api.buf_get_text(NvimConnection().nvim.current.buffer.number, row-1, col, row-1, col + 1, {})
                print(f"{caracter}")
                if caracter[0] == ' ':
                    speak("ESPACIO")
                elif caracter[0] == '':
                    speak("FIN DE LINEA")
                else:
                    speak(f"{caracter[0]}")
                #print(f"char: {caracter}")

        elif tipo == "MODIFICADOR":
            info = event[1]
            tecla_base = info["tecla_base"]
            #print("modificador 1")
            if tecla_base == "Left" or tecla_base == "Right" and info["control"] == True  and info["alt"]== False and info["shift"] == False:
                #Esta es la forma más sencilla si la ventana está enfocada
                palabra = NvimConnection().nvim.eval('expand("<cword>")')
                speak(palabra)
                print(palabra)
















