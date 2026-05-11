import re

operadores = {
    "+": "suma", #operadores aritméticos
    "-": "resta",
    "*": "multiplicacion",
    "/": "division",
    "%": "modulo",
    "**": "potenciacion",
    "=": "asignacion",  #operadores de asignación
    "+=": "asignacion suma",
    "-=": "asignacion resta",
    "/=": "asignacion division",
    "*=": "asignacion multiplicacion",
    "%=": "asignacion modulo",
    "||=": "asignacion or",
    "==": "igualdad",   #operadores de relación
    "!=": "desigualdad",
    ">": "mayor que",
    "<": "menor que",
    ">=": "mayor o igual que",
    "<=": "menor o igual que",
    "<=>": "operador de comparación combinado",
    "===": "operador de comparación triple",
    "&&": "operador lógico and",    #operadores lógicos
    "||": "operador lógico or",
    "!": "operador lógico not",
    "and": "operador lógico and",
    "or": "operador lógico or",
    "not": "operador lógico not",
    "..": "operador de rango",  #operadores de rango
    "...": "operador de rango exclusivo",
    "?": "operador ternario", #operadores especiales
    ":": "operador de símbolo",
    "::": "operador de resolución de ámbito",
    ".": "operador de acceso a método o atributo",
    "&": "operador de referencia",
    "|": "operador de unión",
    "^": "operador de intersección",
    "~": "operador de complemento",
    "<<": "operador de desplazamiento a la izquierda",
    ">>": "operador de desplazamiento a la derecha",
    "=>": "operador de hash rocket",
    "#": "operador de comentario"
}

palabrasReservadas = {  # palabras reservadas básicas de Ruby
    "require": "importar librerias",
    "if": "condicional if",
    "elsif": "condicional elsif",
    "else": "condicional else",
    "True": "valor booleano verdadero",
    "False": "valor booleano falso",
    "unless": "condicional unless",
    "while": "bucle while",
    "until": "bucle until",
    "for": "bucle for",
    "in": "pertenencia / iteración in",
    "do": "inicio de bloque do",
    "def": "definición de método",
    "return": "retorno de método",
    "end": "fin de bloque",
    "class": "definición de clase",
    "module": "definición de módulo",
    "begin": "inicio de manejo de excepciones",
    "rescue": "captura de excepciones",
    "ensure": "bloque que siempre se ejecuta",
    "case": "estructura case",
    "when": "condición en case",
    "then": "ejecución en condicional",
    "break": "salir de bucle",
    "next": "saltar a la siguiente iteración",
    "redo": "repetir iteración actual",
    "retry": "reintentar bloque",
    "yield": "llamada a bloque asociado",
    "super": "llamada al método de la superclase",
    "self": "referencia al objeto actual",
    "alias": "crear alias de método o variable",
    "and": "operador lógico and",
    "or": "operador lógico or",
    "not": "operador lógico not",
    "true": "valor booleano verdadero",
    "false": "valor booleano falso",
    "nil": "valor nulo",
    "__FILE__": "nombre del archivo actual",
    "__LINE__": "número de línea actual"
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

metodos = {
    "puts": "método para imprimir en consola",
    "print": "método para imprimir sin salto de línea",
    "gets": "método para leer entrada del usuario",
    "chomp": "método para eliminar el salto de línea al final de una cadena",
    "to_i": "método para convertir a entero",
    "to_s": "método para convertir a cadena",
    "to_f": "método para convertir a flotante",
    "length": "método para obtener la longitud de una cadena o arreglo",
    "size": "método para obtener el tamaño de un arreglo",
    "each": "método para iterar sobre elementos de un arreglo o hash",
    "map": "método para transformar elementos de un arreglo",
    "times": "método para ejecutar un bloque un número específico de veces",
    "class": "método para obtener la clase de un objeto"
}

tokensEncontrados = []

def validarIdentificador(token):
    patron = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return re.match(patron, token) is not None

def identificarString(token):
    patron = r'^"(?:\\.|[^"\\])*"$|^\'(?:\\.|[^\'\\])*\'$'
    return re.match(patron, token) is not None

def tokenizar(linea):
    patron = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\*\*|\|\|=|===|==|!=|>=|<=|<=>|\+\+|\+=|-=|\*=|/=|%=|\|\||&&|\.\.\.|\.\.|::|=>|<<|>>|[(){}\[\];,=+\-*/%?!:&|^~<>.]|[a-zA-Z_]\w*|\d+\.\d+|\d+|[^\s]'
    tokens = re.findall(patron, linea)
    return tokens

def clasificarToken(token):
    
    if token in palabrasReservadas:
        return "palabra reservada", palabrasReservadas[token]

    if token in operadores:
        return "operador", operadores[token]
    
    if token in simbolos:
        return "simbolo", simbolos[token]
    
    if token in metodos:
        return "metodo", metodos[token]
    
    if re.match(r'^\d+\.\d+$', token):
        return "numero", "número flotante"
    
    if re.match(r'^\d+$', token):
        return "numero", "número entero"
    
    if validarIdentificador(token):
        return "identificador", "nombre de variable o función"
    
    if identificarString(token):
        return "cadena", "cadena de texto"
    
    return "invalido", "token no reconocido"

class Token: #clase para representar los tokens con su tipo y valor
    def __init__(self, type, value, linea=0):
        self.type = type
        self.value = value
        self.linea = linea

    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', linea={self.linea})"
    
def generar_tokens(codigo):
    tokens_parser=[]
    numero_linea = 1 #contador para la linea actual
    for linea in codigo.splitlines():
        lin = linea.strip()
        if not lin or lin.startswith("#"):
            numero_linea += 1
            continue

        tokens_crudos = tokenizar(lin)
        for t in tokens_crudos:
            categoria, descripcion= clasificarToken(t)
            if categoria == "numero": tipo = "Numero"
            elif categoria == "simbolo": tipo = "Simbolo"
            elif categoria == "metodo": tipo = "Metodo"
            elif categoria == "identificador": tipo = "Identificador"
            elif categoria == "palabra reservada": tipo = "PalabraReservada"
            elif categoria == "operador": tipo = "Operador"
            elif categoria == "cadena": tipo = "Cadena"
            else: tipo = "Invalido"

            tokens_parser.append(Token(tipo, t, linea=numero_linea))
        numero_linea += 1
        
    tokens_parser.append(Token("Fin", "", linea=numero_linea))
    return tokens_parser
