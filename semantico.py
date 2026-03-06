class Semantico:
    def __init__(self):
        self.tabla_simbolos = {} #tabla de simbolos para almacenar las variables declaradas y sus tipos
        self.errores = [] #lista para almacenar los errores semanticos encontrados

    def analizar(self, nodo_raiz):
        self.tabla_simbolos = {} #reiniciar la tabla de simbolos para cada análisis
        self.errores = [] #reiniciar la lista de errores para cada análisis
        self.visitar(nodo_raiz)
        return self.errores, self.tabla_simbolos
    
    def visitar(self, nodo):
        if nodo is None:
            return None
        
        tipo_token= nodo.token.type
        valor = nodo.token.value
        linea = getattr(nodo.token, 'linea', 0) #obtener la linea del token, si no existe usa 0

        #regla de conector: <instrucción> -> <instrucción>
        if tipo_token == 'Conector' and valor in ['->', 'Ramas']:
            self.visitar(nodo.left)
            self.visitar(nodo.right)
            return None
        elif tipo_token == 'Numero': #regla de numero: <valor> = <número>
            return 'Número'
        elif tipo_token == 'String': #regla de string: <valor> = <string>
            return 'String'
        elif tipo_token == 'Identificador': #regla de identificador: <id> en tabla de simbolos
            if valor not in self.tabla_simbolos:
                self.errores.append((f"Error semántico: Variable '{valor}' no declarada.", linea))
                return None
            return self.tabla_simbolos[valor]
        elif tipo_token == 'Operador' and valor == '=': #regla de asignación: <id> = <expresión>
            nombre_var = nodo.left.token.value
            tipo_der = self.visitar(nodo.right)
            if tipo_der != 'Error':
                self.tabla_simbolos[nombre_var] = tipo_der
            return tipo_der
        elif tipo_token == 'Operador' and valor in ('+', '-', '*', '/'): #regla de operación aritmética: <expresión> <operador> <expresión>
            tipo_izq = self.visitar(nodo.left)
            tipo_der = self.visitar(nodo.right)

            if tipo_izq == 'Error' or tipo_der == 'Error':
                return 'Error'
            if tipo_izq != 'Número' or tipo_der != 'Número':
                self.errores.append((f"Error semántico: Operación '{valor}' no soportada entre tipos '{tipo_izq}' y '{tipo_der}'.", linea))
                return 'Error'
            return 'Número'
        elif tipo_token == 'Metodo': #regla de método: <metodo><argumentos>
            if nodo.left:
                self.visitar(nodo.left) #visitar los argumentos del método
            return None
        elif tipo_token == 'Operador' and valor in ('==', '!=', '<', '>', '<=', '>='): #regla de comparación: <expresión> <operador_comparación> <expresión>
            tipo_izq = self.visitar(nodo.left)
            tipo_der = self.visitar(nodo.right)

            if tipo_izq == 'Error' or tipo_der == 'Error':
                return 'Error'
            if tipo_izq != tipo_der:
                self.errores.append((f"Error semántico: Comparación '{valor}' no soportada entre tipos '{tipo_izq}' y '{tipo_der}'.", linea))
                return 'Error'
            return 'Booleano'
        elif tipo_token == 'PalabraReservada' and valor == 'if': #regla de if: if <condición>
            tipo_condicion = self.visitar(nodo.left) #visitar la condición del if
            if tipo_condicion != 'Error' and tipo_condicion != 'Booleano':
                self.errores.append((f"Error semántico: Condición del 'if' debe ser de tipo 'Booleano', no '{tipo_condicion}'.", linea))

            self.visitar(nodo.right)
            return None

        return None