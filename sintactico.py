from lexico import Token

class TreeNode: #clase para representar los nodos del arbol
    def __init__(self, token):#constructor para inicializar el nodo con un token y referencias a los hijos izquierdo y derecho
        self.token = token
        self.left = None
        self.right = None
    
    def __repr__(self):#representación del nodo en string para facilitar la depuración
        return f"TreeNode({self.token.type}, {self.token.value})"
    
    def print_tree(self, prefix="", is_left=True, is_root=True):#función para imprimir el arbol
        resultado = ""
        
        if self.right: #imprime el hijo derecho
            new_prefix = prefix + ("│   " if is_left and not is_root else "    ")
            resultado += self.right.print_tree(new_prefix, False, False)

        if is_root:
            resultado += f"Raiz ── {self.token.value}\n"
        else:
            conector = "└── " if is_left else "┌── "
            resultado += f"{prefix}{conector}{self.token.value}\n"
    
        if self.left: #imprime el hijo izquierdo
            new_prefix = prefix + ("    " if is_left and not is_root else "│   ")
            resultado += self.left.print_tree(new_prefix, True, False)
        
        return resultado

class Parser: #clase para el parseo
    def __init__(self, lista_tokens):
        self.tokens = lista_tokens
        self.posicion = 0
        self.token_actual = self.tokens[self.posicion] if self.tokens else Token('Fin', "")
    
    def next_token(self): #función para avanzar al siguiente token
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = Token('Fin', "")
        return self.token_actual

    def eat(self, token_type, token_value=None): #función para consumir un token esperado, verificando su tipo y valor
        if self.token_actual.type == token_type and (token_value is None or self.token_actual.value == token_value):
            self.next_token()
        else:
            esperado = token_value if token_value else token_type
            linea = getattr(self.token_actual, 'linea', 0) #obtener la linea del token actual para el mensaje de error
            raise Exception(f"Linea {linea} | Token inseperado: {self.token_actual.value}, se esperaba: {esperado}")

    def parse(self): #función principal para iniciar el proceso de parseo
        return self.bolque_instrucciones(parse_principal=True)

    def bolque_instrucciones(self, parse_principal=False): #función para procesar un bloque de instrucciones
        nodo_raiz = self.instruccion()

        while self.token_actual.type != 'Fin':
            if not parse_principal and self.token_actual.type == 'PalabraReservada' and self.token_actual.value in ['end', 'else', 'elsif', 'when']:
                break
            siguiente_inst = self.instruccion()
            if siguiente_inst:
                conexion = TreeNode(Token('Conector', '->'))
                conexion.left = nodo_raiz
                conexion.right = siguiente_inst
                nodo_raiz = conexion
        return nodo_raiz

    def instruccion(self): #procesa una instrucción
        if self.token_actual.type in ['Identificador', 'Numero', 'Cadena']:
            posicion_guardada = self.posicion #guarda la posición actual
            
            self.next_token()
            while True: #while para manejar los arrglos
                if self.token_actual.type == 'Simbolo' and self.token_actual.value == '[':
                    self.next_token()
                    while self.token_actual.type != 'Simbolo' or self.token_actual.value != ']':
                        if self.token_actual.type == 'Fin': break #evitamos los bucles infinitos
                        self.next_token()
                    self.next_token() #consumimos el ']'

                elif self.token_actual.type == 'Operador' and self.token_actual.value == '.':
                    self.next_token() #consume el '.'
                    self.next_token() #consume el siguiente token después del '.'
                else: break
            
            es_asignacion = (self.token_actual.type == 'Operador' and self.token_actual.value in ['=', '+=', '-=', '*=', '/=', '%='])

            self.posicion = posicion_guardada #restaura la posición guardada
            self.token_actual = self.tokens[self.posicion] #restaura el token actual

            if es_asignacion:
                return self.asignacion()
            else:
                return self.expr() #si no es una asignación, se trata de una expresión
            
        elif self.token_actual.type =='Metodo':
            token_metodo = self.token_actual
            self.eat('Metodo')
            nodo_metodo = TreeNode(token_metodo)

            if self.token_actual.type not in ['Fin', 'PalabraReservada', 'Metodo']:
                nodo_metodo.left = self.expr()
            return nodo_metodo
        #manejo para la importación de librerías con require
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'require':
            token_req = self.token_actual
            self.eat('PalabraReservada', 'require')
            nodo_req = TreeNode(token_req)
            nodo_req.left = self.factor() #nombre de la librería a importar
            return nodo_req
        
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'if':
            return self.condicional_if()
        
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'case':
            return self.estructura_case()
        
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'while':
            return self.bucle_while()
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'for':
            return self.bucle_for()
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value in ['True', 'False', 'false', 'true']:
            token_booleano = self.token_actual
            self.eat('PalabraReservada')
            return TreeNode(token_booleano)
        
        return self.expr() #si no es un identificador ni un método, se trata de una expresión

    def condicional_if(self): #procesa condicional if
        token_if = self.token_actual
        self.eat('PalabraReservada', 'if')
        nodo_if = TreeNode(token_if)
        nodo_if.left = self.condicion()

        nodo_ramas = TreeNode(Token('Conector', 'Ramas'))
        nodo_ramas.left = self.bolque_instrucciones()
        
        actual_ramas = nodo_ramas

        #procesa múltiples elsif
        while self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'elsif':
            token_elsif = self.token_actual
            self.eat('PalabraReservada', 'elsif')
            nodo_elsif = TreeNode(token_elsif)
            nodo_elsif.left = self.condicion()
            
            nuevo_ramas = TreeNode(Token('Conector', 'Ramas'))
            nuevo_ramas.left = self.bolque_instrucciones()
            nodo_elsif.right = nuevo_ramas
            
            actual_ramas.right = nodo_elsif
            actual_ramas = nuevo_ramas

        #procesa la rama else
        if self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'else':
            self.eat('PalabraReservada', 'else')
            actual_ramas.right = self.bolque_instrucciones()

        self.eat('PalabraReservada', 'end')
        nodo_if.right = nodo_ramas
        return nodo_if
    
    def estructura_case(self): #procesa la estructura para el switch/case
        token_case = self.token_actual
        self.eat('PalabraReservada', 'case')
        nodo_case = TreeNode(token_case)
        nodo_case.left = self.expr()
        actual_nodo = nodo_case
        while self .token_actual.type == 'PalabraReservada' and self.token_actual.value == 'when':
            token_when = self.token_actual
            self.eat('PalabraReservada', 'when')
            nodo_when= TreeNode(token_when)
            nodo_when.left = self.expr()
            nodo_ramas = TreeNode(Token('Conector', 'Ramas'))
            nodo_ramas.left = self.bolque_instrucciones()
            nodo_when.right = nodo_ramas
            actual_nodo.right = nodo_when
            actual_nodo = nodo_ramas

        if self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'else':
            self.eat('PalabraReservada', 'else')
            actual_nodo.right = self.bolque_instrucciones()
        
        self.eat('PalabraReservada', 'end')
        return nodo_case
    
    def bucle_while(self):
        token = self.token_actual
        self.eat('PalabraReservada', 'while')
        nodo_while = TreeNode(token)
        nodo_while.left = self.condicion()
        nodo_while.right = self.bolque_instrucciones()
        self.eat('PalabraReservada', 'end')
        return nodo_while
    
    def bucle_for(self):
        token_for = self.token_actual
        self.eat('PalabraReservada', 'for')
        nodo_for = TreeNode(token_for)

        token_iterador = self.token_actual #para el iterador del for
        self.eat('Identificador')
        nodo_iterador = TreeNode(token_iterador)
        self.eat('PalabraReservada', 'in')
        nodo_rango = self.expr() #para el rango del for

        if self.token_actual.type == 'Operador' and self.token_actual.value == '..':
            token_puntos = self.token_actual
            self.eat('Operador', '..')
            nuevo_rango = TreeNode(token_puntos)
            nuevo_rango.left = nodo_rango
            nuevo_rango.right = self.expr() #rango superior del for
            nodo_rango = nuevo_rango

        nodo_iteracion = TreeNode(Token('Conector', 'Iteracion'))
        nodo_iteracion.left = nodo_iterador
        nodo_iteracion.right = nodo_rango

        nodo_for.left = nodo_iteracion
        nodo_for.right = self.bolque_instrucciones()

        self.eat('PalabraReservada', 'end')
        return nodo_for


    def condicion(self): #procesa una condición
        nodo = self.expr() #comienza con una expresión
        if self.token_actual.type == 'Operador' and self.token_actual.value in ('==', '!=', '<', '>', '<=', '>='):
            token_op = self.token_actual
            self.eat('Operador')
            new_nodo = TreeNode(token_op)
            new_nodo.left = nodo
            new_nodo.right = self.expr() #hijo derecho es la siguiente expresión
            nodo = new_nodo
        return nodo

    def asignacion(self): #procesa una asignación
        nodo_izq = self.factor() #el lado izq puede ser un id o un id[expr]
        
        token_operador = self.token_actual
        nodo_asignacion = TreeNode(self.token_actual)
        self.eat('Operador')
        nodo_asignacion.left = nodo_izq #el lado izquierdo de la asignación es el identificador
        nodo_asignacion.right = self.expr() #el lado derecho de la asignación es una expresión
        return nodo_asignacion


    def expr(self): #procesa suma y resta 
        node = self.termino() #comienza con el primer término
        
        while self.token_actual.type == 'Operador' and self.token_actual.value in ('+', '-'):
            token = self.token_actual
            self.eat('Operador')
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.termino() #hijo derecho es el siguiente término
            node = new_node
        
        return node #devuelve el nodo raíz del árbol sintáctico generado a partir de la expresión de entrada
        
    def termino(self): #procesa multiplicación y división, creando nodos para cada operador y conectándolos con los factores correspondientes
        node = self.factor() #comienza con el primer factor
        
        while self.token_actual.type == 'Operador' and self.token_actual.value in ('*', '/', '%'):
            token = self.token_actual
            self.eat('Operador')
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.factor() #hijo derecho es el siguiente factor
            node = new_node
        return node
    
    def operadores_asignacion(self):
        operador = self.token_actual.value[0] #obtener el operador base (+, -, *, /, %)
        if operador == '+':
            token_op = Token('Operador', '+=')
        elif operador == '-':
            token_op = Token('Operador', '-=')
        elif operador == '*':
            token_op = Token('Operador', '*=')
        elif operador == '/':
            token_op = Token('Operador', '/=')
        elif operador == '%':
            token_op = Token('Operador', '%=')
        else:
            linea = getattr(self.token_actual, 'linea', 0)
            raise Exception(f"Linea {linea} | Operador de asignación no reconocido: {self.token_actual.value}")
    
    def factor(self): #funcion para procesar los tokens
        token = self.token_actual
        
        if token.type == "Numero": #procesa un número creando un nodo para ese número
            self.eat("Numero")
            return TreeNode(token)
        
        elif token.type == "Identificador": #procesa un identificador creando un nodo para ese identificador
            self.eat("Identificador")
            nodo_id = TreeNode(token)
        
            while self.token_actual.type in ['Simbolo', 'Operador'] and self.token_actual.value in ['.', '[']:
                if self.token_actual.value == '[':
                    self.eat('Simbolo', '[')
                    nodo_acceso = TreeNode(Token('Operador', '[]'))
                    nodo_acceso.left = nodo_id
                    nodo_acceso.right = self.expr() #el índice del arreglo
                    self.eat('Simbolo', ']')
                    nodo_id = nodo_acceso
                elif self.token_actual.value == '.':
                    token_punto = self.token_actual
                    self.eat('Operador', '.')
                    nodo_punto = TreeNode(token_punto)
                    nodo_punto.left = nodo_id
                    nodo_punto.right = TreeNode(self.token_actual) #el método o propiedad después del punto
                    if self.token_actual.type in ['Identificador', 'Metodo']:
                        self.eat(self.token_actual.type) #consume el token del método o propiedad
                    else:
                        self.eat('Identificador') #si no es un método es id
                    nodo_id = nodo_punto
            return nodo_id
        
        elif token.type == "Simbolo" and token.value == "(": #procesa una expresión entre paréntesis creando un nodo para esa expresión
            self.eat("Simbolo", "(")
            if self.token_actual.type == 'Simbolo' and self.token_actual.value == ')': #maneja el caso de paréntesis vacíos
                self.eat("Simbolo", ")")
                return TreeNode(Token("Parametros", "()")) #crea un nodo especial para paréntesis vacíos
            node = self.expr()
            self.eat("Simbolo", ")")
            return node
        
        elif token.type == 'Simbolo' and token.value == '[': #procesa una expresión entre corchetes creando un nodo para esa expresión
            self.eat('Simbolo', '[')
            nodo_arreglo = TreeNode(Token('Arreglo', '[]'))

            if self.token_actual.type == 'Simbolo' and self.token_actual.value == ']': #maneja el caso de corchetes vacíos
                self.eat('Simbolo', ']')
                return nodo_arreglo #devuelve el nodo de arreglo vacío
            
            nodo = self.expr()
            #procesa los elementos del arreglo separados por comas
            while self.token_actual.type == 'Simbolo' and self.token_actual.value == ',':
                token_coma = self.token_actual
                self.eat('Simbolo', ',')
                nodo_coma = TreeNode(token_coma)
                nodo_coma.left = nodo
                nodo_coma.right = self.expr() #el siguiente elemento del arreglo
                nodo = nodo_coma

            nodo_arreglo.left = nodo
            self.eat('Simbolo', ']')
            return nodo_arreglo
        
        elif token.type == 'Simbolo' and token.value == '{': #procesa una expresión entre llaves creando un nodo para esa expresión
            self.eat('Simbolo', '{')
            if self.token_actual.type == 'Simbolo' and self.token_actual.value == '}': #maneja el caso de llaves vacías
                self.eat('Simbolo', '}')
                return TreeNode(Token("Bloque", "{}")) #crea un nodo especial para llaves vacías
            node = self.expr()
            self.eat('Simbolo', '}')
            return node
        
        elif token.type == "Cadena": #procesa una cadena de texto creando un nodo para esa cadena
            self.eat("Cadena")
            return TreeNode(token)
        else:
            valor_error = self.token_actual.value
            linea = getattr(self.token_actual, 'linea', 0) #obtener la linea del token actual para el mensaje de error
            self.next_token() #avanza al siguiente token para evitar un bucle infinito
            raise Exception(f"Linea {linea} | Sintaxis invalida en token: {valor_error}")

