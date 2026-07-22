import sys
from collections import defaultdict
import pynvim
import asyncio


SOCKET_PATH = '/data/data/com.termux/files/home/nvim.sock'

class EventLoopManager:
    # Propiedad estática (Singleton)
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(EventLoopManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # Evita la reinicialización si el Singleton ya existe
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # Propiedades miembro
        self.nvim = None
        self.notifications = defaultdict(list)
        self.requests = defaultdict(list)
        if not self.connect():
            sys.exit(1)
        self.ui_attach()
        self.buf_attach()
        #self.start_loop()




    def connect(self, path=SOCKET_PATH):
        try:
            self.nvim = pynvim.attach('socket', path=path)
            print(f"✓ Conectado a Neovim en: {path}")
            return True
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            print("\nAsegúrate de que Neovim está escuchando con:")
            print(f"  nvim --listen {path}")
            return False

    def ui_attach(self):
        if self.nvim:
            options={'ext_linegrid': True, 'ext_popupmenu': True, 'ext_tabline': True, 'ext_wildmenu': True, 'ext_multigrid': True, 'ext_hlstate': True, 'ext_cmdline': True, 'ext_messages': True}
            self.nvim.ui_attach(80, 24, True, **options) 
            print("Enlazado ainterfaz de usuario (ui_attach)...")

    def ui_detach(self):
        # Envía una notificación para desvincular la interfaz si está activa
        if self.nvim:
            self.nvim.command('ui_detach()')

    def buf_attach(self):
        if self.nvim:
             buffer = self.nvim.current.buffer 
             print("Enlazado a buffer")
             print("\nEventos recibidos\n")
             return self.nvim.api.buf_attach(buffer, False, {})
        return False

    def buf_detach(self, buffer):
        if self.nvim:
            # Neovim no tiene un api.buf_detach directo, se suele limpiar el attachment
            # o el buffer llamando a comandos específicos o dejando que expire.
            pass

    def add_notification_handler(self, event_name, handler):
        self.notifications[event_name].append(handler)

    def remove_notification_handler(self, event_name, handler):
        if event_name in self.notifications:
            try:
                self.notifications[event_name].remove(handler)
            except ValueError:
                pass

    def add_request_handler(self, method_name, handler):
        self.requests[method_name].append(handler)

    def remove_request_handler(self, method_name, handler):
        if method_name in self.requests:
            try:
                self.requests[method_name].remove(handler)
            except ValueError:
                pass

    def on_request(self, method, args):
        print(f"[Request Recibida]: {method}")
        if method in self.requests:
            for handler in self.requests[method]:
                try:
                    handler(self.nvim, args)
                except Exception as e:
                    print(f"Error en handler de request '{method}': {e}")
        else:
            print(f"Advertencia: No hay manejadores registrados para la solicitud '{method}'")

    def on_notification(self, method, args):
        # El bucle UI de Neovim emite un método genérico 'redraw' y los eventos 
        # vienen empaquetados dentro de los argumentos (args)
        #print("entro")
        
        if method == 'redraw':
            self.on_redraw(method, args)
        else:
            print(f"{method}:")
            print(f"\n{args}\n")
            # Para notificaciones RPC personalizadas fuera del ecosistema 'redraw'
            if method in self.notifications:
                for handler in self.notifications[method]:
                    handler(self.nvim, args)

    def on_redraw(self, method, args):
            #print(f"{method}")
            #i=0
            for event in args:
                #i=i+1
                event_name = event[0]
                print(f"{event_name}:")
                #if event_name == "msg_set_pos":
                    #print(f"\n{event}\n")
                    #print(f"{type(event)}   {len(event)}   {type(event[1])}   {len(event[1])}   {type(args)}   {len(args)}   {type(args[1])}   {len(args[1])}")
                    #for evargs in event:
                        #print(f"{evargs}")
                event_args = event[1:]
                print(f"\n{event_args}\n")
                if event_name in self.notifications:
                    for handler in self.notifications[event_name]:
                        try:
                            handler(self.nvim, event_args)
                        except Exception as e:
                            print(f"Error en handler de notificación '{event_name}': {e}")
                else:
                    print(f"\nAdvertencia: evento de redraw no registrado: {event_name}\n")




    def start_loop(self):
        if not self.nvim:
            print("Error: No se puede iniciar el bucle sin una conexión activa.")
            return
        try:
            # Pasa las funciones miembro encargadas de rutear las peticiones
            self.nvim.run_loop(self.on_request, self.on_notification)
        except KeyboardInterrupt:
            self.disconnect()

    def disconnect(self):
        if self.nvim:
            try:
                self.ui_detach()
                self.nvim.close()
                print("\nDesconectado de Neovim exitosamente.")
            except Exception as e:
                print(f"Error al cerrar la conexión: {e}")
            finally:
                self.nvim = None




