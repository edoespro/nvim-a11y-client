from dataclasses import dataclass, field
from typing import List

@dataclass
class CeldaPantalla:
    """Representa un único caracter en la pantalla con su estilo aplicado."""
    caracter: str = " "
    id_atributo: int = 0  # Referencia al id en catalogo_atributos

@dataclass
class CuadriculaVisual:
    """Representa una cuadrícula de texto (grid_resize, grid_clear, grid_line)."""
    id_cuadricula: int
    ancho: int = 0
    alto: int = 0
    # Matriz bidimensional de celdas [fila][columna]
    matriz_celdas: List[List[CeldaPantalla]] = field(default_factory=list)
    
    # Posición del cursor en esta cuadrícula específica (grid_cursor_goto)
    fila_cursor: int = 0
    columna_cursor: int = 0

@dataclass
class LineaMensaje:
    """Representa el contenido de una línea de comandos o mensaje (msg_set_pos)."""
    grid_origen: int
    fila_origen: int
    scrolled: bool = False

