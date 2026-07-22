# uievents.py
from collections import defaultdict
from loop import EventLoopManager


class UIEvents:
    """
    Gestiona la suscripción a eventos de UI de Neovim (lotes 'redraw').
    Permite registrar manejadores para eventos específicos como 'grid_line',
    'win_pos', 'msg_set_pos', etc.
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
        self._attached = False

        # Obtener la instancia singleton del bucle de eventos
        self.loop = EventLoopManager()

        # Registrar el callback para la notificación 'redraw'
        self.loop.register_notification("redraw", self._on_redraw)

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

    # ---------- Adjuntar / desadjuntar UI ----------
    def attach(self, width: int = 80, height: int = 20, options: dict = None):
        """
        Adjunta el cliente como UI externa de Neovim.
        Debe haberse iniciado la conexión previamente.
        Parámetros:
            width, height: dimensiones iniciales de la pantalla.
            options: diccionario con las opciones de UI (ext_linegrid, ext_multigrid, etc.)
        """
        if self._attached:
            print("La UI ya está adjuntada.")
            return

        if not self.loop._connection.is_attached:
            raise ConnectionError("No se puede adjuntar UI: no hay conexión a Neovim.")

        # Opciones por defecto recomendadas para una UI externa completa
        default_options = {
            'ext_linegrid': True,
            'ext_popupmenu': True,
            'ext_tabline': True,
            'ext_wildmenu': True,
            'ext_multigrid': True,
            'ext_hlstate': True,
            'ext_cmdline': True,
            'ext_messages': True
        }
        if options:
            default_options.update(options)

        try:
            self.nvim.request('nvim_ui_attach', width, height, default_options)
   #         self.nvim.ui_attach(80, 20, **{
    #"ext_linegrid": True,
    #"ext_multigrid": True,  # ESTA ES LA CLAVE
    #"ext_messages": True,
    #"rgb": True
#})
            self._attached = True
            print(f"✓ UI adjuntada ({width}x{height})")
        except Exception as e:
            print(f"✗ Error al adjuntar UI: {e}")

    def detach(self):
        """Desadjunta la UI externa."""
        if not self._attached or not self.loop._connection.is_attached:
            return
        try:
            self.nvim.request('nvim_ui_detach')
            self._attached = False
            print("✓ UI desadjuntada.")
        except Exception as e:
            print(f"Error al desadjuntar UI: {e}")

    # ---------- Callback para la notificación 'redraw' ----------
    def _on_redraw(self, args):
        """
        Recibe la lista de subeventos de un lote 'redraw' y los despacha
        a los manejadores registrados.
        'args' es una lista de listas (eventos): [ ['grid_resize', ...], ['grid_line', ...], ... ]
        """
        for event in args:
            #if not isinstance(event, (list, tuple)) or len(event) == 0:
                #continue
            event_name = event[0]
            handlers = self.event_handlers.get(event_name, [])
            #if not handlers:
                #continue  # ignorar eventos no manejados
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error en manejador UI '{event_name}': {e}")

            handlers = self.event_handlers.get("all", [])
            #if not handlers:
                #continue  # ignorar eventos no manejados
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error en manejador UI 'all': {e}")
