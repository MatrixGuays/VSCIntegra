import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import hashlib
import uuid

# ... (las demás clases y funciones se mantienen igual hasta VentanaLogin)

class VentanaLogin(tk.Tk):
    """Ventana principal de login y registro - VERSIÓN CORREGIDA"""
    
    def __init__(self):
        super().__init__()
        self.title("Sistema de Alquiler de Puestos de Feria")
        self.geometry("450x500")  # Aumenté el tamaño para acomodar todos los campos
        self.resizable(False, False)
        
        self.sistema_auth = SistemaAutenticacion()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de login/registro - VERSIÓN CORREGIDA"""
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self)  # Ahora es self.notebook
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Pestaña Login
        frame_login = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_login, text="Ingresar")
        
        # Pestaña Registro
        frame_registro = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_registro, text="Crear Usuario")
        
        self.crear_pestana_login(frame_login)
        self.crear_pestana_registro(frame_registro)
    
    def crear_pestana_login(self, parent):
        """Crea la pestaña de login - VERSIÓN CORREGIDA"""
        # Tipo de usuario
        frame_tipo = ttk.LabelFrame(parent, text="Tipo de Usuario", padding=10)
        frame_tipo.pack(fill=tk.X, pady=(0, 15))
        
        self.tipo_login = tk.StringVar(value="feriante")
        tk.Radiobutton(frame_tipo, text="Feriante", variable=self.tipo_login, 
                      value="feriante").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame_tipo, text="Puestero", variable=self.tipo_login, 
                      value="puestero").pack(side=tk.LEFT, padx=10)
        
        # Usuario
        frame_usuario = ttk.Frame(parent)
        frame_usuario.pack(fill=tk.X, pady=8)
        tk.Label(frame_usuario, text="Usuario:", width=12, anchor="w").pack(side=tk.LEFT)
        self.entry_usuario_login = tk.Entry(frame_usuario, width=25)
        self.entry_usuario_login.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Contraseña
        frame_password = ttk.Frame(parent)
        frame_password.pack(fill=tk.X, pady=8)
        tk.Label(frame_password, text="Contraseña:", width=12, anchor="w").pack(side=tk.LEFT)
        self.entry_password_login = tk.Entry(frame_password, width=25, show="*")
        self.entry_password_login.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Botón ingresar
        btn_ingresar = tk.Button(parent, text="Ingresar", command=self.login, 
                                bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold"))
        btn_ingresar.pack(pady=20)
        
        # Bind Enter key para login
        self.entry_password_login.bind('<Return>', lambda e: self.login())
    
    def crear_pestana_registro(self, parent):
        """Crea la pestaña de registro - VERSIÓN CORREGIDA"""
        # Tipo de usuario
        frame_tipo = ttk.LabelFrame(parent, text="Tipo de Usuario", padding=10)
        frame_tipo.pack(fill=tk.X, pady=(0, 15))
        
        self.tipo_registro = tk.StringVar(value="feriante")
        tk.Radiobutton(frame_tipo, text="Feriante", variable=self.tipo_registro, 
                      value="feriante").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(frame_tipo, text="Puestero", variable=self.tipo_registro, 
                      value="puestero").pack(side=tk.LEFT, padx=10)
        
        # Campos de registro
        campos_registro = [
            ("Usuario:", "entry_usuario_registro", None),
            ("Email:", "entry_email_registro", None),
            ("Contraseña:", "entry_password_registro", "*"),
            ("Confirmar Contraseña:", "entry_confirmar_password", "*")
        ]
        
        self.widgets_registro = {}
        
        for texto, clave, show_char in campos_registro:
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=6)
            
            tk.Label(frame, text=texto, width=18, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=25, show=show_char)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            
            self.widgets_registro[clave] = entry
        
        # Botón registrar
        btn_registrar = tk.Button(parent, text="Registrar", command=self.registrar,
                                 bg="#2196F3", fg="white", width=15, font=("Arial", 10, "bold"))
        btn_registrar.pack(pady=20)
        
        # Bind Enter key para registro
        self.widgets_registro["entry_confirmar_password"].bind('<Return>', lambda e: self.registrar())
    
    def login(self):
        """Maneja el proceso de login - VERSIÓN CORREGIDA"""
        tipo = self.tipo_login.get()
        usuario = self.entry_usuario_login.get().strip()
        password = self.entry_password_login.get()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        usuario_autenticado = self.sistema_auth.autenticar_usuario(tipo, usuario, password)
        
        if usuario_autenticado:
            self.abrir_interfaz_principal(usuario_autenticado)
        else:
            # Simular los casos de error descritos
            usuarios_existentes = [u["usuario"] for u in self.sistema_auth.usuarios.get("usuarios", [])]
            
            if usuario not in usuarios_existentes:
                respuesta = messagebox.askquestion("Usuario no existe", 
                                                 "Usuario incorrecto o inexistente\n¿Desea crear un nuevo usuario?",
                                                 icon='warning')
                if respuesta == 'yes':
                    # Cambiar a pestaña de registro y pre-cargar datos
                    self.notebook.select(1)  # Cambiar a pestaña de registro
                    self.widgets_registro["entry_usuario_registro"].delete(0, tk.END)
                    self.widgets_registro["entry_usuario_registro"].insert(0, usuario)
                    self.tipo_registro.set(tipo)  # Mantener el mismo tipo de usuario
            else:
                respuesta = messagebox.askquestion("Contraseña incorrecta", 
                                                 "Contraseña incorrecta\n¿Desea recuperar su contraseña?",
                                                 icon='warning')
                if respuesta == 'yes':
                    # Buscar email del usuario
                    email_usuario = ""
                    for u in self.sistema_auth.usuarios.get("usuarios", []):
                        if u["usuario"] == usuario:
                            email_usuario = u["email"]
                            break
                    
                    messagebox.showinfo("Recuperación enviada", 
                                      f"Se ha enviado un correo de recuperación a {email_usuario}")
    
    def registrar(self):
        """Maneja el proceso de registro - VERSIÓN CORREGIDA"""
        tipo = self.tipo_registro.get()
        usuario = self.widgets_registro["entry_usuario_registro"].get().strip()
        email = self.widgets_registro["entry_email_registro"].get().strip()
        password = self.widgets_registro["entry_password_registro"].get()
        confirmar_password = self.widgets_registro["entry_confirmar_password"].get()
        
        # Validaciones
        if not all([usuario, email, password, confirmar_password]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        if password != confirmar_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            self.widgets_registro["entry_password_registro"].delete(0, tk.END)
            self.widgets_registro["entry_confirmar_password"].delete(0, tk.END)
            self.widgets_registro["entry_password_registro"].focus_set()
            return
        
        if self.sistema_auth.registrar_usuario(tipo, usuario, email, password):
            # Limpiar campos después del registro exitoso
            for widget in self.widgets_registro.values():
                widget.delete(0, tk.END)
            
            # Mostrar mensaje y cambiar a pestaña de login
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Ahora puede iniciar sesión.")
            self.notebook.select(0)  # Volver a pestaña de login
    
    def abrir_interfaz_principal(self, usuario: dict):
        """Abre la interfaz principal según el tipo de usuario"""
        self.withdraw()  # Ocultar ventana de login
        
        if usuario["tipo"] == "feriante":
            ventana_principal = InterfazFeriante(self, usuario)
        else:
            ventana_principal = InterfazPuestero(self, usuario)
        
        ventana_principal.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_sesion(ventana_principal))
    
    def cerrar_sesion(self, ventana_principal):
        """Cierra sesión y vuelve al login"""
        ventana_principal.destroy()
        self.deiconify()  # Mostrar ventana de login nuevamente

# ... (el resto del código se mantiene igual)