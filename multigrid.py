# multigrid.py
from grid import NvimGrid
from uievents import UIEvents
from uirender import UIRender
from connection import NvimConnection

class NvimMultigrid:
    """
    Administra los grids de Neovim y coordina el renderizado.
    Se apoya en UIEvents (singleton) y UIRender.
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

        self._ui = UIEvents()               # singleton
        self.render = UIRender()            # singleton (por como lo tienes)
        self.grid_state: dict[int, NvimGrid] = {}
        self.win_positions: dict[int, tuple] = {}    # grid_id -> (start_row, start_col, width, height)
        self.win_viewports: dict[int, list] = {}     # grid_id -> datos crudos del viewport
        self.msg_grid_info: dict = None              # información del grid de mensajes


        # Dimensiones del grid principal (se actualizan con grid_resize para grid=1)
        self.global_width = 80
        self.global_height = 20

        self._register_handlers()

    @property
    def grids(self):
        return self.grid_state

    @property
    def viewports(self):
        return self.win_viewports

    def _register_handlers(self):
        handlers = {
            'grid_resize':      self._handle_grid_resize,
            'grid_clear':       self._handle_grid_clear,
            'grid_line':        self._handle_grid_line,
            'grid_cursor_goto': self._handle_grid_cursor_goto,
            'flush':            self._handle_flush,
            'win_pos':          self._handle_win_pos,
            'win_viewport':     self._handle_win_viewport,
            'msg_set_pos':      self._handle_msg_set_pos

        }
        for event, handler in handlers.items():
            self._ui.register_handler(event, handler)

    # ---------- Helpers ----------
    def _ensure_grid(self, grid_id: int):
        if grid_id not in self.grid_state:
            self.grid_state[grid_id] = NvimGrid(grid_id, self.global_width, self.global_height)

    def _resize_grid(self, grid_id: int, cols: int, rows: int):
        if grid_id in self.grid_state:
            self.grid_state[grid_id].resize(cols, rows)
        else:
            self.grid_state[grid_id] = NvimGrid(grid_id, cols, rows)

    # ---------- Manejadores ----------
    def _handle_grid_resize(self, event):
        grid_id, cols, rows = event[1]
        if grid_id == 1:
            self.global_width, self.global_height = cols, rows
        print(f"resize: {grid_id} {cols} {rows}")
        self._resize_grid(grid_id, cols, rows)

    def _handle_grid_clear(self, event):
        grid_id = event[1][0]
        #print(f"clear: {grid_id}")
        if grid_id in self.grid_state:
            self.grid_state[grid_id].clear()

    def _handle_grid_line(self, event):
        for line in event[1:]:
            grid_id, row, col_start, cells, wrap = line
            self._ensure_grid(grid_id)
            self.grid_state[grid_id].update_line(row, col_start, cells, wrap)

    def _handle_grid_cursor_goto(self, event):
        #print(f"cursor: {event}")
        pass  # se puede ignorar o guardar


    def _handle_flush(self, event):
        # Al final del lote, delegamos el renderizado a UIRender
        #self.render.render_screen(self.grid_state)
        #for grid_id in self.win_viewports:
         #   print(f"{self.win_viewports[grid_id]} is valid: {NvimConnection().nvim.request("nvim_win_is_valid", self.win_viewports[grid_id][1])}")
         pass

    def _handle_win_pos(self, event):
        """win_pos: ['win_pos', [grid, win, start_row, start_col, width, height]]"""
        grid_id, win, start_row, start_col, width, height = event[1]
        self.win_positions[grid_id] = (start_row, start_col, width, height)
        # Importante: no redimensionamos grids aquí, solo guardamos la posición.
        # La redimensión del grid correspondiente la hace NvimMultigrid cuando
        # recibe el grid_resize asociado (o se crea bajo demanda).

    def _handle_win_viewport(self, event):
        """win_viewport: ['win_viewport', [grid, ...]]"""
        parts = event[1]
        grid_id = parts[0]
        self.win_viewports[grid_id] = parts
        #self._ensure_grid(grid_id)
        #self.grid_state[grid_id].update_viewport(parts)
        #print(f"viewport: {self.win_viewports[grid_id]}")

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





