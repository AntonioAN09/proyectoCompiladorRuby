class Semantico:
    def __init__(self):
        self.tabla_simbolos = {} #tabla de simbolos para almacenar las variables declaradas y sus tipos
        self.errores = [] #lista para almacenar los errores semanticos encontrados

    def registrar_simbolo(self, nombre, tipo, descripcion, bytes):
        self.tabla_simbolos[nombre] = {
            'tipo': tipo,
            'descripcion': descripcion,
            'bytes': bytes
        }

    def analizar(self, nodo_raiz):
        self.tabla_simbolos = {} #reiniciar la tabla de simbolos para cada análisis
        self.errores = [] #reiniciar la lista de errores para cada análisis
        self.visitar(nodo_raiz)
        return self.errores, self.tabla_simbolos
    
    def visitar(self, nodo):
        if nodo is None:
            return ('None', 0)
        
        tipo_token= nodo.token.type
        valor = nodo.token.value
        linea = getattr(nodo.token, 'linea', 0) #obtener la linea del token, si no existe usa 0
        
        if tipo_token == 'Operador':
            self.registrar_simbolo(valor, 'operador', "Operador", 1)
        elif tipo_token == 'Simbolo':
            self.registrar_simbolo(valor, 'símbolo', "Símbolo", 1)
        elif tipo_token == 'PalabraReservada':
            self.registrar_simbolo(valor, 'palabra_res', "Palabra Reservada", len(valor))

        #regla de conector: <instrucción> -> <instrucción>
        if tipo_token == 'Conector' and valor in ['->', 'Ramas']:
            self.visitar(nodo.left)
            self.visitar(nodo.right)
            return ('None', 0)
        
        elif tipo_token == 'Numero': #regla de numero: <valor> = <número>
            if '.' in valor:
                return ('double', 8) #número flotante
            else:
                return ('int', 4) #número entero
        
        elif tipo_token == 'Cadena': #regla de string: <valor> = <string>
            tamano= len(valor) - 2 #restar las comillas
            return ('string', tamano)
        
        elif tipo_token == 'Identificador': #regla de identificador: <id> en tabla de simbolos
            if valor not in self.tabla_simbolos:
                self.errores.append((f"Error semántico: Variable '{valor}' no declarada.", linea))
                return ('Error', 0)
            info_variable = self.tabla_simbolos[valor]
            return (info_variable['tipo'], info_variable['bytes'])
        
        elif tipo_token == 'Operador' and valor == '=': #regla de asignación: <id> = <expresión>
            self.registrar_simbolo(valor, 'operador', 'asignacion', 1)
            nodo_izq = nodo.left
            tipo_der, bytes_der = self.visitar(nodo.right)
            if nodo_izq.token.type != 'Identificador':
                self.errores.append((f"Error semántico: No se puede tener <expr> = <valor>, debe ser <id> = <expr>.", linea))
                return ('Error', 0)
            nombre_variable = nodo_izq.token.value
            if tipo_der != 'Error':
                self.registrar_simbolo(nombre_variable, tipo_der, 'Variable', bytes_der)
            return (tipo_der, bytes_der)

        elif tipo_token == 'Operador' and valor in ('+', '-', '*', '/'): #regla de operación aritmética: <expresión> <operador> <expresión>
            tipo_izq, bytes_izq = self.visitar(nodo.left)
            tipo_der, bytes_der = self.visitar(nodo.right)

            if tipo_izq == 'Error' or tipo_der == 'Error':
                return ('Error', 0)
            if tipo_izq not in ['int', 'double'] or tipo_der not in ['int', 'double']:
                self.errores.append((f"Error semántico: Operación '{valor}' no soportada entre tipos '{tipo_izq}' y '{tipo_der}'.", linea))
                return ('Error', 0)
            if tipo_izq == 'double' or tipo_der == 'double':
                return ('double', 8)
            return ('int', 4)
        
        elif tipo_token == 'Metodo': #regla de método: <metodo><argumentos>
            if nodo.left:
                self.visitar(nodo.left) #visitar los argumentos del método
            return ('None', 0)
        
        elif tipo_token == 'Operador' and valor in ('==', '!=', '<', '>', '<=', '>='): #regla de comparación: <expresión> <operador_comparación> <expresión>
            tipo_izq, _= self.visitar(nodo.left)
            tipo_der, _ = self.visitar(nodo.right)

            if tipo_izq == 'Error' or tipo_der == 'Error':
                return ('Error', 0)
            son_numericos = (tipo_izq in ['int', 'double']) and (tipo_der in ['int', 'double'])
            if son_numericos or (tipo_izq == tipo_der):
                return ('Booleano', 1)
            else:
                self.errores.append((f"Error semántico: Comparación '{valor}' no soportada entre tipos '{tipo_izq}' y '{tipo_der}'.", linea))
                return ('Error', 0)
        
        elif tipo_token == 'PalabraReservada' and valor == 'if': #regla de if: if <condición>
            tipo_condicion, _ = self.visitar(nodo.left) #visitar la condición del if
            if tipo_condicion != 'Error' and tipo_condicion != 'Booleano':
                self.errores.append((f"Error semántico: Condición del 'if' debe ser de tipo 'Booleano', no '{tipo_condicion}'.", linea))

            self.visitar(nodo.right)
            return ('None', 0)
        
        elif tipo_token == 'PalabraReservada' and valor == 'while': #regla de while: while <condición>
            tipo_condicion, _ = self.visitar(nodo.left) #visitar la condición del while
            if tipo_condicion != 'Error' and tipo_condicion != 'Booleano':
                self.errores.append((f"Error semántico: Condición del 'while' debe ser de tipo 'Booleano', no '{tipo_condicion}'.", linea))

            self.visitar(nodo.right)
            return ('None', 0)
        
        elif tipo_token == 'Operador' and valor in ('+=', '-=', '*=', '/=', '%='):
            nodo_izquierdo = nodo.left
            
            if nodo_izquierdo.token.type != 'Identificador':
                self.errores.append((f"Error semántico: No se puede aplicar '{valor}' a un valor literal.", linea))
                return ('Error', 0)
                
            nombre_var = nodo_izquierdo.token.value
            
            if nombre_var not in self.tabla_simbolos:
                self.errores.append((f"Error semántico: La variable '{nombre_var}' no está declarada. No se puede usar '{valor}'.", linea))
                return ('Error', 0)
                
            tipo_izq = self.tabla_simbolos[nombre_var]['tipo']
            
            tipo_der, bytes_der = self.visitar(nodo.right)
            
            if tipo_der == 'Error':
                return ('Error', 0)
                
            if tipo_izq not in ['int', 'double'] or tipo_der not in ['int', 'double']:
                self.errores.append((f"Error semántico: Operación '{valor}' no soportada entre '{tipo_izq}' y '{tipo_der}'.", linea))
                return ('Error', 0)
                
            if tipo_izq == 'double' or tipo_der == 'double':
                tipo_final = 'double'
                bytes_final = 8
            else:
                tipo_final = 'int'
                bytes_final = 4
                
            self.registrar_simbolo(nombre_var, tipo_final, "Variable", bytes_final)
            
            return (tipo_final, bytes_final)

        return ('None', 0)