class Token: #clase para definir los tokens que el lexer va a generar, con un tipo y un valor
    class Type:
        Numero = 'Numero'
        Suma = 'Suma'
        Resta = 'Resta'
        Multiplica = 'Multiplica'
        Divide = 'Divide'
        ParentesisAbre = 'ParentesisAbre'
        ParentesisCierra = 'ParentesisCierra'
        Fin = 'Fin'
        Invalido = 'Invalido'

    def __init__(self, type, value): #constructor para inicializar el token con su tipo y valor
        self.type = type
        self.value = value

class Lexer: #clase para analizar la cadena de entrada y generar tokens
    def __init__(self, origen):
        self.origen = origen
        self.index = 0
    
    def next_token(self): #función para obtener el siguiente token de la cadena de entrada
        while self.index < len(self.origen) and self.origen[self.index].isspace():
            self.index += 1 #ignorar espacios en blanco
        
        if self.index >= len(self.origen):  #verificar si se ha llegado al final de la cadena de entrada
            return Token(Token.Type.Fin, "")
        
        entrada_actual = self.origen[self.index]
        
        if entrada_actual.isdigit(): #reconocer números
            num = ""
            while self.index < len(self.origen) and self.origen[self.index].isdigit():
                num += self.origen[self.index]
                self.index += 1
            return Token(Token.Type.Numero, num)
        
        self.index += 1
        
        #reconocer operadores y paréntesis
        if entrada_actual == '+':
            return Token(Token.Type.Suma, entrada_actual)
        elif entrada_actual == '-':
            return Token(Token.Type.Resta, entrada_actual)
        elif entrada_actual == '*':
            return Token(Token.Type.Multiplica, entrada_actual)
        elif entrada_actual == '/':
            return Token(Token.Type.Divide, entrada_actual)
        elif entrada_actual == '(':
            return Token(Token.Type.ParentesisAbre, entrada_actual)
        elif entrada_actual == ')':
            return Token(Token.Type.ParentesisCierra, entrada_actual)
        else:
            return Token(Token.Type.Invalido, entrada_actual)
        
class TreeNode: #clase para representar los nodos del arbol
    def __init__(self, token):#constructor para inicializar el nodo con un token y referencias a los hijos izquierdo y derecho
        self.token = token
        self.left = None
        self.right = None
    
    def __repr__(self):#representación del nodo en string para facilitar la depuración
        return f"TreeNode({self.token.type}, {self.token.value})"
    
    def print_tree(self, level=0):#función para imprimir el arbol
        indent = "  " * level
        
        if self.right: #imprime el hijo derecho
            self.right.print_tree(level + 1)
        
        if self.token.type == Token.Type.Numero: #imprime el valor del número si el token es un número
            print(f"{indent}Número: {self.token.value}")
        else:
            print(f"{indent}Operador: {self.token.value}")
        
        if self.left: #imprime el hijo izquierdo
            self.left.print_tree(level + 1)

class Parser: #clae para el parseo
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_actual = self.lexer.next_token()
    
    def parse(self): #función principal para iniciar el proceso de parseo
        return self.expr()
    
    def expr(self): #procesa suma y resta (menor precedencia)
        node = self.termino()
        
        while self.token_actual.type in (Token.Type.Suma, Token.Type.Resta):
            token = self.token_actual
            self.eat(token.type)
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.termino() #hijo derecho es el siguiente término
            node = new_node
        
        return node #devuelve el nodo raíz del árbol sintáctico generado a partir de la expresión de entrada
        
    def termino(self): #procesa multiplicación y división, creando nodos para cada operador y conectándolos con los factores correspondientes
        node = self.factor() #comienza con el primer factor
        
        while self.token_actual.type in (Token.Type.Multiplica, Token.Type.Divide):
            token = self.token_actual
            self.eat(token.type)
            new_node = TreeNode(token)
            new_node.left = node
            new_node.right = self.factor() #hijo derecho es el siguiente factor
            node = new_node
        
        return node
    
    def factor(self): #procesa números y expresiones entre parentesis
        token = self.token_actual
        
        if token.type == Token.Type.Numero:
            self.eat(Token.Type.Numero)
            return TreeNode(token)
        elif token.type == Token.Type.ParentesisAbre:
            self.eat(Token.Type.ParentesisAbre)
            node = self.expr()  # expresión dentro de paréntesis
            self.eat(Token.Type.ParentesisCierra)
            return node
        else:
            raise Exception(f"Token inesperado: {token.type} con valor '{token.value}'")

    def eat(self, token_type): #verifica que el token actual sea del tipo esperado y avanza al siguiente token
        if self.token_actual.type == token_type:
            self.token_actual = self.lexer.next_token()
        else:
            raise Exception(f"Token inesperado: {self.token_actual.type}, se esperaba: {token_type}")
        
if __name__ == "__main__":
    expresion1 = "9*4/5-7+1*3+2"
    expresion2 = "(3+5)*2"
    expresion3 = "10/(2+3)"
    expresion4 = "7-4*2"
    expresion5 = "8/(4-2)"
    print(f"\nExpresión: {expresion3}")
    print("\nÁrbol Sintáctico:")
    
    lexer = Lexer(expresion3)
    parser = Parser(lexer)
    arbol_sintactico = parser.parse()
    arbol_sintactico.print_tree()
    