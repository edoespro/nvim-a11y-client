from client import NvimClient
from  tts import speak
from tts import write
from connection import NvimConnection

def handle_event(event):
    name = event[0]
    #speak(f"{name}")

def tecla_presionada(event):
    print(f"En mainclient.tecla_presionada: {event}")
    tecla = event[1][0]
    key_name = NvimConnection().nvim.funcs.keytrans(tecla)
    print(f"{key_name}")
    if key_name == "<Down>" or key_name == "<Up>":
        write(f"{NvimConnection().nvim.current.line}")
        print(f"line_ {key_name}")
    elif key_name == "<Left>" or key_name =="<Right>":
        row, col = NvimConnection().nvim.api.win_get_cursor(NvimConnection().nvim.current.window.handle)
        caracter = NvimConnection().nvim.api.buf_get_text(NvimConnection().nvim.current.buffer.number, row-1, col, row-1, col + 1, {})
        write(f"{caracter}")
        print(f"char: {caracter}")
    #print(f"current_mode: {NvimClient().mode}")




def main():
    client = NvimClient()
    #client.connect()
    #client.register_handler("keypress", tecla_presionada)
    #client.register_handler("grid_cursor_goto", handle_event)
    #client.register_handler("flush", handle_event)
    client.onkey_attach()
    client.ui_attach()
    client.buf_attach()
    client.run_loop()


if __name__ == "__main__":
    main()
