# grid.py
class NvimGrid:
    """
    Representa una cuadrícula de Neovim.
    Almacena el estado de las celdas y proporciona métodos para
    redimensionar, actualizar líneas y obtener el contenido renderizado.
    """

    def __init__(self, grid_id: int, cols: int, rows: int):
        self._id = grid_id
        self._cols = cols
        self._rows = rows
        self._viewport = []
        # Estado interno: diccionario fila -> columna -> carácter
        self._state = {
            r: {c: ' ' for c in range(cols)}
            for r in range(rows)
        }

    # ---------- Propiedades públicas ----------
    @property
    def id(self) -> int:
        """Identificador único del grid (1 = principal, 2 = ventana, etc.)."""
        return self._id

    @property
    def cols(self) -> int:
        """Número de columnas actual del grid."""
        return self._cols

    @property
    def rows(self) -> int:
        """Número de filas actual del grid."""
        return self._rows

    @property
    def state(self) -> dict:
        """
        Devuelve una copia superficial del estado del grid.
        Para proteger la integridad, no se debe modificar directamente;
        usar los métodos update_line(), resize(), clear().
        """
        return self._state

    @property
    def viewport(self) -> list:
        return self._viewport

    # ---------- Métodos públicos ----------
    def get_lines(self) -> list:
        """
        Retorna una lista de cadenas, una por cada fila del grid.
        Se eliminan los espacios en blanco del final de cada línea.
        """
        lines = []
        for row in range(self._rows):
            line_chars = [
                self._state.get(row, {}).get(col, ' ')
                for col in range(self._cols)
            ]
            lines.append("".join(line_chars).rstrip())
        
        textchars = ""
        textlines = ""
        for r in range(len(lines)):
            textchars = ""
            for c in range( len(lines[r])):
                textchars += lines[r][c]
            textlines += textchars

        return textlines


        #return lines

    def resize(self, cols: int, rows: int):
        """
        Redimensiona el grid a un nuevo número de columnas y filas.
        Conserva el contenido previo en las celdas que aún existan.
        """
        #print(f"resize: {self._id} {cols} {rows}")
        old_state = self._state
        new_state = {}
        for r in range(rows):
            new_state[r] = {}
            for c in range(cols):
                new_state[r][c] = old_state.get(r, {}).get(c, ' ')

        self._cols = cols
        self._rows = rows
        self._state = new_state

    def update_line(self, row: int, col_start: int, cells: list, wrap: bool = None):
        """
        Aplica una lista de celdas a una fila específica, comenzando en col_start.
        - cells: lista de listas [texto, atributo?, repeticiones?]
        - wrap (opcional): indica si la línea es parte de un texto que continúa.
        """
        #print(f"update: {self._id}")
        if row not in self._state:
            self._state[row] = {}
        current_col = col_start
        for cell in cells:
            if not isinstance(cell, list) or len(cell) == 0:
                continue
            text = cell[0]
            # El tercer elemento (si existe y es entero) indica repeticiones
            repeat = cell[2] if len(cell) > 2 and isinstance(cell[2], int) else 1
            for _ in range(repeat):
                if current_col < self._cols:  # evitar escribir fuera de límites tras redimensiones
                    self._state[row][current_col] = text
                current_col += 1

    def clear(self):
        """Limpia todas las celdas del grid, dejando espacios en blanco."""
        for r in range(self._rows):
            if r in self._state:
                for c in range(self._cols):
                    self._state[r][c] = ' '

    def __repr__(self):
        return f"<NvimGrid id={self._id} size={self._cols}x{self._rows}>"

    def update_viewport(self, parts):
        old = self._viewport
        self._viewport = parts
        #print(f"old viewport: {old} \nnew viewport: {self._viewport}")

