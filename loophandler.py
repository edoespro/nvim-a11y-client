import sys
from uistate import BufferEstadoUI
from uiglobal import ColorRGB, AtributosResaltado

class EventLoopHandler:
    """Gestor de handlers individuales para eventos Neovim UI y buffer."""

    def __init__(self, event_loop_manager):
        self.manager = event_loop_manager
        self.handlers = {}
        
        # Instanciamos el buffer de estado intermedio
        self.state = BufferEstadoUI()

        events = [
            "option_set", "set_icon", "set_title", "chdir",
            "default_colors_set", "hl_attr_define", "hl_group_set",
            "grid_resize", "grid_clear", "msg_set_pos", "grid_line",
            "win_viewport", "grid_cursor_goto", "flush",
            "mode_info_set", "mode_change", "mouse_on",
            "nvim_buf_changedtick_event", "nvim_buf_lines_event",
            "nvim_buf_detach_event", "grid_scroll",
            "win_pos",
            "win_float_pos",

        ]

        for event_name in events:
            handler_name = f"{event_name}_handler"
            handler = getattr(self, handler_name)
            self.handlers[handler_name] = handler
            self.manager.add_notification_handler(event_name, handler)

    # --- UI / opciones globales ---
    def option_set_handler(self, source, args):
        for batch in args:
            name, value = batch[0], batch[1]
            self.state.estado_global.opciones_neovim[name] = value

    def set_icon_handler(self, source, args):
        for batch in args:
            self.state.estado_global.icono_ventana_os = batch[0]

    def set_title_handler(self, source, args):
        for batch in args:
            self.state.estado_global.titulo_ventana_os = batch[0]

    def chdir_handler(self, source, args):
        for batch in args:
            self.state.estado_global.directorio_actual = batch[0]

    def default_colors_set_handler(self, source, args):
        for batch in args:
            # Los colores vienen en formato entero decimal, Neovim los procesa así
            fg, bg, sp = batch[0], batch[1], batch[2]
            # Helper para convertir enteros a ColorRGB si no son -1 (por defecto)
            def to_rgb(val):
                if val == -1 or val is None: return None
                return ColorRGB((val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF)
            
            self.state.estado_global.color_texto_defecto = to_rgb(fg)
            self.state.estado_global.color_fondo_defecto = to_rgb(bg)
            self.state.estado_global.color_especial_defecto = to_rgb(sp)

    def hl_attr_define_handler(self, source, args):
        for batch in args:
            id_attr = batch[0]
            info = batch[1] # Diccionario con las propiedades rgb
            # info.get('foreground') contiene el entero del color
            # Aquí poblarías tu estructura AtributosResaltado...
            pass

    def hl_group_set_handler(self, source, args):
        for batch in args:
            name, id_attr = batch[0], batch[1]
            self.state.estado_global.grupos_resaltado[name] = id_attr

    def mode_info_set_handler(self, source, args):
        pass

    def mode_change_handler(self, source, args):
        for batch in args:
            self.state.estado_global.modo_actual = batch[0]

    def mouse_on_handler(self, source, args):
        self.state.estado_global.mouse_activo = True

    # --- Grid y pantalla ---
    def grid_resize_handler(self, source, args):
        from uigrid import CeldaPantalla
        for batch in args:
            #print(f"grid_resize: {batch}")
            id_grid, ancho, alto = batch[0], batch[1], batch[2]
            grid = self.state.obtener_cuadricula(id_grid)
            grid.ancho = ancho
            grid.alto = alto
            # Inicializar o redimensionar la matriz bidimensional de celdas
            grid.matriz_celdas = [[CeldaPantalla() for _ in range(ancho)] for _ in range(alto)]

    def grid_clear_handler(self, source, args):
        from uigrid import CeldaPantalla
        for batch in args:
            id_grid = batch[0]
            grid = self.state.obtener_cuadricula(id_grid)
            grid.matriz_celdas = [[CeldaPantalla() for _ in range(grid.ancho)] for _ in range(grid.alto)]

    def grid_line_handler(self, source, args):
        for batch in args:
            id_grid, fila, col_inicio, celdas = batch[0], batch[1], batch[2], batch[3]
            grid = self.state.obtener_cuadricula(id_grid)
            
            col_actual = col_inicio
            id_attr_actual = 0
            
            for celda in celdas:
                texto = celda[0]
                if len(celda) > 1:
                    id_attr_actual = celda[1] # El ID de resaltado cambia
                
                repeticiones = celda[2] if len(celda) > 2 else 1
                
                for _ in range(repeticiones):
                    if col_actual < grid.ancho and fila < grid.alto:
                        grid.matriz_celdas[fila][col_actual].caracter = texto
                        grid.matriz_celdas[fila][col_actual].id_atributo = id_attr_actual
                        col_actual += 1

    def grid_scroll_handler(self, source, args):
        pass

    def grid_cursor_goto_handler(self, source, args):
        for batch in args:
            id_grid, fila, col = batch[0], batch[1], batch[2]
            grid = self.state.obtener_cuadricula(id_grid)
            grid.fila_cursor = fila
            grid.columna_cursor = col

    def flush_handler(self, source, args):
        # ¡EL MOMENTO CLAVE!
        # Aquí es donde disparas la lógica de renderizado hacia tu cliente o pantalla.
        # El buffer `self.state` está completamente actualizado y consistente aquí.
        #print(">> [FLUSH]: Pantalla consistente. Lista para ser procesada / dibujada.")
        #self.state.renderizar_pantalla_consola()
        pass
    
    def msg_set_pos_handler(self, source, args):
        from uigrid import LineaMensaje
        for batch in args:
            id_grid, fila, scrolled = batch[0], batch[1], batch[2]
            self.state.posicion_mensajes = LineaMensaje(id_grid, fila, scrolled)

    
    def win_viewport_handler(self, source, args):
        for batch in args:
            # Formato real: [grid_id, window_object, topline, botline, cur_row, cur_col, ...]
            id_grid = batch[0]
            objeto_win = batch[1]
            #grid = self.state.obtener_cuadricuala(id_grid)
            #self.state.id_cuadricula_activa = id_grid
            
            # Guardamos la grilla asociada a la ventana en el estado global para tracking,
            # pero no alteramos la grilla de renderizado de consola por defecto.
            self.state.estado_global.opciones_neovim["last_focused_window_grid"] = id_grid


    # --- Eventos nativos de buffer Neovim ---
    def nvim_buf_changedtick_event_handler(self, source, args):
        pass

    def nvim_buf_lines_event_handler(self, source, args):
        # args[0] es el buffer, args[1] el changedtick, args[2] línea de inicio, etc.
        pass

    def nvim_buf_detach_event_handler(self, source, args):
        pass


    def win_pos_handler(self, source, args):
        print(f"win_pos_handler: {args}")
        for batch in args:
            # Formato: [win, grid, start_row, start_col, width, height]
            _, id_grid, fila_inicio, col_inicio, _, _ = batch
            self.state.actualizar_posicion_cuadricula(id_grid, fila_inicio, col_inicio)

    def win_float_pos_handler(self, source, args):
        print(f"win_float_post: {args}")  
        for batch in args:
            # Formato: [win, grid, anchor, anchor_grid, row, col, focusable, ...]
            _, id_grid, _, _, fila, col, _, *_ = batch
            # Las ventanas flotantes usan floats para sub-píxeles a veces; casteamos a int
            self.state.actualizar_posicion_cuadricula(id_grid, int(fila), int(col))

