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
            raise Exception(f"Token inseperado: {self.token_actual.value}, se esperaba: {esperado}")

    def parse(self): #función principal para iniciar el proceso de parseo
        return self.bolque_instrucciones(parse_principal=True)

    def bolque_instrucciones(self, parse_principal=False): #función para procesar un bloque de instrucciones
        nodo_raiz = self.instruccion()

        while self.token_actual.type != 'Fin':
            if not parse_principal and self.token_actual.type == 'PalabraReservada' and self.token_actual.value in ['end', 'else', 'elsif']:
                break
            siguiente_inst = self.instruccion()
            if siguiente_inst:
                conexion = TreeNode(Token('Conector', '->'))
                conexion.left = nodo_raiz
                conexion.right = siguiente_inst
                nodo_raiz = conexion
        return nodo_raiz

    def instruccion(self): #procesa una instrucción
        if self.token_actual.type == 'Identificador':
            posicion_guardada = self.posicion #guarda la posición actual
            self.next_token()
            es_asignacion = (self.token_actual.type == 'Operador' and self.token_actual.value == '=')

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
        
        elif self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'if':
            return self.condicional_if()
        
        return self.expr() #si no es un identificador ni un método, se trata de una expresión

    def condicional_if(self): #procesa una estructura condicional if
        token_if = self.token_actual
        self.eat('PalabraReservada', 'if')
        nodo_if = TreeNode(token_if)
        nodo_if.left = self.condicion()

        nodo_ramas = TreeNode(Token('Conector', 'Ramas'))
        nodo_ramas.left = self.bolque_instrucciones()
        #procesa las ramas elsif
        if self.token_actual.type == 'PalabraReservada' and self.token_actual.value == 'else':
            self.eat('PalabraReservada', 'else')
            nodo_ramas.right = self.bolque_instrucciones()

        self.eat('PalabraReservada', 'end')
        nodo_if.right = nodo_ramas
        return nodo_if
    
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
        nodo_id = TreeNode(self.token_actual)
        self.eat('Identificador')
        nodo_asignacion = TreeNode(self.token_actual)
        self.eat('Operador', '=')
        nodo_asignacion.left = nodo_id #el lado izquierdo de la asignación es el identificador
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
        
        while self.token_actual.type == 'Operador' and self.token_actual.value in ('*', '/'):
            token = self.token_actual
            self.eat('Operador')
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.factor() #hijo derecho es el siguiente factor
            node = new_node
        
        return node
    
    def factor(self): #funcion para procesar los tokens
        token = self.token_actual
        
        if token.type == "Numero": #procesa un número creando un nodo para ese número
            self.eat("Numero")
            return TreeNode(token)
        elif token.type == "Identificador": #procesa un identificador creando un nodo para ese identificador
            self.eat("Identificador")
            return TreeNode(token)
        elif token.type == "Simbolo" and token.value == "(": #procesa una expresión entre paréntesis creando un nodo para esa expresión
            self.eat("Simbolo", "(")
            node = self.expr()
            self.eat("Simbolo", ")")
            return node
        elif token.type == "String": #procesa una cadena de texto creando un nodo para esa cadena
            self.eat("String")
            return TreeNode(token)
        else:
            valor_error = self.token_actual.value
            self.next_token() #avanza al siguiente token para evitar un bucle infinito
            raise Exception(f"Sintaxis invalida en token: {valor_error}")
