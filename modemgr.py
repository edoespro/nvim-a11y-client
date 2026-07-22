from mode import NvimMode
from  insert import Insert
from uievents import UIEvents
from tts import speak
from keyevents import KeyEvents


class ModeManager:

    def __init__(self):
        self.mode_info = []
        self.nvim_modes = {
                "insert": Insert()
                }
        self.current_nvim_mode = None        
        self.current_mode = ""
        ui = UIEvents()
        ui.register_handler("mode_info_set", self.handle_mode_info_set)
        ui.register_handler("mode_change", self.handle_mode_change)
        keys = KeyEvents()
        keys.register_handler("keydown", self.handle_keydown)

    def handle_mode_info_set(self, event):
        info = event[1]
        #print(f"entro a mode info {len(info[1])}\n{info}\n")
        for i in range(len(info[1])):
            #name = dic["name"]
            self.mode_info.append(info[1][i])
        for j in range(len(self.mode_info)):
            name = self.mode_info[j]["name"]
            short_name = self.mode_info[j]["short_name"]
            print(f"{j}) name: {name}, short_name: {short_name}.\n")
            if name not in self.nvim_modes:
                self.nvim_modes[name] = None

    def handle_mode_change(self, event):
        mode_name = event[1][0]
        #print(mode_name)
        speak(mode_name)
        #self.current_mode = mode_name
        #self.current_nvim_mode = self.nvim_modes[mode_name]

        if mode_name in self.nvim_modes:
            self.current_nvim_mode = self.nvim_modes[mode_name]
        #self.current_mode = mode_name
        #print(f"nvim_mode: {self.current_nvim_mode}")


    def handle_keydown(self, event):
        ##print(f"En keydown nvim_mode: {self.current_nvim_mode}")
        if self.current_nvim_mode:
            self.current_nvim_mode.process_key(event)











