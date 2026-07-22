# bufferevents.py
from collections import defaultdict
from loop import EventLoopManager


class BufferEvents:
    """
    Gestiona la suscripción a eventos de buffer de Neovim.
    Permite registrar manejadores para eventos como 'nvim_buf_lines_event',
    'nvim_buf_changedtick_event', etc., y los despacha cuando se reciben.
    Se debe adjuntar un buffer con attach_buffer() para empezar a recibir eventos.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Evitar reinicialización si ya fue inicializado
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.event_handlers = defaultdict(list)  # { nombre_evento: [handler, ...] }
        self._attached_buffers = set()           # buffers a los que nos hemos adjuntado
        self._registered_events = set()          # eventos ya registrados en el loop

        # Obtener la instancia singleton del bucle de eventos
        self.loop = EventLoopManager()
        self.register_handler("nvim_buf_lines_event", self.handle_buf_lines_event)
        self.register_handler("nvim_buf_changedtick_event", self.handle_buf_changedtick_event)
        self.register_handler("nvim_buf_detach_event", self.handle_buf_detach_event)
        
# ---------- Acceso al objeto nvim ----------
    @property
    def nvim(self):
        """Devuelve el objeto nvim de la conexión activa, o lanza excepción si no hay."""
        if not self.loop._connection.is_attached:
            raise ConnectionError("No hay conexión activa a Neovim.")
        return self.loop._connection.nvim

    # ---------- Registro de manejadores ----------
    def register_handler(self, event_name: str, handler: callable):
        """
        Agrega un manejador para un evento de buffer.
        Si el evento aún no está registrado en el bucle principal, lo registra.
        """
        self.event_handlers[event_name].append(handler)
        # Registrar la notificación en el loop si no está ya
        if event_name not in self._registered_events:
            self.loop.register_notification(
                event_name,
                lambda args, name=event_name: self._dispatch(name, args)
            )
            self._registered_events.add(event_name)

    def unregister_handler(self, event_name: str, handler: callable):
        """Elimina un manejador de evento de buffer."""
        if event_name in self.event_handlers:
            try:
                self.event_handlers[event_name].remove(handler)
            except ValueError:
                pass

    # ---------- Adjuntar / desadjuntar buffer ----------
    def attach_buffer(self, buf_number: int):
        """
        Se adjunta a un buffer específico para recibir sus eventos.
        Llama a nvim_buf_attach con send_buffer=True y opciones vacías.
        Se puede llamar varias veces para distintos buffers.
        """
        if not self.loop._connection.is_attached:
            raise ConnectionError("No se puede adjuntar buffer: no hay conexión a Neovim.")
        if buf_number in self._attached_buffers:
            print(f"Ya adjuntado al buffer {buf_number}.")
            return

        try:
            self.nvim.request('nvim_buf_attach', buf_number, True, {})
            self._attached_buffers.add(buf_number)
            print(f"✓ Adjuntado al buffer {buf_number}")
        except Exception as e:
            print(f"✗ Error al adjuntar buffer {buf_number}: {e}")

    def detach_buffer(self, buf_number: int):
        """Desadjunta un buffer previamente adjuntado."""
        if not self.loop._connection.is_attached:
            return
        if buf_number not in self._attached_buffers:
            return
        try:
            self.nvim.request('nvim_buf_detach', buf_number)
            self._attached_buffers.discard(buf_number)
            print(f"✓ Desadjuntado buffer {buf_number}")
        except Exception as e:
            print(f"Error al desadjuntar buffer {buf_number}: {e}")

    # ---------- Despacho interno ----------
    def _dispatch(self, event_name: str, args):
        """
        Busca los manejadores registrados para event_name y los invoca con los args.
        Los args dependen del evento; para nvim_buf_lines_event son
        (buffer, tick, firstline, lastline, linedata, more).
        """
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(args)
            except Exception as e:
                print(f"Error en manejador de buffer '{event_name}': {e}")




    def handle_buf_lines_event(self, event):
        print(f"buf_lines: \n{event}")
        
    def handle_buf_changedtick_event(self, event):
        print(f"buf_changedtick: {event}")

    def handle_buf_detach_event(self, event):
        print(f"bu_detach: {event}")
    

























