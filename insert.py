from mode import NvimMode
from tts import speak
from connection import NvimConnection

class Insert(NvimMode):

    def __init__(self):
        super().__init__("Insert")
        #print("Clase hija Insert")
        self.nvim = NvimConnection().nvim

    def process_key(self, event):
        super().process_key(event)
        #print(event)
        tipo = event[0]
        if tipo == "SIMPLE":
            speak(event[1])
        elif tipo == 'ESPECIAL':
            key_str = event[1]
            #print(key_str)
            if key_str == "<BS>":
                self.on_backspace()
            elif key_str == "<Space>":
                speak("Espacio")
        elif tipo == "MODIFICADOR":
            pass
            #info = event[1]
            #tecla_base = info["tecla_base"]
            #if tecla_base == "Left" or tecla_base == "Right" and info["control"] == True  and info["alt"]== False and info["shift"] == False:
                #Esta es la forma más sencilla si la ventana está enfocada
                #palabra = NvimConnection().nvim.eval('expand("<cword>")')
                #speak(palabra)


    def on_backspace(self):
        # Obtener el carácter que se va a borrar
        try:
            row, col = self.nvim.api.win_get_cursor(self.nvim.current.window.handle)
            # curcol - 1 porque el cursor está después del carácter a borrar
            deleted_char = self.nvim.api.buf_get_text(self.nvim.current.buffer.number, row-1, col, row-1, col+1, {})
            speak(f"borrado {deleted_char}")
        except Exception as e:
            speak(f"Excepcion en borrado {e}")



















