# nvimevents.py
from loop import EventLoopManager
from uievents import UIEvents
from bufferevents import BufferEvents


class NvimEvents:
    """
    Punto central de acceso a los eventos de Neovim.
    Instancia y configura EventLoopManager, UIEvents y BufferEvents,
    exponiéndolos como propiedades para que otras clases registren sus manejadores.

    Uso típico:
        events = NvimEvents()
        events.ui.register_handler('grid_line', mi_handler)
        events.buffer.register_handler('nvim_buf_lines_event', otro_handler)
        events.start()   # conecta, adjunta UI/buffers y arranca el bucle
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
        
        # Instanciar los componentes (no se conectan todavía)
        self._loop = EventLoopManager()
        self._ui = UIEvents()
        self._buffer = BufferEvents()
        

        # Estado de configuración
        self._configured = False

    # ---------- Propiedades de solo lectura ----------
    @property
    def nvim(self):
        """Devuelve el nvim."""
        return self.loop.nvim

    @property
    def loop(self):
        """Devuelve el gestor del bucle de eventos."""
        return self._loop

    

    @property
    def ui(self):
        """Devuelve el gestor de eventos de UI."""
        return self._ui

    @property
    def buffer(self):
        """Devuelve el gestor de eventos de buffer."""
        return self._buffer


    # ---------- Configuración y arranque ----------
    #def start(self, connection_method='socket', **conn_kwargs):
    def configure(self, connection_method='socket', **conn_kwargs):
        """
        Establece la conexión con Neovim, adjunta la UI y los buffers,
        y arranca el bucle de eventos.
        
        connection_method: 'socket', 'tcp' o 'child'
        conn_kwargs: argumentos adicionales para la conexión
        """
        if self._configured:
            print("NvimEvents ya está configurado y en ejecución.")
            return

        # 1. Conectar a Neovim (sin iniciar el bucle todavía)
        #    Se asume que EventLoopManager tiene un método connect()
        #    que solo establece la conexión y deja nvim listo.
        if not hasattr(self._loop, 'connect'):
            raise AttributeError(
                "EventLoopManager no tiene método 'connect'. "
                "Añádelo como: def connect(self, method, **kwargs): ..."
            )
        success = self._loop.connect(connection_method, **conn_kwargs)
        if not success:
            print("No se pudo conectar a Neovim.")
            return

        # 2. Adjuntar UI externa (necesita conexión activa)
        self._ui.attach(width=80, height=20)

        # 3. Adjuntar buffer 1 por defecto (puede modificarse externamente)
        #self._buffer.attach_buffer(1)

        self._configured = True

        # 4. Iniciar el bucle de mensajes (bloqueante)
        #self._loop.run_loop()


    def run_loop(self):
        self._loop.run_loop()



