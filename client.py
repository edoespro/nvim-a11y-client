from collections import defaultdict
from connection import NvimConnection
from loop import EventLoopManager
from uievents import UIEvents
from keyevents import KeyEvents
from modemgr import ModeManager
from bufferevents import BufferEvents

class NvimClient:

    def __init__(self):
        self._running = False
        self._connection = NvimConnection()
        self.connect()
        self._loop = EventLoopManager()
        self.event_handlers = defaultdict(list)
        self._mode = ""

        self._ui_events = UIEvents()
        self._ui_events.register_handler("all", self.on_event)
        
        self._key_events = KeyEvents()
        self._key_events.register_handler("keypress", self.on_event)
        self._key_events.register_handler("keydown", self.on_event)
        
        self._buffer_events = BufferEvents()

        self.mode_manager = ModeManager()

    @property
    def mode(self):
        return self.mode_manager.current_mode

    def connect(self, method='socket', **kwargs):
        """Solo conecta, no arranca el bucle."""
        #if self._running:
            #print("Ya hay un bucle en ejecución.")
            #return False
        if method == 'socket':
            ok = self._connection.attach_socket(**kwargs)
        elif method == 'tcp':
            ok = self._connection.attach_tcp(**kwargs)
        elif method == 'child':
            ok = self._connection.attach_child(**kwargs)
        else:
            raise ValueError(f"Método desconocido: {method}")
        if ok:
            print("Conexión establecida. Listo para iniciar el bucle.")
        return ok



    def run_loop(self):
        if self._running:
            print("Ya hay un bucle en ejecución.")
            return False
        self._loop.run_loop()
        self.running = True
    

    def register_handler(self, event_name: str, handler: callable):
        """Agrega un manejador para un evento de UI (ej. 'grid_line')."""
        self.event_handlers[event_name].append(handler)

    def unregister_handler(self, event_name: str, handler: callable):
        """Elimina un manejador de evento de UI."""
        if event_name in self.event_handlers:
            try:
                self.event_handlers[event_name].remove(handler)
            except ValueError:
                passi


    def on_event(self, event):
        event_name = event[0]
        #if event_name == "keypress":
            #print(f"En client.on_evnet: {event_name}")
        handlers = self.event_handlers.get(event_name, [])
            #if not handlers:
                #continue  # ignorar eventos no manejados
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error en Client.on_event '{event_name}': {e}")


    def ui_attach(self):
        self._ui_events.attach()

    def onkey_attach(self):
        self._key_events.attach()

    def buf_attach(self):
        self._buffer_events.attach_buffer(1)












