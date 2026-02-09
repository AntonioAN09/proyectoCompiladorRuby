#interfaz Compilador Ruby
import tkinter as tk
from tkinter import ttk, messagebox, END

class Compilador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Ruby")
        self.geometry("900x700")
        self.minsize(800, 600)

        self.barra_menu()   #crea el menú de la aplicación

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



    def nuevo_archivo(self):
        messagebox.showinfo("Nuevo Archivo", "Función para crear un nuevo archivo.")

    def abrir_archivo(self):
        messagebox.showinfo("Abrir Archivo", "Función para abrir un archivo existente.")

    def guardar_archivo(self):
        messagebox.showinfo("Guardar Archivo", "Función para guardar el archivo actual.")
    
    def limpiar_archivo(self):
        self.bloque_codigo.delete('1.0', END)
        self.actualizar_numeros()

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

if __name__ == "__main__":
    app = Compilador()
    app.mainloop()