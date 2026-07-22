import sys

class GridManager:
    def __init__(self, nvim_instance):
        self.nvim = nvim_instance
        self.grids = {}
        self.highlight_table = {0: {'fg': None, 'bg': None}} # Resaltado base
        self.cursor_pos = {'grid': 1, 'row': 0, 'col': 0}

    def get_grid(self, grid_id):
        return self.grids.get(grid_id)

    def pull_window_info(self, grid_id, win_handle):
        """Solicita activamente la posición si no se recibió el evento"""
        grid = self.get_grid(grid_id)
        if not grid: return

        try:
            config = self.nvim.api.win_get_config(win_handle)
            if config.get('relative'): # Ventana Flotante (como Lazy)
                grid.set_position(config['row'], config['col'], config.get('zindex', 50))
            else: # Ventana Normal
                row, col = self.nvim.api.win_get_position(win_handle)
                grid.set_position(row, col, 0)
        except Exception:
            pass # La ventana podría haberse cerrado antes de la consulta

    def _render_to_terminal(self):
        """Compositor jerárquico disparado por el evento 'flush'"""
    # 1. Limpieza de grids asociados a ventanas que ya no son válidas
        to_remove = []
        for g_id, grid in self.grids.items():
            #print(g_id)
            if grid.win_handle and not self.nvim.api.win_is_valid(grid.win_handle):
                #print(g_id)
                to_remove.append(g_id)
        for g_id in to_remove:
            del self.grids[g_id]

        #return

    # 2. Ordenar grids por zindex para el renderizado por capas
    # Capa Base (0) -> Flotantes (50+) -> Mensajes (200)
        sorted_grids = sorted(self.grids.values(), key=lambda g: g.zindex)

    # 3. Dibujar cada grid en su posición física de pantalla
        for grid in sorted_grids:
            #print(f"{grid.grid_id}{grid.is_visible}")
            if not grid.is_visible:
                continue

            for r in range(grid.height):
            # Calcular posición absoluta en la terminal (1-based para ANSI)
                term_row = int(grid.row + r + 1)
                term_col = int(grid.col + 1)

            # Posicionar cursor: \033[Fila;ColumnaH
                sys.stdout.write(f"\033[{term_row};{term_col}H")

            # Construir la línea uniendo los caracteres del vector unidimensional
                line_chars = []
                for c in range(grid.width):
                    cell = grid.cells[(grid.width * r) + c]
                    line_chars.append(cell['text'])

            # Escribir la fila completa de una sola vez
                #print(line_chars)
                sys.stdout.write("".join(line_chars))

    # 4. Posicionar el cursor físico en el grid que tiene el foco
        f_grid = self.get_grid(self.cursor_pos['grid'])
        if f_grid:
            cursor_r = int(f_grid.row + self.cursor_pos['row'] + 1)
            cursor_c = int(f_grid.col + self.cursor_pos['col'] + 1)
            #sys.stdout.write(f"\033[{cursor_r};{cursor_c}H")

        sys.stdout.flush()
 


    def render_to_terminal(self):
        # 1. Obtener el Grid 1 (Base global)
        base_grid = self.get_grid(1)
        if not base_grid: 
            return
        
        screen_w, screen_h = base_grid.width, base_grid.height
        
        # 2. LIMPIEZA TOTAL DEL LIENZO (Evita que Lazy se quede pegado)
        # Re-inicializamos la matriz con espacios en cada flush
        canvas = [[' ' for _ in range(screen_w)] for _ in range(screen_h)]

        # 3. Limpieza de Grids "Muertos" (con manejo de errores)
        # Al no recibir grid_destroy, validamos pero sin bloquear el proceso
        to_remove = []
        for gid, grid in self.grids.items():
            if gid == 1: continue # El grid global nunca se borra
            try:
                # Solo validamos si tenemos el handle y no lo hemos hecho recientemente
                if grid.win_handle and not self.nvim.api.win_is_valid(grid.win_handle):
                    to_remove.append(gid)
            except Exception:
                # Si la llamada falla o hay timeout, asumimos que sigue vivo para no congelar
                pass
                
        for gid in to_remove: 
            del self.grids[gid]

        # 4. Orden de Capas (Z-Index)
        # Grid 1 al fondo (-1), Base (0), Flotantes (50), Mensajes (200)
        sorted_grids = sorted(self.grids.values(), key=lambda g: -1 if g.grid_id == 1 else g.zindex)

        # 5. Estampar Grids en el Lienzo Virtual
        for grid in sorted_grids:
            if not grid.is_visible: continue
            
            for r in range(grid.height):
                abs_row = int(grid.row + r)
                if 0 <= abs_row < screen_h:
                    for c in range(grid.width):
                        abs_col = int(grid.col + c)
                        if 0 <= abs_col < screen_w:
                            # I = W * R + C
                            cell = grid.cells[(grid.width * r) + c]
                            char = cell['text']
                            # Si el carácter es vacío (derecha de un wide-char), no sobreescribir
                            if char != "":
                                canvas[abs_row][abs_col] = char

        # 6. Construir Cadena Única de Salida
        output = ["\033[H"] # Salto a Home (0,0)
        for i, row_chars in enumerate(canvas):
            output.append("".join(row_chars))
            if i < screen_h - 1:
                output.append("\n")

        # 7. Posicionar Cursor Físico
        f_grid = self.get_grid(self.cursor_pos['grid'])
        if f_grid:
            cursor_r = int(f_grid.row + self.cursor_pos['row'] + 1)
            cursor_c = int(f_grid.col + self.cursor_pos['col'] + 1)
            output.append(f"\033[{cursor_r};{cursor_c}H")

        # 8. Volcado único al hardware
        sys.stdout.write("".join(output))
        sys.stdout.flush()
