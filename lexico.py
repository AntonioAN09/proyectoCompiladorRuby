import re

operadores = {
    "+": "suma",
    "-": "resta",
    "*": "multiplicacion",
    "/": "division",
    "=": "asignacion",
    ">": "mayor que",
    "<": "menor que"
}

palabrasReservadas = {
    "int": "entero",
    "float": "flotante",
    "string": "cadena",
    "double": "doble",
    "char": "caracter",
    "if": "condicional",   
    "else": "sino",
    "main": "funcion principal",
    "return": "retorno"
}

simbolos = {
    "(": "parentesis izquierdo",
    ")": "parentesis derecho",
    "{": "llave izquierda",
    "}": "llave derecha",
    "[": "corchete izquierdo",
    "]": "corchete derecho",
    ";": "punto y coma",
    ",": "coma"
}
tokensEncontrados = []

def validarIdentificador(token):
    patron = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return re.match(patron, token) is not None

def tokenizar(linea):
    patron = r'[^\s(){}\[\];,=+\-*/]+|[(){}\[\];,=+\-*/]'
    tokens = re.findall(patron, linea)
    return tokens

def clasificarToken(token):
    if token in palabrasReservadas:
        return "palabra reservada", palabrasReservadas[token]

    if token in operadores:
        return "operador", operadores[token]
    
    if token in simbolos:
        return "simbolo", simbolos[token]
    
    if re.match(r'^\d+$', token):
        return "numero", "número"
    
    if validarIdentificador(token):
        return "identificador", "nombre de variable o función"
    
    return "invalido", "token no reconocido"

def verificarDuplicado(token, categoria, lista):
    if categoria == "identificador":
        if token in lista:
            return True
        else:
            lista.append(token)
            return False
    return False

