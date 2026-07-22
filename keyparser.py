
def parser_key (key_bytes, nvim):
    tipo, key_str = clasificar_tecla(key_bytes, nvim)
    
    if tipo == "SIMPLE":
        return ["SIMPLE", key_str]
        #print(f"El usuario escribió el texto literal: {key_str}")
        # Tu lógica para insertar texto o comandos directos
        
    elif tipo == "ESPECIAL":
        return ["ESPECIAL", key_str]
        #print(f"Se presionó la tecla especial: {key_str}")
        #if key_str == "<Esc>":
            # Tu lógica para salir de un modo o cerrar un menú flotante
         #   pass
            
    elif tipo == "MODIFICADOR":
        info = parsear_modificador(key_str)
        return ["MODIFICADOR", info]
        #print(f"Combinación detectada. Tecla: {info['tecla_base']}, Ctrl: {info['control']}, Alt: {info['alt']}, Shift: {info['shift']}")
        # Tu lógica para atajos de teclado complejos
        return ["UNKNOWN", key_bytes] 


import re

def clasificar_tecla(key_bytes, nvim):
    # 1. Traducir los bytes crudos a formato Vim legible
    key_str = nvim.funcs.keytrans(key_bytes)
    #print(f"key_str: {key_str}")
    
    # 2. Clasificar usando expresiones regulares
    
    # Caso A: Modificadores (ej: <C-a>, <M-x>, <S-Tab>, <C-S-F1>)
    if re.match(r'^<[CMS]-.+>$', key_str):
        return "MODIFICADOR", key_str
        
    # Caso B: Teclas Especiales Solas (ej: <Esc>, <Up>, <CR>, <Space>, <F5>)
    elif re.match(r'^<.+>$', key_str):
        return "ESPECIAL", key_str
        
    # Caso C: Caracteres Simples / ASCII (ej: "a", "1", "A", "¿", "ñ")
    else:
        return "SIMPLE", key_str



def parsear_modificador(key_str):
    # Limpiamos los caracteres < y > (ej: "<C-S-Up>" -> "C-S-Up")
    contenido = key_str.strip("<>")
    
    # Separamos por el guion
    partes = contenido.split("-")
    
    # La última parte siempre es la tecla real presionada
    tecla_base = partes[-1]
    
    # Las partes anteriores son los modificadores activos
    modificadores_activos = partes[:-1]
    
    significado = {
        "tecla_base": tecla_base,
        "control": "C" in modificadores_activos,
        "alt": ("M" in modificadores_activos or "A" in modificadores_activos),
        "shift": "S" in modificadores_activos
    }
    return significado

# Ejemplo de uso:
# parsear_modificador("<C-S-Up>") 
# Devuelve: {'tecla_base': 'Up', 'control': True, 'alt': False, 'shift': True}





























