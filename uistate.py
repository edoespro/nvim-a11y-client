from typing import Dict, Optional
from uiglobal import EstadoGlobalNeovim
from uigrid import CuadriculaVisual, LineaMensaje
import sys

class BufferEstadoUI:
    def __init__(self):
        self.estado_global = EstadoGlobalNeovim()
        self.cuadriculas: Dict[int, CuadriculaVisual] = {}
        self.posicion_mensajes = None
        self.id_cuadricula_activa = 1
        
        # Diccionario nuevo para registrar las coordenadas de cada grid en pantalla
        # Llave: id_cuadrícula (int) -> Valor: Tupla (fila, columna)
        self.posiciones_cuadriculas: Dict[int, Tuple[int, int]] = {1: (0, 0)}

    def obtener_cuadricula(self, id_grid: int) -> CuadriculaVisual:
        if id_grid not in self.cuadriculas:
            from uigrid import CuadriculaVisual
            self.cuadriculas[id_grid] = CuadriculaVisual(id_cuadricula=id_grid)
        return self.cuadriculas[id_grid]


    def renderizar_pantalla_consola(self):
        """
        Dibuja la cuadrícula de edición activa y concatena la cuadrícula de mensajes 
        en la parte inferior si Neovim ha enviado datos para ella.
        """
        import sys
        
        # 1. Obtener la cuadrícula de edición activa (donde está el código/texto)
        id_grid_activa = self.id_cuadricula_activa
        if id_grid_activa not in self.cuadriculas:
            print(f"No esta id: {id_grid_activa}")
            return # Evitamos renderizar si no hay datos listos
            
        grid_texto = self.cuadriculas[id_grid_activa]
        
        # Limpieza rápida de pantalla de Termux mediante ANSI
        sys.stdout.write("\033[H\033[2J")
        
        lineas_pantalla = []
        
        # 2. Renderizar el bloque de la ventana principal (lo que ya te funcionaba bien)
        for fila in grid_texto.matriz_celdas:
            texto_fila = "".join(celda.caracter for celda in fila)
            lineas_pantalla.append(texto_fila)
            
        # 3. COMPLEMENTO: Buscar si existen cuadrículas de mensajes o estado (IDs distintos a la activa y a la 1)
        # Neovim suele usar IDs como 3 o 4 para la barra inferior. Si existen y tienen texto, las añadimos abajo.
        for id_grid, grid_secundaria in self.cuadriculas.items():
            if id_grid != id_grid_activa and id_grid != 1:
                # Solo procesamos si la grilla secundaria tiene celdas cargadas
                if grid_secundaria.matriz_celdas:
                    for fila in grid_secundaria.matriz_celdas:
                        texto_fila = "".join(celda.caracter for celda in fila)
                        # Si la línea no está completamente vacía, la agregamos al final
                        if texto_fila.strip():
                            lineas_pantalla.append(texto_fila)

        # 4. Volcar de un solo golpe a la terminal
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.write("\n".join(lineas_pantalla))
        sys.stdout.flush()


