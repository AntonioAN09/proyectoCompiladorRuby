
class GeneradorCodigo:
    def __init__(self):
        self.codigo = []

    def generador(self, nodo_raiz):
        self.codigo = []  #reiciar el código generado para cada análisis
        self.codigo.append("Iniciando gneración de código...")
        self.visitar(nodo_raiz)
        self.codigo.append("Código generado exitosamente.")
        return self.codigo
    
    def visitar(self, nodo):
        if nodo is None:
            return

        tipo = nodo.token.type
        valor = nodo.token.value
        #conectores
        if tipo == 'Conector' and valor in ['->', 'Ramas']:
            self.visitar(nodo.left)
            self.visitar(nodo.right)
        #asignacion
        elif tipo == 'Operador' and valor == '=':
            nombre_var = nodo.left.token.value
            self.codigo.append(f"Push variable: {nombre_var}")
            self.visitar(nodo.right)
            self.codigo.append("Almacenando valor")
        #constantes y numeros
        elif tipo == 'Numero':
            self.codigo.append(f"Push constante: {valor}")
        elif tipo in ['Cadena', 'Cadena']:
            self.codigo.append(f"Push string: {valor}")
        #expresiones
        elif tipo == 'Identificador':
            self.codigo.append(f"Cargando variable: {valor}")
        #operaciones matematicas
        elif tipo == 'Operador' and valor in ['+', '-', '*', '/']:
            self.visitar(nodo.left)
            self.visitar(nodo.right)
            
            if valor == '+':
                self.codigo.append("Suma")
            elif valor == '-':
                self.codigo.append("Negar")
                self.codigo.append("Suma (add)")
            elif valor == '*':
                self.codigo.append("Multiplicar (mul)")
            elif valor == '/':
                self.codigo.append("Dividir (div)")
        #metodos
        elif tipo == 'Metodo':
            if valor in ['puts', 'print']:
                if nodo.left:
                    self.visitar(nodo.left)
                self.codigo.append("Salida de consola")
            elif valor == 'gets':
                self.codigo.append("Entrada de usuario")
        #condicional if
        elif tipo == 'PalabraReservada' and valor == 'if':
            self.codigo.append("-- Evaluando Condición If --")
            self.visitar(nodo.left) 
            self.codigo.append("Saltar si falso a FIN_IF")
            self.codigo.append("-- Bloque If Verdadero --")
            self.visitar(nodo.right) 
            self.codigo.append("-- Fin del bloque If --")
        #condicional else
        elif tipo == 'PalabraReservada' and valor == 'else':
            self.codigo.append("-- Evaluando Condición Else --")
            self.visitar(nodo.left) 
            self.codigo.append("Saltar si falso a FIN_ELSE (jmpf)")
            self.codigo.append("-- Bloque Else Verdadero --")
            self.visitar(nodo.right) 
            self.codigo.append("-- Fin del bloque Else --")
        #condicional while
        elif tipo == 'PalabraReservada' and valor == 'while':
            self.codigo.append("-- Inicio del bucle While --")
            self.visitar(nodo.left) 
            self.codigo.append("Saltar si falso a FIN_WHILE (jmpf)")
            self.codigo.append("-- Bloque While Verdadero --")
            self.visitar(nodo.right) 
            self.codigo.append("Saltar al inicio del While (jmp)")
            self.codigo.append("-- Fin del bucle While --")

def errores(self, codigo):
    print(f"Línea {self.lexico.lineaActual()}: Error de sintaxis: {codigo}")
    mensajes_error = {
        1: " :Esperaba un )",
        2: " :Esperaba un ]",
        3: " :Esperaba un }",
        4: " :Esperaba un identificador",
        5: " :Esperaba un número",
        6: " :Esperaba una cadena",
        7: " :Esperaba un operador (+,-,*,/)",
        8: " :Esperaba una palabra reservada",
        9: " :Esperaba un conector",
        10: " :Esperaba un operador lógico",
        11: " :Esperaba un método",
        12: " :Esperaba un =",
        13: " :Esperaba un if",
        14: " :Esperaba un else",
        15: " :Esperaba un while"
    }
    return mensajes_error.get(codigo, " :Error de sintaxis desconocido")
