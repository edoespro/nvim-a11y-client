class NvimGrid:
    def __init__(self, grid_id, width, height):
        self.grid_id = grid_id
        self.width = width
        self.height = height
        # Vector unidimensional contiguo para optimizar caché
        self.cells = [{'text': ' ', 'hl_id': 0} for _ in range(width * height)]
        self.win_handle = None
        self.row = 0
        self.col = 0
        self.zindex = 0
        self.is_visible = True

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.cells = [{'text': ' ', 'hl_id': 0} for _ in range(width * height)]


    def set_position(self, row, col, zindex=0):
        self.row = row
        self.col = col
        self.zindex = zindex



    
    def update_line(self, row, col_start, cells_data):
        current_col = col_start
        last_hl_id = 0

        for cell in cells_data:
        # cell es una LISTA: [text, hl_id, repeat]
        # 1. Extraer el texto real (SIEMPRE está en el índice 0)
            char = cell[0]

        # 2. Extraer hl_id si existe (índice 1), de lo contrario usar el último
            if len(cell) > 1:
                hl_id = cell[1]
                last_hl_id = hl_id
            else:
                hl_id = last_hl_id

        # 3. Extraer repeticiones si existen (índice 2), por defecto 1
            repeat = cell[2] if len(cell) > 2 else 1

        # 4. Actualizar el vector de celdas usando direccionamiento lineal
            for _ in range(repeat):
                if 0 <= row < self.height and 0 <= current_col < self.width:
                    idx = (self.width * row) + current_col
                # Guardamos un string real en 'text', permitiendo concatenación posterior
                    self.cells[idx] = {'text': char, 'hl_id': hl_id}
                current_col += 1






    def scroll(self, top, bot, left, right, rows):
        if rows > 0: # El texto sube, las filas inferiores se mueven a las superiores
            for r in range(top + rows, bot):
                src_row = r
                dst_row = r - rows
                for c in range(left, right):
                    self.cells[self.width * dst_row + c] = self.cells[self.width * src_row + c]
        else: # El texto baja (rows es negativo)
            abs_rows = abs(rows)
            for r in range(bot - abs_rows - 1, top - 1, -1):
                src_row = r
                dst_row = r + abs_rows
                for c in range(left, right):
                    self.cells[self.width * dst_row + c] = self.cells[self.width * src_row + c]





