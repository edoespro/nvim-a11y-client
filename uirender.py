# uirender.py
import subprocess
import sys
from uievents import UIEvents
from grid import NvimGrid

class UIRender:
    """
    Almacena la información de posicionamiento de ventanas y mensajes,
    y se encarga de la composición final de la pantalla (renderizado por capas).
    La creación de grids se basa en el evento 'win_viewport' y los grids
    se mantienen en un diccionario indexado por grid_id.
    """

    def __init__(self):
        self._ui = UIEvents()                       # singleton

        # Diccionarios de estado
        self.win_viewports: dict[int, list] = {}    # grid_id -> lista cruda del viewport
        self.win_positions: dict[int, tuple] = {}   # grid_id -> (row, col, width, height, zindex)
        self.grids: dict[int, NvimGrid] = {}        # grid_id -> objeto NvimGrid
        self.msg_grid_info: dict = None             # información del grid de mensajes

        # Dimensiones del grid global (ID 1) – se actualizan con grid_resize
        self.global_width = 80
        self.global_height = 20
        # Aseguramos que el grid 1 exista inicialmente
        self.grids[1] = NvimGrid(1, self.global_width, self.global_height)
        self.msg_grid = None
        self._register_handlers()
        self.text_speak = ""
        self.contador = 0
    # ------------------------------------------------------------------
    # Registro de manejadores
    # ------------------------------------------------------------------
    def _register_handlers(self):
        handlers = {
            'grid_resize':       self._handle_grid_resize,
            'grid_clear':        self._handle_grid_clear,
            'grid_line':         self._handle_grid_line,
            'grid_cursor_goto':   self._handle_grid_cursor_goto,
            'win_viewport':      self._handle_win_viewport,
            'msg_set_pos':       self._handle_msg_set_pos,
            'flush':             self._handle_flush
        }
        for event, handler in handlers.items():
            self._ui.register_handler(event, handler)

    # ------------------------------------------------------------------
    # Manejadores de eventos
    # ------------------------------------------------------------------
    def _handle_grid_cursor_goto(self,event):
        grid_id, row, col = event[1]
        line = ""
        #buffer = self._ui.nvim.current.buffer
        #window = self._ui.nvim.current.window
        #if grid_id in self.win_viewports:
         #   print(f"{self.win_viewports[grid_id]}")
          #  win_handle = self.win_viewports[grid_id][1]
        #--buf_id = self._ui.nvim.api.win_get_buf(window.handle)
        #--row, col = self._ui.nvim.api.win_get_cursor(window.handle)
        #--line = self._ui.nvim.api.buf_get_lines(buf_id, row - 1, row, True)
        #else:
        #row, col = self._ui.nvim.api.win_get_cursor(window.handle)
        #line = self._ui.nvim.api.buf_get_lines(window.number, row - 1, row, True)
            #nvim_win_get_cursor
            #win_viewport
        #for gid in self.win_viewports:
        #    print (f"window {window.handle} {window.number} \ngrid: {grid_id} for {gid} {grid_id in self.win_viewports} row {row} col {col} \n linea: {line}")
        #self.speak(self._ui.nvim.current.line)
        

    def _handle_grid_resize(self, event):
        """Solo se usa para redimensionar el grid 1 (pantalla global)."""
        grid_id, cols, rows = event[1]
        if grid_id in self.grids:
            self.grids[grid_id].resize(cols, rows)
            if grid_id == 1:
                self.global_width = cols
                self.global_height = rows
            #if 1 in self.grids:
            #    self.grids[1].resize(cols, rows)
            #else:
             #   self.grids[1] = NvimGrid(1, cols, rows)

    def _handle_grid_clear(self, event):
        """Limpia un grid específico."""
        grid_id = event[1][0]
        if grid_id in self.grids:
            self.grids[grid_id].clear()

    def _handle_grid_line(self, event):
        """Aplica líneas a un grid, creándolo si es necesario a partir del viewport."""
        for line in event[1:]:
            grid_id, row, col_start, cells, wrap = line
            if grid_id in self.grids:
                self.grids[grid_id].update_line(row, col_start, cells, wrap)
            #if grid_id not in self.grids:
                # Intentar crear el grid usando la información del último viewport
            elif grid_id in self.win_viewports:
                self.grids[grid_id] = self._create_grid_from_viewport(grid_id)
                self.grids[grid_id].update_line(row, col_start, cells, wrap)
                #else:
                    # Grid desconocido y sin viewport previo → ignorar (no debería pasar)
                 #   continue
            #if grid_id in self.grids:
                #self.grids[grid_id].update_line(row, col_start, cells, wrap)

    def _handle_win_viewport(self, event):
        """
        win_viewport: ['win_viewport', [grid, win_handle, ...]]
        Almacena el viewport y limpia ventanas ya cerradas.
        """
        self._delete_invalid_viewports()
        parts = event[1]
        grid_id = parts[0]
        self.win_viewports[grid_id] = parts

    def _handle_msg_set_pos(self, event):
        """
        msg_set_pos: ['msg_set_pos', grid, row, scrolled, sep_char, zindex, compindex]
        """
        grid_id, row, scrolled, sep_char, zindex, compindex = event[1]
        if grid_id not in self.grids:
            self.msg_grid = NvimGrid(grid_id, self.global_width, self.global_height)
            self.grids[grid_id] = self.msg_grid

        self.msg_grid_info = {
            'grid': grid_id,
            'row': row,
            'scrolled': scrolled,
            'sep_char': sep_char,
            'zindex': zindex,
            'compindex': compindex
        }

    def _handle_flush(self, event):
        """Al final de un lote de redraw, se compone y dibuja la pantalla."""
        #lines = self.render_screen()
        #self._draw_screen(lines)
        #print(self.msg_grid.get_lines())
        #text = self.msg_grid.get_lines().strip()
        #if text != self.text_speak:
            #subprocess.run(["termux-tts-speak", text])
            #self.text_speak = text
        #self.contador += 1
        #print(self.contador)


    # ------------------------------------------------------------------
    # Lógica de creación y mantenimiento de grids
    # ------------------------------------------------------------------
    def _create_grid_from_viewport(self, grid_id):
        """Crea un NvimGrid usando el handle de ventana almacenado en win_viewports."""
        try:
            parts = self.win_viewports[grid_id]
            win_handle = parts[1]  # segundo elemento del viewport
            nvim = self._ui.nvim

            # Para ventanas normales obtenemos posición absoluta
            # Para flotantes usamos la configuración específica
            config = nvim.api.win_get_config(win_handle)
            width = config['width']
            height = config['height']
            if config.get('relative'):  # ventana flotante
                row = int(config['row'])
                col = int(config['col'])
                zindex = config.get('zindex', 50)
                self._set_win_position(grid_id, row, col, width, height, zindex)
            else:  # ventana normal
                row, col = nvim.api.win_get_position(win_handle)
                self._set_win_position(grid_id, row, col, width, height, 0)
            return NvimGrid(grid_id, width, height)
        except Exception as e:
            print(f"Error en _create_grid_from_viewport para grid {grid_id}: {e}")
            return None

    def _set_win_position(self, grid_id, start_row, start_col, width, height, zindex):
        self.win_positions[grid_id] = (start_row, start_col, width, height, zindex)

    def _delete_invalid_viewports(self):
        """Elimina viewports, posiciones y grids cuyas ventanas han sido cerradas."""
        to_remove = []
        nvim = self._ui.nvim
        for grid_id, parts in list(self.win_viewports.items()):
            try:
                win_handle = parts[1]
                if not nvim.api.win_is_valid(win_handle):
                    to_remove.append(grid_id)
            except Exception as e:
                # Si falla la consulta, mantenemos el grid por seguridad
                print(f"Error validando ventana {grid_id}: {e}")
                pass

        for gid in to_remove:
            del self.win_viewports[gid]
            self.grids.pop(gid, None)
            self.win_positions.pop(gid, None)

    # ------------------------------------------------------------------
    # Composición de la pantalla
    # ------------------------------------------------------------------
    def render_screen(self):
        """
        Compone la pantalla completa por capas:
        1. Capa base: grid 1
        2. Ventanas superpuestas según win_positions (ordenadas por zindex)
        3. Grid de mensajes (msg_grid_info) como capa superior
        Retorna una lista de cadenas, una por línea, listas para imprimir.
        """
        # --- Capa base: grid 1 ---
        base_lines = {}
        g1 = self.grids.get(1)
        if g1:
            for r in range(self.global_height):
                base_lines[r] = list(g1.state.get(r, {}).get(c, ' ') for c in range(self.global_width))
        else:
            for r in range(self.global_height):
                base_lines[r] = [' '] * self.global_width

        # --- Superposición de ventanas (ordenadas por zindex) ---
        # Filtrar solo las ventanas que tienen grid y posición válidos
        valid_windows = []
        for grid_id, (sr, sc, w, h, z) in self.win_positions.items():
            if grid_id in self.grids:
                valid_windows.append((z, grid_id, sr, sc, w, h))
        # Ordenar de menor a mayor zindex
        valid_windows.sort(key=lambda x: x[0])

        for _, grid_id, sr, sc, w, h in valid_windows:
            grid = self.grids[grid_id]
            for r in range(h):
                for c in range(w):
                    char = grid.state.get(r, {}).get(c, ' ')
                    if char != ' ':  # transparencia para espacios
                        row = sr + r
                        col = sc + c
                        if 0 <= row < self.global_height and 0 <= col < self.global_width:
                            base_lines[row][col] = char

        # --- Superposición del grid de mensajes ---
        if self.msg_grid_info:
            mg = self.msg_grid_info
            msg_grid_id = mg['grid']
            if msg_grid_id in self.grids:
                msg_grid = self.grids[msg_grid_id]
                mrow = mg['row']
                mw = msg_grid.cols   # asumimos que el grid ya tiene el tamaño correcto
                mh = msg_grid.rows
                for r in range(mh):
                    for c in range(mw):
                        char = msg_grid.state.get(r, {}).get(c, ' ')
                        if char != ' ':
                            row = mrow + r
                            col = c
                            if 0 <= row < self.global_height and 0 <= col < self.global_width:
                                base_lines[row][col] = char

        # --- Convertir a lista de strings ---
        screen = []
        for r in range(self.global_height):
            line = ''.join(base_lines[r]).rstrip()
            screen.append(line)
        return screen

    # ------------------------------------------------------------------
    # Dibujado en terminal (ANSI)
    # ------------------------------------------------------------------
    def _draw_screen(self, lines):
        """Limpia la terminal y vuelca las líneas recibidas."""
        sys.stdout.write("\033[2J\033[H")  # limpiar pantalla, cursor a (1,1)
        for i, line in enumerate(lines):
            if i == len(lines) - 1:
                sys.stdout.write(line)      # última línea sin salto para evitar scroll
            else:
                sys.stdout.write(line + "\n")
        sys.stdout.write("\033[H")          # cursor al inicio para el siguiente frame
        sys.stdout.flush()


    def speak(self, text):
        subprocess.run(["termux-tts-speak", text])
