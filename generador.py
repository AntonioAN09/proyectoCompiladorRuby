
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
            nodo_izq = nodo.left
            if nodo_izq.token.type == 'Identificador':
                nombre_var = nodo_izq.token.value
                self.codigo.append(f"Push variable: {nombre_var}")
            elif nodo_izq.token.type == 'Operador' and nodo_izq.token.value == '[]':
                nombre_arr = nodo_izq.left.token.value
                self.codigo.append(f"Cargar referencia arreglo: {nombre_arr}")
                self.visitar(nodo_izq.right) # Visita el índice
                self.codigo.append("Preparar índice para escritura")

            self.visitar(nodo.right)
            self.codigo.append("Almacenando valor (store)")
        #constantes y numeros
        elif tipo == 'Numero':
            self.codigo.append(f"Push constante: {valor}")
        elif tipo in ['Cadena', 'Cadena']:
            self.codigo.append(f"Push string: {valor}")
        #expresiones
        elif tipo == 'Identificador':
            self.codigo.append(f"Cargando variable: {valor}")
        #operaciones matematicas y relacionales
        elif tipo == 'Operador' and valor in ['+', '-', '*', '/', '%', '<', '>']:
            self.visitar(nodo.left)
            self.visitar(nodo.right)
            
            if valor == '+':
                self.codigo.append("Suma (add)")
            elif valor == '-':
                self.codigo.append("Negar (neg)")
                self.codigo.append("Suma (add)")
            elif valor == '*':
                self.codigo.append("Multiplicar (mul)")
            elif valor == '/':
                self.codigo.append("Dividir (div)")
            elif valor == '%':
                self.codigo.append("Módulo (mod)")
            elif valor == '<':
                self.codigo.append("Menor que (lt)")
            elif valor == '>':
                self.codigo.append("Mayor que (gt)")
        #metodos
        elif tipo == 'Metodo':
            if valor in ['puts', 'print']:
                if nodo.left:
                    self.visitar(nodo.left)
                self.codigo.append("Salida de consola")
            elif valor == 'gets':
                self.codigo.append("Entrada de usuario")
        #arreglos literales
        elif tipo == 'Arreglo':
            self.codigo.append("Instanciar nuevo Arreglo en memoria")
            if nodo.left:
                self.visitar(nodo.left) # Visitar los elementos separados por coma
            self.codigo.append("Llenar arreglo con valores iniciales")

        #lectura de indices (ej. arr[j])
        elif tipo == 'Operador' and valor == '[]':
            nombre_arr = nodo.left.token.value
            self.codigo.append(f"Cargar arreglo: {nombre_arr}")
            self.visitar(nodo.right) # El índice
            self.codigo.append("Obtener valor en índice (load_array)")

        #propiedades (ej. arr.length)
        elif tipo == 'Operador' and valor == '.':
            nombre_obj = nodo.left.token.value
            propiedad = nodo.right.token.value
            self.codigo.append(f"Cargar objeto: {nombre_obj}")
            self.codigo.append(f"Llamar propiedad/método: {propiedad}")
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
        #librerias 'require'
        elif tipo == 'PalabraReservada' and valor == 'require':
            nombre_lib = nodo.left.token.value if nodo.left else "desconocida"
            self.codigo.append(f"Importar librería: {nombre_lib}")

        #estructura case/switch
        elif tipo == 'PalabraReservada' and valor == 'case':
            self.codigo.append("-- Inicio estructura Case --")
            self.codigo.append("Cargar valor a evaluar (switch_expr)")
            self.visitar(nodo.left) 
            self.visitar(nodo.right) # Visita los 'when'
            self.codigo.append("-- Fin estructura Case --")
            
        elif tipo == 'PalabraReservada' and valor == 'when':
            self.codigo.append("-- Evaluando Caso (When) --")
            self.visitar(nodo.left) 
            self.codigo.append("Comparar con switch_expr y Saltar si falso al SIGUIENTE_CASO")
            self.codigo.append("-- Bloque When Verdadero --")
            self.visitar(nodo.right)
            self.codigo.append("Saltar al FIN_CASE (jmp)")

        elif tipo == 'Operador' and valor == '..':
            self.visitar(nodo.left) 
            self.visitar(nodo.right) 
            self.codigo.append("Generar rango (range)")

        elif tipo == 'PalabraReservada' and valor == 'for':
            nodo_iteracion = nodo.left
            nombre_var = nodo_iteracion.left.token.value

            self.codigo.append(f"Inicializar iterador: {nombre_var}")
            self.visitar(nodo_iteracion.right)
            
            self.codigo.append("-- Inicio del bucle For --")
            self.codigo.append("Comprobar limite del rango y Saltar si falso a FIN_FOR (jmpf)")
            self.codigo.append("-- Bloque For Verdadero --")
            
            self.visitar(nodo.right)
            
            self.codigo.append(f"Aumentar iterador (inc): {nombre_var}")
            self.codigo.append("Saltar al inicio del For (jmp)")
            self.codigo.append("-- Fin del bucle For --")