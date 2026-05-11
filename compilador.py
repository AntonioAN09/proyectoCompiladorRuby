#interfaz Compilador Ruby
import tkinter as tk
from tkinter import ttk, messagebox, END, filedialog, simpledialog
import validaciones as validar
import os
import lexico as lex
import sintactico as sintax
import semantico as sem
import generador as gen
import ensamblador as asm
import re
import sys
from io import StringIO
import time

class Compilador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Ruby - Nuevo Archivo")
        self.geometry("900x700")
        self.minsize(800, 600)

        self.ruta_actual = None
        self.nombre_archivo = None

        self.barra_menu()   #crea el menú de la aplicación
        self.barra_botones() #crea la barra con botones a la derecha

        # PanedWindow para dividir editor y salida
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        #área para mostrar los números de línea
        editor_frame = tk.Frame(paned)
        paned.add(editor_frame, weight=3)

        #widget para mostrar el número de línea
        self.numeros_linea = tk.Text(editor_frame, width=3, padx=3, takefocus=0,
                                      border=0, background='lightgray', state='disabled',
                                      font=("Consolas", 12))
        self.numeros_linea.pack(side=tk.LEFT, fill=tk.Y)

        #crear el bloque de código
        self.bloque_codigo = tk.Text(editor_frame, wrap=tk.NONE, font=("Consolas", 12), 
                                     undo=True, maxundo=-1, autoseparators=True, background="white", 
                                     fg="#000000", insertbackground='black')
        self.bloque_codigo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        #tags para resaltar errores
        self.bloque_codigo.tag_config("error", background="#e67979", underline=True,
                                       foreground="#d81616")
        self.bloque_codigo.tag_config("error_bg", background="#cb8d8d")

        #tags para palabras reservadas
        self.bloque_codigo.tag_config("reservada", foreground="purple")
        self.bloque_codigo.tag_config("string", foreground="green")
        self.bloque_codigo.tag_config("numero", foreground="blue")


        #crear scroll para el bloque de código
        scrollbar = tk.Scrollbar(editor_frame, command=self.bloque_codigo.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bloque_codigo.config(yscrollcommand=lambda *args: self.sincronizar_scroll(scrollbar, *args))
        
        
        self.bloque_codigo.bind('<KeyRelease>', self.resaltar_sintaxis)

        #actualiza el número de la línea
        self.bloque_codigo.bind('<KeyRelease>', self.actualizar_numeros, add='+')
        
        self.actualizar_numeros()

        #frame para la salida del compilador
        salida_frame = tk.Frame(paned)
        paned.add(salida_frame, weight=1)

        #seccion de solo lectura para mostrar la salida
        self.salida = tk.Text(salida_frame, wrap=tk.NONE, height=10, 
                              font=("Cascadia Code", 10), state='disabled',
                              bg="#282c34", fg="#e06c75")
        self.salida.pack(fill=tk.BOTH, expand=True)

        #scroll para el área de la salida
        salida_scroll = tk.Scrollbar(salida_frame, command=self.salida.yview)
        salida_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.salida.config(yscrollcommand=salida_scroll.set)

        #verificador para generar código intermedio
        self.semenatico_ok = False

        self.bind_all("<Control-BackSpace>", self.borrar_palabra)


    def barra_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo", command=self.nuevo_archivo, accelerator="Ctrl+N")
        menu_archivo.add_command(label="Abrir", command=self.abrir_archivo, accelerator="Ctrl+O")
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo, accelerator="Ctrl+S")
        menu_archivo.add_command(label="Limpiar", command=self.limpiar_archivo, accelerator="Ctrl+L")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.quit, accelerator="Alt+F4")
        
        menu_editar = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Editar", menu=menu_editar)
        menu_editar.add_command(label="Deshacer", accelerator="Ctrl+Z", command=self.deshacer)
        menu_editar.add_command(label="Rehacer", accelerator="Ctrl+Y", command=self.rehacer)
        menu_editar.add_command(label="Buscar", accelerator="Ctrl+F", command=self.buscar)
        menu_editar.add_command(label="Reemplazar", accelerator="Ctrl+M", command=self.reemplazar)
        menu_editar.add_separator()
        menu_editar.add_command(label="Limpiar Terminal", command=self.limpiar_salida, accelerator="Ctrl+P")
        
        menu_compilador = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Compilador", menu=menu_compilador)
        menu_compilador.add_command(label="Analizar Léxico", command=self.analizar_lexico, accelerator="Ctrl+Q")
        menu_compilador.add_command(label="Analizar Sintáctico", command=self.analizar_sintactico, accelerator="Ctrl+W")
        menu_compilador.add_command(label="Analizar Semántico", command=self.analizar_semantico, accelerator="Ctrl+E")
        menu_compilador.add_command(label='Generar Código', command=self.generar_codigo, accelerator="Ctrl+R")

        #atajos del teclado para las funciones del menú
        self.bind_all("<Control-n>", lambda event: self.nuevo_archivo())
        self.bind_all("<Control-o>", lambda event: self.abrir_archivo())
        self.bind_all("<Control-s>", lambda event: self.guardar_archivo())
        self.bind_all("<Control-f>", lambda event: self.buscar())
        self.bind_all("<Control-m>", lambda event: self.reemplazar())
        self.bind_all("<Control-z>", lambda event: self.deshacer())
        self.bind_all("<Control-y>", lambda event: self.rehacer())
        self.bind_all("<Control-l>", lambda event: self.limpiar_archivo())
        self.bind_all("<Alt-F4>", lambda event: self.quit())
        self.bind_all("<Control-q>", lambda event: self.analizar_lexico())
        self.bind_all("<Control-w>", lambda event: self.analizar_sintactico())
        self.bind_all("<Control-e>", lambda event: self.analizar_semantico())
        self.bind_all("<Control-r>", lambda event: self.generar_codigo())
        self.bind_all("<Control-p>", lambda event: self.limpiar_salida())
        self.bind_all("<F5>", lambda event: self.ejecutar_codigo())

    def barra_botones(self):
        barra = tk.Frame(self, bg='white', height=40) 
        barra.pack(side=tk.TOP, fill=tk.X)
        barra.pack_propagate(False) # Congela la altura de la barra para que no se encoja

        boton_ejecutar = tk.Button(barra, text="▶ Ejecutar Código (F5)", bg="#2ea043", fg="white", 
                                   font=("Consolas", 10, "bold"), relief=tk.FLAT, 
                                   activebackground="#238636", activeforeground="white",
                                   cursor="hand2", padx=15, command=self.ejecutar_codigo)
        
        boton_ejecutar.pack(side=tk.RIGHT, padx=15, pady=5)
    
    
    def nuevo_archivo(self):
        if self.bloque_codigo.get('1.0', END).strip():  #verifica si el bloque de código no está vacío
            if messagebox.askyesno("Nuevo Archivo", "¿Deseas guardar el archivo actual?"):
                self.guardar_archivo() #confirma con el usuario si desea guardar el archivo abierto
        
        self.bloque_codigo.delete('1.0', END)   #borra el contenido del bloque de código
        self.ruta_actual = None                         #modifica el titulo, ruta y nombre del archivo
        self.nombre_archivo = None
        self.title("Compilador Ruby - Nuevo Archivo")

        self.actualizar_numeros() #actualiza los números de lpineas

    def abrir_archivo(self):
        if self.bloque_codigo.get('1.0', END).strip():  #verifica si el bloque de código no está vacío
            if messagebox.askyesno("Abrir Archivo", "¿Deseas guardar el archivo actual?"):
                self.guardar_archivo() #confirma con el usuario si desea guardar el archivo abierto

        ruta = filedialog.askopenfilename( #pregunta cuál archivo abrir
            filetypes=[("Text files", "*.txt")]
        )
        if not ruta:
            return  #el usuario canceló el diálogo de apertura
        try:
            with open(ruta, 'r', encoding='utf-8-sig') as archivo:
                contenido = archivo.read()
        except Exception as e:
            messagebox.showerror("Error al Abrir Archivo", f"No se pudo abrir el archivo:\n{e}")
            return
        
        self.bloque_codigo.delete('1.0', END) #borra el contenido del bloque de código
        self.bloque_codigo.insert('1.0', contenido) #inserta el contenido del archivo en el bloque de código
        self.ruta_actual = ruta     #modifica el titulo, ruta y nombre del archivo
        self.nombre_archivo = os.path.basename(ruta)
        self.title(f"Compilador Ruby - {self.nombre_archivo}")
        self.actualizar_numeros() #actualiza los números de línea

    def guardar_archivo(self): #funcion para guardar el archivo
        if not self.nombre_archivo or not self.ruta_actual:
            ruta = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if not ruta:
                return  #el usuario canceló el diálogo de guardado
            self.ruta_actual = ruta

        contenido = self.bloque_codigo.get('1.0', END)
        with open(self.ruta_actual, 'w', encoding='utf-8-sig') as archivo:
            archivo.write(contenido)
        self.nombre_archivo = os.path.basename(self.ruta_actual)
        self.title(f"Compilador Ruby - {self.nombre_archivo}")
        messagebox.showinfo("Archivo Guardado", f"Archivo guardado exitosamente en:\n{self.ruta_actual}")

    def limpiar_errores_visuales(self): #función para limpiar los errores visuales del bloque de código
        self.bloque_codigo.tag_remove("error", "1.0", tk.END)
        self.bloque_codigo.tag_remove("error_bg", "1.0", tk.END)
    
    def marcar_linea_error(self, numero_linea):
        inicio = f"{numero_linea}.0"
        fin = f"{numero_linea}.end"
        self.bloque_codigo.tag_add("error_bg", inicio, fin)
        #añade un marcador al inicio de la línea
        self.bloque_codigo.tag_add("error", inicio, f"{numero_linea}.1")

    def analizar_lexico(self):
        #limpiar errores visuales anteriores
        self.limpiar_errores_visuales()
        self.limpiar_salida()
        
        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("El bloque de código está vacío. Por favor, ingresa código para analizar.")
            return
        
        self.escribir_salida("Análisis léxico completado exitosamente.")
        #validar aperturas de cierre de paréntesis, llaves y corchetes
        
        try:
            numeroLinea = 0
            self.escribir_salida("-" * 65)
            lineas_con_error = []
            
            for linea in codigo.split('\n'):
                numeroLinea += 1
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue

                tokens = lex.tokenizar(linea)
                for token in tokens:
                    categoria, descripcion = lex.clasificarToken(token)
                    self.escribir_salida(f"'{token}':".ljust(15) + f" | {categoria:<20} | {descripcion}")
                    
                    if categoria == "invalido":
                        lineas_con_error.append(numeroLinea)
                        if re.match(r'^\d', token):
                            self.escribir_salida(f"Error: Identificador '{token}' no puede comenzar con número (Línea {numeroLinea})")
                        else:
                            self.escribir_salida(f"Error: Token '{token}' contiene caracteres inválidos (Línea {numeroLinea})")
            
            #marca todas las líneas con errores
            for linea_num in lineas_con_error:
                self.marcar_linea_error(linea_num)

        except Exception as e:
            self.escribir_salida(f"Error al analizar el código: {e}")

    def analizar_sintactico(self):
        self.limpiar_errores_visuales()
        self.limpiar_salida()

        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("El bloque de código está vacío. Por favor, ingresa código para analizar.")
            return
        es_valido, linea_error, mensaje_error = validar.validar_aperturaCierre(codigo)
        if not es_valido:
            self.escribir_salida(f"Error sintactico: {mensaje_error} (Línea {linea_error})")
            self.marcar_linea_error(linea_error)
            return
        try:
            self.escribir_salida("Análisis sintáctico completado exitosamente.")
            self.escribir_salida("-" * 65)
            lista_tokens = lex.generar_tokens(codigo)
            parser = sintax.Parser(lista_tokens)
            arbol = parser.parse()
            resultado = arbol.print_tree()
            self.escribir_salida(resultado)
        except Exception as e:
            mensaje_error = str(e)
            self.escribir_salida(f"Error sintáctico: {mensaje_error}")
            match= re.search(r'Linea (\d+)', mensaje_error)
            if match:
                linea_num = int(match.group(1))
                if linea_num > 0:
                    self.marcar_linea_error(linea_num)

    def analizar_semantico(self):
        self.limpiar_errores_visuales()
        self.limpiar_salida()

        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("El bloque de código está vacío. Por favor, ingresa código para analizar.")
            return
        es_valido, linea_error, mensaje_error = validar.validar_aperturaCierre(codigo)
        if not es_valido:
            self.escribir_salida(f"Error sintactico: {mensaje_error} (Línea {linea_error})")
            self.marcar_linea_error(linea_error)
            return
        try:
            lsita_tokens = lex.generar_tokens(codigo)
            parser = sintax.Parser(lsita_tokens)
            arbol = parser.parse()

            analizador_semantico = sem.Semantico()
            errores, tabla_simbolos = analizador_semantico.analizar(arbol)
            self.escribir_salida("Análisis semántico completado.\n"+"-" * 65)
            
            if errores: #marca los errores si los encontró
                self.escribir_salida("Errores semánticos encontrados:")
                for mensaje, linea in errores:
                    self.escribir_salida(f"Línea {linea} | {mensaje}")
                    if linea > 0:
                        self.marcar_linea_error(linea)
                self.semenatico_ok = False
            else:
                self.semenatico_ok = True
                self.escribir_salida("No se encontraron errores semánticos.")

            self.escribir_salida("\nTabla de Símbolos:")
            if not tabla_simbolos:
                self.escribir_salida("La tabla de símbolos está vacía.")
            else:
                encabezado = f"| {'Símbolo'.ljust(10)} | {'Tipo de datos'.ljust(15)} | {'Descripción'.ljust(20)} | {'Bytes'.ljust(5)} |"
                self.escribir_salida(encabezado)
                self.escribir_salida("-" * len(encabezado))
                for simbolo, info in tabla_simbolos.items():
                    tipo = str(info['tipo'])
                    desc = str(info['descripcion'])
                    fila = f"| {simbolo.ljust(10)} | {tipo.ljust(15)} | {desc.ljust(20)} | {str(info['bytes']).ljust(5)} |"
                    self.escribir_salida(fila)

        except Exception as e:
            mensaje_error = str(e)
            self.escribir_salida(f"Error sintactico: {mensaje_error}")
            match= re.search(r'Linea (\d+)', mensaje_error)
            if match:
                linea_num = int(match.group(1))
                if linea_num > 0:
                    self.marcar_linea_error(linea_num)

    def generar_codigo(self):
        self.limpiar_errores_visuales()
        self.limpiar_salida()

        if not self.semenatico_ok:
            self.escribir_salida("Análisis semántico no realizado o con errores.")
            return
        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("El bloque de código está vacío. Por favor, ingresa código para analizar.")
            return
        
        es_valido, linea_error, mensaje_error = validar.validar_aperturaCierre(codigo)
        if not es_valido:
            self.escribir_salida(f"Error sintactico: {mensaje_error} (Línea {linea_error})")
            self.marcar_linea_error(linea_error)
            return
        
        try:
            lista_tokens = lex.generar_tokens(codigo)
            parser = sintax.Parser(lista_tokens)
            arbol = parser.parse()

            generador_codigo = gen.GeneradorCodigo()
            codigo_generado = generador_codigo.generador(arbol)
            # for linea in codigo_generado:
            #     self.escribir_salida(linea)

            self.escribir_salida("\nGenerando código ensamblador...")
            analizador_semantico = sem.Semantico()
            errores_sem, tabla_simbolos = analizador_semantico.analizar(arbol)
            
            traductor = asm.Ensamblador(tabla_simbolos, codigo_generado)
            codigo_asm_final = traductor.generar()
            
            for linea_asm in codigo_asm_final:
                self.escribir_salida(linea_asm)
                
            self.semenatico_ok = False

        except Exception as e:
            mensaje_error = str(e)
            self.escribir_salida(f"Error al generar código: {mensaje_error}")
            match= re.search(r'Linea (\d+)', mensaje_error)
            if match:
                linea_num = int(match.group(1))
                if linea_num > 0:
                    self.marcar_linea_error(linea_num)

    def ejecutar_codigo(self):
        self.limpiar_errores_visuales()
        self.limpiar_salida()
        self.analizar_semantico()
        
        if not self.semenatico_ok:
            self.escribir_salida("\nERROR DE EJECUCION.")
            return
        
        self.limpiar_errores_visuales()
        self.limpiar_salida()
        
        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("No hay código para ejecutar.")
            return

        self.escribir_salida("--- Ejecutando Programa ---")
        import time
        tiempo_arranque = time.time()
        python_code = []
        indent_level = 0
        switch_var = ""
        first_when = True
        
        for linea in codigo.splitlines():
            lin = linea.strip()
            if not lin or lin.startswith("#"):
                continue
            
            #para los cierres
            if lin == 'end':
                indent_level = max(0, indent_level - 1)
                continue
            elif lin.startswith('elsif ') or lin == 'else' or lin.startswith('when '):
                #when no quita identacion
                if lin.startswith('when ') and first_when:
                    pass 
                else:
                    indent_level = max(0, indent_level - 1)

            py_line = "    " * indent_level

            lin = re.sub(r'(\w+)\.length', r'len(\1)', lin)
            lin = re.sub(r'(\w+)\.size', r'len(\1)', lin)

            if lin.startswith('puts '):
                py_line += f"print({lin[5:]})"
            elif lin.startswith('print '):
                py_line += f"print({lin[6:]}, end='')"
            elif lin.startswith('if '):
                py_line += f"{lin}:"
                indent_level += 1
            elif lin.startswith('elsif '):
                py_line += f"elif {lin[6:]}:"
                indent_level += 1
            
            elif lin.startswith('while '):
                py_line += f"{lin}:"
                indent_level += 1
                python_code.append(py_line)
                python_code.append("    " * indent_level + "import time")
                python_code.append("    " * indent_level + f"if time.time() - {tiempo_arranque} > 3: raise Exception('Bucle_Infinito')")
                continue 
                
            elif lin == 'begin':
                py_line += "while True:"
                indent_level += 1
                python_code.append(py_line)
                python_code.append("    " * indent_level + "import time")
                python_code.append("    " * indent_level + f"if time.time() - {tiempo_arranque} > 3: raise Exception('Bucle_Infinito')")
                continue

            elif lin.startswith('end while '):
                condicion = lin[10:].strip()
                indent_level = max(0, indent_level - 1)
                py_line = "    " * indent_level
                py_line += f"    if not ({condicion}): break"
            elif lin.startswith('for ') and ' in ' in lin:
                match = re.match(r'for\s+(\w+)\s+in\s+(.+)\.\.(.+)', lin)
                if match:
                    var, start, end = match.groups()
                    py_line += f"for {var} in range({start}, {end} + 1):"
                    indent_level += 1
                else:
                    py_line += lin
            
            elif lin.startswith('def '):
                py_line += f"{lin}:"
                indent_level += 1
            elif lin.startswith('return '):
                py_line += f"{lin}"
            
            elif lin.startswith('case '):
                switch_var = lin[5:].strip()
                first_when = True
                py_line += f"__switch_var = {switch_var}"
            elif lin.startswith('when '):
                condicion = lin[5:].strip()
                if first_when:
                    py_line += f"if __switch_var == {condicion}:"
                    first_when = False
                else:
                    py_line += f"elif __switch_var == {condicion}:"
                indent_level += 1
            elif lin == 'else':
                py_line += "else:"
                indent_level += 1
            
            elif lin.startswith('require '):
                py_line += f"# {lin} (ignorado en ejecución rápida)"
            else:
                py_line += lin

            python_code.append(py_line)

        codigo_final = "\n".join(python_code)
        
        print("\n--- CÓDIGO PYTHON GENERADO ---")
        print(codigo_final)
        print("------------------------------\n")
        viejo_stdout = sys.stdout
        salida_redirigida = sys.stdout = StringIO()
        
        try:
            entorno_vacio = {}
            exec(codigo_final, entorno_vacio)
            
            resultado = salida_redirigida.getvalue()
            if resultado:
                self.escribir_salida(resultado)
            else:
                self.escribir_salida("[Programa ejecutado sin salidas en consola]")

        except Exception as e:
            mensaje_error = str(e)            
            if "Bucle_Infinito" in mensaje_error:
                self.escribir_salida("\nError de ejecucion: Bucle infinito")
                self.escribir_salida("El programa tardo mas de 3 segundos y fue detenido.")
            elif "list index out of range" in mensaje_error:
                self.escribir_salida("Error de ejecucion, index fuera de rango.")
                self.escribir_salida("Acceso a una posicion que no existe.")
            elif "division by zero" in mensaje_error:
                self.escribir_salida("Error de ejecucion, division por cero no permitida.")
            else:
                self.escribir_salida(f"Error de ejecucion: {mensaje_error}")
        finally:
            sys.stdout = viejo_stdout

    def limpiar_archivo(self):
        self.limpiar_errores_visuales()
        self.bloque_codigo.delete('1.0', END)
        self.actualizar_numeros()
        self.salida.config(state='normal')
        self.salida.delete('1.0', END)
        self.salida.config(state='disabled')
        self.ruta_actual = None
        self.nombre_archivo = None
        self.title("Compilador Ruby - Nuevo Archivo")

    def sincronizar_scroll(self, scrollbar, *args):#función para sincronziar el scroll
        scrollbar.set(*args)
        self.numeros_linea.yview_moveto(args[0])

    def actualizar_numeros(self, event=None): #función para actualizar los números de línea
        if event:
            self.semenatico_ok = False
        self.numeros_linea.config(state='normal')
        self.numeros_linea.delete('1.0', tk.END)

        #obtiene el número de líneas del bloque de código
        num_lineas = self.bloque_codigo.index('end-1c').split('.')[0]
        
        #genera los números de línea y los inserta en el widget de números de línea
        numeros = '\n'.join(str(i) for i in range(1, int(num_lineas) + 1))
        self.numeros_linea.insert('1.0', numeros)
        self.numeros_linea.config(state='disabled')

    def escribir_salida(self, texto):#funcion para escribir la salida en el panel inferior
        self.salida.config(state='normal')
        self.salida.insert(tk.END, texto + '\n')
        self.salida.see(tk.END)
        self.salida.config(state='disabled')

    def limpiar_salida(self): #función para limpiar el panel de salida
        self.salida.config(state='normal')
        self.salida.delete('1.0', tk.END)
        self.salida.config(state='disabled')

    def deshacer(self): #funcion para deshacer cambios al codigo
        try:
            self.bloque_codigo.edit_undo()
        except tk.TclError:
            pass
    def rehacer(self): #funcion para rehacer cambios al codigo
        try:
            self.bloque_codigo.edit_redo()
        except tk.TclError:
            pass
    def borrar_palabra(self, event = None): #funcion para borrar la palabra con Ctrl+Backspace
        try:
            if self.bloque_codigo.tag_ranges("sel"):
                self.bloque_codigo.delete("sel.first", "sel.last")
            else:
                self.bloque_codigo.delete("insert-1c wordstart", "insert")
            return "break"
        except tk.TclError:
            pass
    def buscar(self): #funcion para buscar texto en el bloque de código
        objetivo = simpledialog.askstring("Buscar", "Ingrese el texto a buscar:")
        if objetivo:
            self.bloque_codigo.tag_remove('found', '1.0', tk.END)
            inicio = '1.0'
            while True:
                inicio = self.bloque_codigo.search(objetivo, inicio, stopindex=tk.END)
                if not inicio:
                    break
                fin = f"{inicio}+{len(objetivo)}c"
                self.bloque_codigo.tag_add('found', inicio, fin)
                self.bloque_codigo.tag_config('found', background='yellow')
                inicio = fin
    
    def reemplazar(self):
        #ventana emergente para buscar y reemplazar texto en el bloque de código
        ventana = tk.Toplevel(self)
        ventana.title("Buscar y Reemplazar")
        ventana.geometry("350x200")
        ventana.attributes("-topmost", True) #ventana al frente
        ventana.transient(self) #asocia la ventana con el compilador
        ventana.grab_set() #bloquea la ventana principal mientras esta abierta

        var_buscar = tk.StringVar()
        var_reemplazar = tk.StringVar()

        tk.Label(ventana, text="Palabra a buscar:", font=("Arial", 10)).pack(pady=(15, 5))
        entry_buscar = tk.Entry(ventana, textvariable=var_buscar, width=40, font=("Arial", 10))
        entry_buscar.pack()
        entry_buscar.focus()

        tk.Label(ventana, text="Reemplazar con:", font=("Arial", 10)).pack(pady=(10, 5))
        entry_reemplazar = tk.Entry(ventana, textvariable=var_reemplazar, width=40, font=("Arial", 10))
        entry_reemplazar.pack()

        #funcion para reemplazar el texto en el bloque de código
        def ejecutar_reemplazo():
            objetivo = var_buscar.get()
            nuevo = var_reemplazar.get()
            
            if objetivo: #si se buscó algo, se reemplaza
                contenido = self.bloque_codigo.get('1.0', tk.END)
                contenido_nuevo = contenido.replace(objetivo, nuevo)
                
                self.bloque_codigo.delete('1.0', tk.END)
                self.bloque_codigo.insert('1.0', contenido_nuevo)
                
            ventana.destroy() #ciera la ventana después de reemplazar
        #boton para ejecutar el reemplazo
        tk.Button(ventana, text="Reemplazar Todo", command=ejecutar_reemplazo, bg='#d0e0f0').pack(pady=20)
    
    def resaltar_sintaxis(self, event=None): #funcion para resaltar ciertas sintaxis
        for tag in ["reservada", "string", "numero"]:
            self.bloque_codigo.tag_remove(tag, '1.0', tk.END)
        
        reservadas = ["def", "end", "if", "else", "elsif", "while", "for", "in", 
                      "return", "puts", "begin", "case", "when"]

        for palabra in reservadas: #resalta las palabras reservadas
            inicio = '1.0'
            while True:
                inicio = self.bloque_codigo.search(rf'\m{palabra}\M', inicio, stopindex=tk.END, regexp=True)
                if not inicio:
                    break
                fin = f"{inicio}+{len(palabra)}c"
                self.bloque_codigo.tag_add("reservada", inicio, fin)
                inicio = fin

        inicio = '1.0' 
        while True: #para resaltar los numeros
            inicio = self.bloque_codigo.search(r"\m\d+\M", inicio, stopindex=tk.END, regexp=True)
            if not inicio:
                break
            match_str = self.bloque_codigo.get(inicio, f"{inicio} wordend")
            num_len = len(''.join(filter(str.isdigit, match_str)))
            fin = f"{inicio}+{num_len}c"
            self.bloque_codigo.tag_add("numero", inicio, fin)
            inicio = fin




if __name__ == "__main__":
    app = Compilador()
    app.mainloop()