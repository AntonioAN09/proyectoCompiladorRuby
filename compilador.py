#interfaz Compilador Ruby
import tkinter as tk
from tkinter import ttk, messagebox, END, filedialog
import validaciones as validar
import os
import lexico as lex
import sintactico as sintax
import semantico as sem
import re

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
        self.bloque_codigo = tk.Text(editor_frame, wrap=tk.NONE, font=("Consolas", 12))
        self.bloque_codigo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar tags para resaltar errores
        self.bloque_codigo.tag_config("error", background="#ffcccc", underline=True, foreground="#cc0000")
        self.bloque_codigo.tag_config("error_bg", background="#ffe6e6")

        #crear scroll para el bloque de código
        scrollbar = tk.Scrollbar(editor_frame, command=self.bloque_codigo.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bloque_codigo.config(yscrollcommand=lambda *args: self.sincronizar_scroll(scrollbar, *args))

        #actualiza el número de la línea
        self.bloque_codigo.bind('<KeyRelease>', self.actualizar_numeros)
        
        self.actualizar_numeros()

        #frame para la salida del compilador
        salida_frame = tk.Frame(paned)
        paned.add(salida_frame, weight=1)

        #seccion de solo lectura para mostrar la salida
        self.salida = tk.Text(salida_frame, wrap=tk.NONE, height=10, 
                              font=("Consolas", 10), state='disabled',
                              bg='#1e1e1e', fg='white')
        self.salida.pack(fill=tk.BOTH, expand=True)

        #scroll para el área de la salida
        salida_scroll = tk.Scrollbar(salida_frame, command=self.salida.yview)
        salida_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.salida.config(yscrollcommand=salida_scroll.set)


    def barra_menu(self):
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo", command=self.nuevo_archivo)
        menu_archivo.add_command(label="Abrir", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        menu_archivo.add_command(label="Limpiar", command=self.limpiar_archivo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.quit)
        menu_editar = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Editar", menu=menu_editar)
        menu_editar.add_command(label="Deshacer")
        menu_editar.add_command(label="Rehacer")
        menu_editar.add_command(label="Buscar")
        menu_editar.add_command(label="Reemplazar")
        menu_compilador = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Compilador", menu=menu_compilador)
        menu_compilador.add_command(label="Analizar Léxico", command=self.analizar_lexico)
        menu_compilador.add_command(label="Analizar Sintáctico", command=self.analizar_sintactico)
        menu_compilador.add_command(label="Analizar Semántico", command=self.analizar_semantico)

    def barra_botones(self):
        #frame para la barra de botones (al mismo nivel del menú)
        barra = tk.Frame(self, bg='#f0f0f0')
        barra.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        #menubutton que actúa como dropdown con ícono de triángulo (play)
        menubutton = tk.Menubutton(barra, text="▶", bg='#f0f0f0', 
                                   relief=tk.RAISED, bd=1, padx=8, pady=3, font=("Arial", 12))
        menubutton.pack(side=tk.RIGHT, padx=5, pady=3)
        
        #menú desplegable para el botón
        menu = tk.Menu(menubutton, tearoff=0)
        menubutton.config(menu=menu)
        menu.add_command(label="Compilar")
        menu.add_command(label="Ejecutar")


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
        
        #validar aperturas de cierre de paréntesis, llaves y corchetes
        es_valido, linea_error, mensaje_error = validar.validar_aperturaCierre(codigo)
        if not es_valido:
            self.escribir_salida(f"ERROR: {mensaje_error}")
            self.marcar_linea_error(linea_error)
        
        self.escribir_salida("Análisis léxico completado exitosamente.")
        try:
            numeroLinea = 0
            self.escribir_salida("-" * 65)
            lineas_con_error = []
            
            for linea in codigo.split('\n'):
                numeroLinea += 1
                linea = linea.rstrip()
                tokens = lex.tokenizar(linea)
                
                for token in tokens:
                    categoria, descripcion = lex.clasificarToken(token)
                    
                    self.escribir_salida(f"'{token}':".ljust(15) + f" | {categoria:<20} | {descripcion}")
                    
                    if lex.verificarDuplicado(token, categoria, lex.tokensEncontrados):
                        self.escribir_salida(f"ERROR: Variable '{token}' duplicada (Línea {numeroLinea})")
                        lineas_con_error.append(numeroLinea)
                    
                    if categoria == "invalido":
                        lineas_con_error.append(numeroLinea)
                        if re.match(r'^\d', token):
                            self.escribir_salida(f"ERROR: Identificador '{token}' no puede comenzar con número (Línea {numeroLinea})")
                        else:
                            self.escribir_salida(f"ERROR: Token '{token}' contiene caracteres inválidos (Línea {numeroLinea})")
            
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
        try:
            self.escribir_salida("Análisis sintáctico completado exitosamente.")
            self.escribir_salida("-" * 65)
            lista_tokens = lex.generar_tokens(codigo)
            parser = sintax.Parser(lista_tokens)
            arbol = parser.parse()
            resultado = arbol.print_tree()
            self.escribir_salida(resultado)
        except Exception as e:
            self.escribir_salida(f"Error al analizar el código: {e}")

    def analizar_semantico(self):
        self.limpiar_errores_visuales()
        self.limpiar_salida()

        codigo = self.bloque_codigo.get('1.0', END).strip()
        if not codigo:
            self.escribir_salida("El bloque de código está vacío. Por favor, ingresa código para analizar.")
            return
        try:
            lsita_tokens = lex.generar_tokens(codigo)
            parser = sintax.Parser(lsita_tokens)
            arbol = parser.parse()

            analizador_semantico = sem.Semantico()
            errores, tabla_simbolos = analizador_semantico.analizar(arbol)
            self.escribir_salida("Análisis semántico completado.\n"+"-" * 65)
            if errores:
                self.escribir_salida("Errores semánticos encontrados:")
                for error in errores:
                    self.escribir_salida(error)
            else:
                self.escribir_salida("No se encontraron errores semánticos.")

            self.escribir_salida("\nTabla de Símbolos:")
            if not tabla_simbolos:
                self.escribir_salida("La tabla de símbolos está vacía.")
            for variable, tipo in tabla_simbolos.items():
                self.escribir_salida(f"Variable: {variable} | Tipo: {tipo}")
        except Exception as e:
            self.escribir_salida(f"Error al analizar el código: {e}")

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

if __name__ == "__main__":
    app = Compilador()
    app.mainloop()