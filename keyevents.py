
from keyparser import parser_key
from collections import defaultdict
from loop import EventLoopManager


class KeyEvents:

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
        #self.keypress_event_handlers = defaultdict(list)  # { nombre_evento: [handler, ...] }
        self._attached = False

        # Obtener la instancia singleton del bucle de eventos
        self.loop = EventLoopManager()

        # Registrar el callback para la notificación 'redraw'
        self.loop.register_notification("tecla_presionada", self._on_tecla_presionada)

        # La UI no se adjunta automáticamente; se debe llamar a attach() explícitamente
        # cuando la conexión esté lista.

    # ---------- Acceso al objeto nvim ----------
    @property
    def nvim(self):
        """Devuelve el objeto nvim de la conexión activa, o lanza excepción si no hay."""
        if not self.loop._connection.is_attached:
            raise ConnectionError("No hay conexión activa a Neovim.")
        return self.loop._connection.nvim

    # ---------- Registro de manejadores ----------
    def register_handler(self, event_name: str, handler: callable):
        """Agrega un manejador para un evento de UI (ej. 'grid_line')."""
        self.event_handlers[event_name].append(handler)

    def unregister_handler(self, event_name: str, handler: callable):
        """Elimina un manejador de evento de UI."""
        if event_name in self.event_handlers:
            try:
                self.event_handlers[event_name].remove(handler)
            except ValueError:
                pass

    
    def attach3(self):
        channel_id, info = self.nvim.api.get_api_info()
        lua_script = f"""
vim.on_key(function(key)
    -- Enviar notificación RPC al canal del cliente
    -- 'tecla_presionada' es el nombre del evento que el cliente debe escuchar
    vim.rpcnotify({channel_id}, 'tecla_presionada', key)
end)
"""
        self.nvim.exec_lua(lua_script, [])

    def attach(self):
        channel_id, info = self.nvim.api.get_api_info()
    
        lua_script = f"""
local ns = vim.api.nvim_create_namespace('mi_capturador_teclas')

vim.on_key(function(key)
    --if not key or key == '' then return end

    -- pcall intenta ejecutar la notificación. Si falla (canal inválido),
    -- simplemente no hace nada en lugar de lanzar el error visual en Neovim.
    pcall(vim.rpcnotify, {channel_id}, 'tecla_presionada', key)
end, ns)
"""
        self.nvim.exec_lua(lua_script, [])


    def _on_tecla_presionada(self, event):
        args = parser_key(event[0], self.nvim)
        #print(f"En keyevents {event}")
        event_name = "keydown"
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler( args )
            except Exception as e:
                print(f"Error en manejador Keydown: {e}")

        event_name = "keypress"
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(args)
            except Exception as e:
                print(f"Error en manejador Keypress: {e}")
