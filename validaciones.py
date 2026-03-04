import re

def validar_nombre_archivo(nombre):
    #expresion regular para validar el nombre del archivo
    patron = r'^[\w,\s-]+\.[A-Za-z]+$'
    if re.match(patron, nombre):
        return True
    else:
        return False

def validar_identificador(identificador):
    #expresion regular para validar un identificador
    patron = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if re.match(patron, identificador):
        return True
    else:
        return False
    
def validar_aperturaCierre(codigo):
    stack = []
    pares = {'(': ')', '{': '}', '[': ']'}
    linea_actual = 1
    
    for i, char in enumerate(codigo):
        if char == '\n':
            linea_actual += 1
        if char in pares:
            stack.append((char, linea_actual))
        elif char in pares.values():
            if not stack:
                return False, linea_actual, f"Cierre '{char}' sin apertura correspondiente"
            apertura, linea_apertura = stack.pop()
            if pares[apertura] != char:
                return False, linea_actual, f"Cierre '{char}' no coincide con apertura '{apertura}' en línea {linea_apertura}"
    
    if stack:
        apertura, linea_apertura = stack[-1]
        return False, linea_apertura, f"'{apertura}' sin cerrar"
    
    return True, None, None
