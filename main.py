#import subprocess
#subprocess.run(["termux-tts-speak", "Hola, esto es una prueba"])
#from uirender import UIRender
#from nvimevents import NvimEvents
import sys
from connection import NvimConnection
#from multigrid import NvimMultigrid
from onkey import register_onkey
from tts import speak
from redrawevents import RedrawEvents

current_mode = None

def all_events(event):
    print(event[0])


def tecla_presionada(event):
    print(f"event: {event}")
    key_name = NvimConnection().nvim.funcs.keytrans(event[0])
    print(f"{key_name}")
    if key_name == "<Down>" or key_name == "<Up>": 
        speak(f"{NvimConnection().nvim.current.line}")
    #print(f"{event[0]}")
    elif key_name == "<Left>" or key_name =="<Right>":
        row, col = NvimConnection().nvim.api.win_get_cursor(NvimConnection().nvim.current.window.handle)
        caracter = NvimConnection().nvim.api.buf_get_text(NvimConnection().nvim.current.buffer.number, row-1, col, row-1, col + 1, {})
        speak(f"{caracter}")
        print(f"char: {caracter}") 
    print(f"current_mode: {current_mode}")

def all_events3(event):
    print(f"{event[0]}")
    if event[0] == "win_viewport":
        print(f"{event}")
        #for line in event[1:]:
        handle = event[1][1]
        #print(f"handle: {handle}")
        config = NvimConnection().nvim.api.win_get_config(handle)
        print(f"config {config}")
    
    elif event[-0] == "grid_line":
        print(event[0])
        for line in event[1:]:
            print(line[0])

def flush(event):
    multigrid = NvimMultigrid()
    for grid_id in multigrid.viewports:
        #if NvimEvents().multigrid.viewports[grid_id]:
        try:
            if grid_id in multigrid.grids:
                print(f"grid: {grid_id} SI tiene viewport y grid")
            #viewport = NvimEvents().multigrid.viewports[grid_id]
            #handle = viewport[1]
            #config = NvimConnection().nvim.api.win_get_config(handle)
            #print(f"config {grid_id}: {config}")
            else:
                print(f"grid: {grid_id} NO tiene viewport y grid")

        except Exception as e:
            pass
            #for gi in NvimEvents().multigrid.viewports:
             #   print(f"vw: {gi} {NvimEvents().multigrid.viewports[gi]}")
        #print(f"{grid_id}: { NvimEvents().multigrid.grids[grid_id].get_lines()}")


def mode_info(event):
    print(f"mode_info: {event}")

def mode_change(event):
    print(f"mode_change: {event}")
    global current_mode
    current_mode = event[1][0]

def main():
    events = RedrawEvents()
    events.loop.connect()
    #events.register_multigrid()
    #events.ui.register_handler("mode_info_set", mode_info)
    events.register_handler("mode_change", mode_change)
    events.loop.register_notification("tecla_presionada", tecla_presionada)
    #uirender = UIRender()
    channel, info = events. nvim.api.get_api_info()
    register_onkey(channel, events.nvim)
    #print(f"channel: {channel}")
    events.loop.run_loop()

if __name__ == "__main__":
    main()


