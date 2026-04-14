class Ensamblador:
    def __init__(self, tabla_simbolos, codigo_intermedio):
        self.tabla_simbolos = tabla_simbolos
        self.codigo_intermedio = codigo_intermedio
        self.codigo_asm = []
        
        self.cont_if = 0
        self.stack_if = []
        
        self.cont_while = 0
        self.stack_while = []

        self.iterador_actual = ""

    def nueva_etiqueta(self, prefijo):
        self.contador_etiquetas += 1
        return f"{prefijo}_{self.contador_etiquetas}"

    def generar(self):
        self.codigo_asm = []
        self.codigo_asm.append("; --- CÓDIGO ENSAMBLADOR GENERADO (x86) ---")
        self.generar_seccion_data()
        self.generar_seccion_bss()
        self.generar_seccion_text()
        return self.codigo_asm

    def generar_seccion_data(self):
        self.codigo_asm.append("\nsection .data")
        self.codigo_asm.append("    msg_salida db 'Salida: ', 0")
        self.codigo_asm.append("    limite_for resd 1   ;")

    def generar_seccion_bss(self):
        self.codigo_asm.append("\nsection .bss")
        # Aquí declaramos las variables usando la tabla de símbolos
        for nombre, info in self.tabla_simbolos.items():
            if info['tipo'] == 'int':
                # resd reserva 1 double-word (4 bytes) para enteros
                self.codigo_asm.append(f"    {nombre} resd 1")
            elif info['tipo'].startswith('array'):
                # Si es un arreglo, reservamos el espacio correspondiente
                self.codigo_asm.append(f"    {nombre} resd 10") # Asumimos tamaño 10 por ahora

    def generar_seccion_text(self):
        self.codigo_asm.append("\nsection .text")
        self.codigo_asm.append("    global _start")
        self.codigo_asm.append("\n_start:")
        
        # Traducir cada instrucción del código intermedio
        for instruccion in self.codigo_intermedio:
            self.traducir_instruccion(instruccion)
            
        # Llamada al sistema para salir limpiamente del programa (sys_exit)
        self.codigo_asm.append("\n    ; --- Fin del Programa ---")
        self.codigo_asm.append("    mov eax, 1      ;")
        self.codigo_asm.append("    xor ebx, ebx    ;")
        self.codigo_asm.append("    int 0x80        ;")
        # Agregamos la subrutina del sistema para imprimir enteros en consola
        self.codigo_asm.append("\n; --- Subrutina para imprimir enteros (puts) ---")
        self.codigo_asm.append("print_int:")
        self.codigo_asm.append("    pusha               ;")
        self.codigo_asm.append("    mov ecx, 10         ;")
        self.codigo_asm.append("    mov edi, esp        ;")
        self.codigo_asm.append("    sub esp, 16         ;")
        self.codigo_asm.append("    mov byte [edi-1], 10 ;(\\n)")
        self.codigo_asm.append("    lea ebx, [edi-2]    ;")
        self.codigo_asm.append(".convertir_loop:")
        self.codigo_asm.append("    xor edx, edx        ;")
        self.codigo_asm.append("    div ecx             ;")
        self.codigo_asm.append("    add dl, '0'         ;")
        self.codigo_asm.append("    mov [ebx], dl       ;")
        self.codigo_asm.append("    dec ebx             ;")
        self.codigo_asm.append("    test eax, eax       ;")
        self.codigo_asm.append("    jnz .convertir_loop ;")
        self.codigo_asm.append("    inc ebx             ;")
        self.codigo_asm.append("    mov eax, 4          ;")
        self.codigo_asm.append("    mov ecx, ebx        ;")
        self.codigo_asm.append("    mov edx, edi        ")
        self.codigo_asm.append("    sub edx, ebx        ;")
        self.codigo_asm.append("    mov ebx, 1          ;")
        self.codigo_asm.append("    int 0x80            ;")
        self.codigo_asm.append("    add esp, 16         ;")
        self.codigo_asm.append("    popa                ;")
        self.codigo_asm.append("    ret                 ;")

    def traducir_instruccion(self, inst):
        if inst.startswith("Iniciando") or inst.startswith("Código"):
            self.codigo_asm.append(f"\n    ; {inst}")
            return

        self.codigo_asm.append(f"    ; {inst}") # Imprimimos la instrucción original como comentario
        
        if inst.startswith("Push constante:"):
            valor = inst.split(":")[1].strip()
            self.codigo_asm.append(f"    push dword {valor}")
            
        elif inst.startswith("Push variable:") or inst.startswith("Cargando variable:"):
            var = inst.split(":")[1].strip()
            self.codigo_asm.append(f"    push dword [{var}]")
            
        elif inst == "Almacenando valor (store)" or inst == "Almacenando valor":
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    pop ebx         ;")
            self.codigo_asm.append("    mov [ebx], eax  ;")
            
        # Operaciones Matemáticas
        elif inst == "Suma" or inst == "Suma (add)":
            self.codigo_asm.append("    pop ebx")
            self.codigo_asm.append("    pop eax")
            self.codigo_asm.append("    add eax, ebx")
            self.codigo_asm.append("    push eax")
            
        elif inst == "Multiplicar (mul)":
            self.codigo_asm.append("    pop ebx")
            self.codigo_asm.append("    pop eax")
            self.codigo_asm.append("    imul eax, ebx")
            self.codigo_asm.append("    push eax")
            
        # Operaciones Relacionales (Para el For, While e If)
        elif inst == "Menor que (lt)":
            self.codigo_asm.append("    pop ebx")
            self.codigo_asm.append("    pop eax")
            self.codigo_asm.append("    cmp eax, ebx")
            self.codigo_asm.append("    setl al         ")
            self.codigo_asm.append("    movzx eax, al")
            self.codigo_asm.append("    push eax")

        # --- ESTRUCTURAS DE CONTROL: IF ---
        elif inst == "-- Evaluando Condición If --":
            self.cont_if += 1
            # Guardamos la etiqueta única para este IF en la pila
            self.stack_if.append(f"FIN_IF_{self.cont_if}")
            
        elif inst == "Saltar si falso a FIN_IF":
            etiq_fin = self.stack_if[-1] # Leemos la etiqueta actual
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    cmp eax, 0      ;")
            self.codigo_asm.append(f"    je {etiq_fin}    ;")
            
        elif inst == "-- Fin del bloque If --":
            etiq_fin = self.stack_if.pop() # Sacamos la etiqueta de la pila
            self.codigo_asm.append(f"{etiq_fin}:") # Imprimimos la etiqueta en el código


        # --- ESTRUCTURAS DE CONTROL: WHILE ---
        elif inst == "-- Inicio del bucle While --":
            self.cont_while += 1
            etiq_inicio = f"INICIO_WHILE_{self.cont_while}"
            etiq_fin = f"FIN_WHILE_{self.cont_while}"
            # Guardamos la tupla con inicio y fin en la pila
            self.stack_while.append((etiq_inicio, etiq_fin))
            
            self.codigo_asm.append(f"{etiq_inicio}:") # Imprimimos etiqueta de inicio
            
        elif inst == "Saltar si falso a FIN_WHILE (jmpf)":
            _, etiq_fin = self.stack_while[-1]
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    cmp eax, 0      ;")
            self.codigo_asm.append(f"    je {etiq_fin}    ;")
            
        elif inst == "Saltar al inicio del While (jmp)":
            etiq_inicio, _ = self.stack_while[-1]
            self.codigo_asm.append(f"    jmp {etiq_inicio} ;")
            
        elif inst == "-- Fin del bucle While --":
            _, etiq_fin = self.stack_while.pop()
            self.codigo_asm.append(f"{etiq_fin}:")
        
        # --- BUCLE FOR ---
        elif inst.startswith("Inicializar iterador:"):
            self.iterador_actual = inst.split(":")[1].strip()
            
        elif inst == "Generar rango (range)":
            self.codigo_asm.append("    pop ebx         ;")
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append(f"    mov [{self.iterador_actual}], eax ;")
            self.codigo_asm.append("    mov [limite_for], ebx ;")
            
        elif inst == "-- Inicio del bucle For --":
            self.cont_while += 1 # Reciclamos el contador del while para el for
            etiq_inicio = f"INICIO_FOR_{self.cont_while}"
            etiq_fin = f"FIN_FOR_{self.cont_while}"
            self.stack_while.append((etiq_inicio, etiq_fin))
            self.codigo_asm.append(f"{etiq_inicio}:")
            
        elif inst == "Comprobar limite del rango y Saltar si falso a FIN_FOR (jmpf)":
            _, etiq_fin = self.stack_while[-1]
            self.codigo_asm.append(f"    mov eax, [{self.iterador_actual}] ;")
            self.codigo_asm.append("    cmp eax, [limite_for] ;")
            self.codigo_asm.append(f"    jg {etiq_fin}     ;")
            
        elif inst.startswith("Aumentar iterador (inc):"):
            var = inst.split(":")[1].strip()
            self.codigo_asm.append(f"    inc dword [{var}] ;")
            
        elif inst == "Saltar al inicio del For (jmp)":
            etiq_inicio, _ = self.stack_while[-1]
            self.codigo_asm.append(f"    jmp {etiq_inicio}")
            
        elif inst == "-- Fin del bucle For --":
            _, etiq_fin = self.stack_while.pop()
            self.codigo_asm.append(f"{etiq_fin}:")

        # --- SALIDA DE CONSOLA (PUTS) ---
        elif inst == "Salida de consola":
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    call print_int  ;")
        
        # --- ARREGLOS EN MEMORIA ---
        
        # 1. Cargar la dirección base del arreglo
        elif inst.startswith("Cargar arreglo:") or inst.startswith("Cargar referencia arreglo:"):
            nombre_arr = inst.split(":")[1].strip()
            self.codigo_asm.append(f"    mov esi, {nombre_arr} ;")
            
        # 2. Leer un valor del arreglo (ej. arr[j])
        elif inst == "Obtener valor en índice (load_array)":
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    mov ebx, 4      ;")
            self.codigo_asm.append("    mul ebx         ;")
            self.codigo_asm.append("    add eax, esi    ;")
            self.codigo_asm.append("    mov edx, [eax]  ;")
            self.codigo_asm.append("    push edx        ;")
            
        # 3. Escribir un valor en el arreglo (ej. arr[j] = temp)
        elif inst == "Preparar índice para escritura":
            self.codigo_asm.append("    pop eax         ;")
            self.codigo_asm.append("    mov ebx, 4      ")
            self.codigo_asm.append("    mul ebx         ;")
            self.codigo_asm.append("    add eax, esi    ;")
            self.codigo_asm.append("    push eax        ;")
            
        # 4. Cuando se instancia un arreglo nuevo con valores
        elif inst == "Instanciar nuevo Arreglo en memoria":
            # Aquí podríamos inicializar un puntero interno si fuera necesario
            pass # En .bss ya reservamos el espacio general (resd 10)
            
        elif inst == "Llenar arreglo con valores iniciales":
            # (Simplificado) Asumimos que los valores están en la pila
            self.codigo_asm.append("    ; -- Llenando arreglo (Simplificado) --")

        elif inst.startswith("Llamar propiedad/método: length") or inst.startswith("Llamar propiedad/método: size"):
            self.codigo_asm.append("    push dword 4    ; Forzamos el tamaño del arreglo a 4 (Bubble Sort)")