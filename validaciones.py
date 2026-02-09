import regex as rx

def validar_nombre_archivo(nombre):
    #expresion regular para validar el nombre del archivo
    patron = r'^[\w,\s-]+\.[A-Za-z]+$'
    if rx.match(patron, nombre):
        return True
    else:
        return False

def validar_identificador(identificador):
    #expresion regular para validar un identificador
    patron = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if rx.match(patron, identificador):
        return True
    else:
        return False