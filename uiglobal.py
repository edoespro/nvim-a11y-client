from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ColorRGB:
    """Representa un color en formato RGB."""
    r: int
    g: int
    b: int

@dataclass
class AtributosResaltado:
    """Almacena las propiedades visuales de un token de texto (evento hl_attr_define)."""
    id_atributo: int
    primer_plano: Optional[ColorRGB] = None     # foreground
    fondo: Optional[ColorRGB] = None            # background
    especial: Optional[ColorRGB] = None         # special (subrayados, etc)
    negrita: bool = False
    italica: bool = False
    subrayado: bool = False

@dataclass
class EstadoGlobalNeovim:
    """Almacena el estado global del editor que no depende de una cuadrícula específica."""
    directorio_actual: str = ""                # chdir
    titulo_ventana_os: str = ""                # set_title
    icono_ventana_os: str = ""                 # set_icon
    modo_actual: str = "normal"                # mode_change
    mouse_activo: bool = False                 # mouse_on / mouse_off
    opciones_neovim: Dict[str, any] = field(default_factory=dict) # option_set
    
    # Colores por defecto del editor (default_colors_set)
    color_texto_defecto: Optional[ColorRGB] = None
    color_fondo_defecto: Optional[ColorRGB] = None
    color_especial_defecto: Optional[ColorRGB] = None
    
    # Diccionarios de consulta (Lookups)
    catalogo_atributos: Dict[int, AtributosResaltado] = field(default_factory=dict)
    grupos_resaltado: Dict[str, int] = field(default_factory=dict)

