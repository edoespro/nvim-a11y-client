# uirender.py
from uievents import UIEvents
from grid import NvimGrid
from connection import NvimConnection

class UIRender:
    """
    Almacena la información de posicionamiento de ventanas y mensajes,
    y se encarga de la composición final de la pantalla (renderizado por capas).
    """

    def __init__(self):
        self._ui = UIEvents()                   # singleton
        self.win_positions: dict[int, tuple] = {}    # grid_id -> (start_row, start_col, width, height)
        self.win_viewports: dict[int, list] = {}     # grid_id -> datos crudos del viewport
        self.msg_grid_info: dict = None              # información del grid de mensajes
        self.grids: dict[int, NvimGrid] = {}
        self._register_handlers()
        #pass

    def _register_handlers(self):
        handlers = {
            'grid_line':          self._handle_grid_line,
            'win_viewport':     self._handle_win_viewport,
            'msg_set_pos':      self._handle_msg_set_pos,
            'flush':            self._handle_flush
        }
        for event, handler in handlers.items():
            self._ui.register_handler(event, handler)


    def _handle_grid_line(self, event):
        for line in event[1:]:
            grid_id, row, col_start, cells, wrap = line
            if grid_id in self.grids:
                self.grids[grid_id].update_line(row, col_start, cells,wrap)
            elif grid_id in self.win_viewports:
                self.grids[grid_id] = self.create_grid_from_viewport(grid_id)
                self.grids[grid_id].update_line(row, col_start, cells,wrap)

            #self._ensure_grid(grid_id)
            #self.grid_state[grid_id].update_line(row, col_start, cells, wrap)


    def create_grid_from_viewport(self, grid_id):
        try:
            win_handle = self.win_viewports[grid_id][1]
            #print(f"handle: {win_handle}")
            nvim = self._ui.nvim
            config = nvim.api.win_get_config(win_handle)
            #print(f"config {config}")
            width = config['width']
            height = config['height']
            grid = NvimGrid(grid_id, width, height)
            if config.get('relative'): # Ventana Flotante (como Lazy)
                self.set_win_position(grid_id, config['row'], config['col'], width, height, config.get('zindex', 50))
            else: # Ventana Normal
                row, col = nvim.api.win_get_position(win_handle)
                self.set_win_position(grid_id, row, col, width, height, 0)
            return grid
        except Exception as e:
            print(f"uirendr.create_grid {e}")
            #pass # La ventana podría haberse cerrado antes de la consulta

        return None

    def set_win_position(self, grid_id, start_row, start_col, width, height, zindex):
        self.win_positions[grid_id] = (start_row, start_col, width, height, zindex)
        # Importante: no redimensionamos grids aquí, solo guardamos la posición.
        # La redimensión del grid correspondiente la hace NvimMultigrid cuando
        # recibe el grid_resize asociado (o se crea bajo demanda).

    def _handle_win_viewport(self, event):
        """win_viewport: ['win_viewport', [grid, ...]]"""
        self.delete_invalid_viewports()
        parts = event[1]
        grid_id = parts[0]
        self.win_viewports[grid_id] = parts
        print(f"Llego: {self.win_viewports[grid_id]}")

    def delete_invalid_viewports(self):
        # Limpieza de Grids "Muertos" (con manejo de errores)
        # Al no recibir grid_destroy, validamos pero sin bloquear el proceso
        to_remove = []
        nvim = self._ui.nvim
        for grid_id in self.win_viewports:
            try:
                win_handle = self.win_viewports[grid_id][1]
                # Solo validamos si tenemos el handle y no lo hemos hecho recientemente
                if win_handle and not nvim.api.win_is_valid(win_handle):
                    to_remove.append(grid_id)
            except Exception:
                # Si la llamada falla o hay timeout, asumimos que sigue vivo para no congelar
                print(f"En delete_viewports: {e}")
                #pass

        for gid in to_remove:
            del self.win_viewports[gid]
            if gid in self.grids:
                del self.grids[gid]
            if gid in self.win_positions:
                del self.win_positions[gid]
            print(f"borrado: {gid}")

    def _handle_msg_set_pos(self, event):
        """
        msg_set_pos: ['msg_set_pos', grid, row, scrolled, sep_char, zindex, compindex]
        Guarda la información de anclaje y apilamiento del grid de mensajes.
        """
        # Desempaquetamos según el nuevo formato
        grid_id, row, scrolled, sep_char, zindex, compindex = event[1]
        self.msg_grid_info = {
            'grid': grid_id,
            'row': row,
            'scrolled': scrolled,
            'sep_char': sep_char,
            'zindex': zindex,
            'compindex': compindex
        }


    def _handle_flush(self, event):
        for grid_id in self.win_viewports:
            print(f"viewport {grid_id}: {self.win_viewports[grid_id]}")
            if grid_id in self.win_positions:
                print(f"position {grid_id}: {self.win_positions[grid_id]}")
            if grid_id in self.grids:
                print(f"grid {grid_id}: {self.grids[grid_id]}")



    def render_screen(self, grid_state):
        """
        Composición por capas. A implementar más adelante.
        Recibe el diccionario de grids (grid_id -> NvimGrid) mantenido por NvimMultigrid.
        """
        # TODO: implementar la lógica de capas usando:
        # - grid_state (para contenido de celdas)
        # - self.win_positions
        # - self.msg_grid_info
        pass
        #print(f"se renderiza la pantalla")
