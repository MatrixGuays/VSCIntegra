import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import hashlib
import uuid
from typing import Dict, List, Optional

# CONSTANTES DEL SISTEMA
RANGO_FECHAS = ("01/01/2000", "31/12/2050")
PALETA_COLORES = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8",
    "#F7DC6F", "#BB8FCE", "#85C1E9", "#F8C471", "#82E0AA", "#F1948A", "#85C1E9",
    "#D7BDE2", "#F9E79F", "#A9DFBF", "#FAD7A0", "#D6EAF8", "#D5DBDB", "#F5B7B1",
    "#AED6F1", "#A3E4D7", "#FDEBD0", "#E8DAEF", "#D1F2EB", "#FDEDEC", "#EAF2F8",
    "#FEF9E7", "#EAEDED"
]

class JSONHandler:
    """Manejador de archivos JSON"""
    
    @staticmethod
    def cargar_archivo(nombre_archivo: str) -> dict:
        """Carga un archivo JSON, creándolo si no existe"""
        try:
            if os.path.exists(nombre_archivo):
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Crear estructura básica si el archivo no existe
                estructura_base = {
                    "usuarios": {"usuarios": []},
                    "feriantes": {"feriantes": []},
                    "puestos": {"puestos": []},
                    "ferias": {"ferias": []},
                    "clientes_regulares": {"clientes_regulares": []},
                    "clientes_ocasionales": {"clientes_ocasionales": []},
                    "solicitudes": {"solicitudes": []},
                    "asistencias": {"asistencias": []}
                }
                
                if nombre_archivo in estructura_base:
                    data = estructura_base[nombre_archivo]
                else:
                    data = {}
                
                JSONHandler.guardar_archivo(nombre_archivo, data)
                return data
                
        except (json.JSONDecodeError, Exception) as e:
            messagebox.showerror("Error", f"Error al cargar {nombre_archivo}: {str(e)}")
            return {}
    
    @staticmethod
    def guardar_archivo(nombre_archivo: str, data: dict):
        """Guarda datos en un archivo JSON"""
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar {nombre_archivo}: {str(e)}")

class SistemaAutenticacion:
    """Sistema de autenticación y gestión de usuarios"""
    
    def __init__(self):
        self.usuarios = JSONHandler.cargar_archivo("usuarios.json")
        self.feriantes = JSONHandler.cargar_archivo("feriantes.json")
        self.usuario_actual = None
    
    def hash_password(self, password: str) -> str:
        """Genera hash de contraseña (básico para demostración)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generar_id(self) -> str:
        """Genera un ID único"""
        return str(uuid.uuid4())
    
    def validar_email(self, email: str) -> bool:
        """Valida formato de email"""
        return '@' in email and '.' in email.split('@')[-1]
    
    def registrar_usuario(self, tipo: str, usuario: str, email: str, password: str) -> bool:
        """Registra un nuevo usuario"""
        # Validaciones
        if len(usuario.strip()) < 1:
            messagebox.showerror("Error", "El usuario no puede estar vacío")
            return False
        
        if not self.validar_email(email):
            messagebox.showerror("Error", "Email no válido")
            return False
        
        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return False
        
        # Verificar si el usuario ya existe
        for u in self.usuarios.get("usuarios", []):
            if u["usuario"] == usuario:
                messagebox.showerror("Error", "El usuario ya existe")
                return False
        
        # Crear nuevo usuario
        nuevo_usuario = {
            "id": self.generar_id(),
            "tipo": tipo,
            "usuario": usuario,
            "email": email,
            "contraseña": self.hash_password(password),
            "fecha_registro": datetime.now().isoformat(),
            "ultimo_login": None
        }
        
        self.usuarios["usuarios"].append(nuevo_usuario)
        JSONHandler.guardar_archivo("usuarios.json", self.usuarios)
        
        # Si es feriante, crear perfil básico
        if tipo == "feriante":
            nuevo_feriante = {
                "id_usuario": nuevo_usuario["id"],
                "nombre_completo": "",
                "telefono": "",
                "rubro_principal": "",
                "horarios_preferidos": {"dias": [], "horario": {"inicio": "08:00", "fin": "18:00"}},
                "ubicaciones_preferidas": [],
                "fecha_actualizacion": datetime.now().isoformat()
            }
            self.feriantes["feriantes"].append(nuevo_feriante)
            JSONHandler.guardar_archivo("feriantes.json", self.feriantes)
        
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        return True
    
    def autenticar_usuario(self, tipo: str, usuario: str, password: str) -> dict:
        """Autentica un usuario"""
        password_hash = self.hash_password(password)
        
        for u in self.usuarios.get("usuarios", []):
            if (u["usuario"] == usuario and u["tipo"] == tipo and 
                u["contraseña"] == password_hash):
                
                # Actualizar último login
                u["ultimo_login"] = datetime.now().isoformat()
                JSONHandler.guardar_archivo("usuarios.json", self.usuarios)
                
                self.usuario_actual = u
                return u
        
        return None

class CalendarioWidget(tk.Frame):
    """Widget de calendario reutilizable"""
    
    def __init__(self, parent, ancho=400, alto=300, modo_lectura=False):
        super().__init__(parent)
        self.parent = parent
        self.modo_lectura = modo_lectura
        self.ancho = ancho
        self.alto = alto
        self.fecha_actual = datetime.now()
        self.dias_seleccionados = set()
        self.ferias = JSONHandler.cargar_archivo("ferias.json").get("ferias", [])
        self.solicitudes = JSONHandler.cargar_archivo("solicitudes.json").get("solicitudes", [])
        
        self.construir_interfaz()
        self.actualizar_calendario()
    
    def construir_interfaz(self):
        """Construye la interfaz del calendario"""
        # Frame de controles
        frame_controles = tk.Frame(self)
        frame_controles.pack(pady=5)
        
        btn_anterior = tk.Button(frame_controles, text="◀", command=self.mes_anterior)
        btn_anterior.pack(side=tk.LEFT, padx=5)
        
        self.lbl_mes_anio = tk.Label(frame_controles, text="", font=("Arial", 12, "bold"))
        self.lbl_mes_anio.pack(side=tk.LEFT, padx=10)
        
        btn_siguiente = tk.Button(frame_controles, text="▶", command=self.mes_siguiente)
        btn_siguiente.pack(side=tk.LEFT, padx=5)
        
        # Frame del calendario
        frame_calendario = tk.Frame(self)
        frame_calendario.pack(pady=5)
        
        # Días de la semana
        dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
        for i, dia in enumerate(dias_semana):
            lbl = tk.Label(frame_calendario, text=dia, width=5, height=1, 
                          font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=i, padx=1, pady=1)
        
        # Cuadrícula de días
        self.botones_dias = []
        for fila in range(6):
            fila_botones = []
            for columna in range(7):
                btn = tk.Button(frame_calendario, text="", width=5, height=2,
                               command=lambda r=fila, c=columna: self.seleccionar_dia(r, c))
                btn.grid(row=fila+1, column=columna, padx=1, pady=1)
                fila_botones.append(btn)
            self.botones_dias.append(fila_botones)
    
    def mes_anterior(self):
        """Navega al mes anterior"""
        self.fecha_actual = self.fecha_actual.replace(day=1) - timedelta(days=1)
        self.actualizar_calendario()
    
    def mes_siguiente(self):
        """Navega al mes siguiente"""
        if self.fecha_actual.month == 12:
            self.fecha_actual = self.fecha_actual.replace(year=self.fecha_actual.year + 1, month=1, day=1)
        else:
            self.fecha_actual = self.fecha_actual.replace(month=self.fecha_actual.month + 1, day=1)
        self.actualizar_calendario()
    
    def actualizar_calendario(self):
        """Actualiza la visualización del calendario"""
        # Actualizar label del mes y año
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes_anio.config(text=f"{meses[self.fecha_actual.month-1]} {self.fecha_actual.year}")
        
        # Limpiar botones
        for fila in self.botones_dias:
            for btn in fila:
                btn.config(text="", state=tk.NORMAL, bg="SystemButtonFace", relief="raised")
        
        # Primer día del mes
        primer_dia = self.fecha_actual.replace(day=1)
        dia_semana = primer_dia.weekday()  # 0=Lunes, 6=Domingo
        
        # Llenar calendario
        dia_actual = 1
        for fila in range(6):
            for columna in range(7):
                if (fila == 0 and columna < dia_semana) or dia_actual > 31:
                    continue
                
                try:
                    fecha = self.fecha_actual.replace(day=dia_actual)
                    self.botones_dias[fila][columna].config(text=str(dia_actual))
                    
                    # Colorear según disponibilidad de ferias
                    if self.tiene_ferias_disponibles(fecha):
                        self.botones_dias[fila][columna].config(bg="#90EE90")  # Verde
                    elif self.tiene_solicitudes_propias(fecha):
                        self.botones_dias[fila][columna].config(bg="#ADD8E6")  # Azul claro
                    
                    dia_actual += 1
                except ValueError:
                    break
    
    def tiene_ferias_disponibles(self, fecha: datetime) -> bool:
        """Verifica si hay ferias disponibles en una fecha"""
        dia_semana = fecha.strftime("%a")[0].upper()  # L, M, X, J, V, S, D
        
        for feria in self.ferias:
            if (feria.get("activa", False) and 
                feria.get("visible_feriantes", False) and
                dia_semana in feria.get("dias_semana", [])):
                return True
        return False
    
    def tiene_solicitudes_propias(self, fecha: datetime) -> bool:
        """Verifica si el usuario tiene solicitudes en una fecha"""
        # Esta función se implementaría completamente con el sistema de autenticación
        return False
    
    def seleccionar_dia(self, fila: int, columna: int):
        """Maneja la selección de un día"""
        if self.modo_lectura:
            return
            
        texto_boton = self.botones_dias[fila][columna].cget("text")
        if not texto_boton:
            return
        
        dia = int(texto_boton)
        fecha_seleccionada = self.fecha_actual.replace(day=dia)
        
        # Cambiar estado visual del botón
        if fecha_seleccionada in self.dias_seleccionados:
            self.dias_seleccionados.remove(fecha_seleccionada)
            self.botones_dias[fila][columna].config(relief="raised")
        else:
            self.dias_seleccionados.add(fecha_seleccionada)
            self.botones_dias[fila][columna].config(relief="sunken")

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

class InterfazFeriante(tk.Toplevel):
    """Interfaz principal para usuarios Feriantes"""
    
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.title("Sistema de Ferias - Feriante")
        self.geometry("800x600")
        self.usuario = usuario
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del feriante"""
        # Barra superior de navegación
        frame_superior = tk.Frame(self, bg="#2C3E50", height=40)
        frame_superior.pack(fill=tk.X, side=tk.TOP)
        frame_superior.pack_propagate(False)
        
        botones_nav = [
            ("Buscar Ferias", self.mostrar_buscar_ferias),
            ("Mis Solicitudes", self.mostrar_mis_solicitudes),
            ("Calculadora", self.mostrar_calculadora),
            ("Mi Perfil", self.mostrar_mi_perfil),
            ("Cerrar Sesión", self.cerrar_sesion)
        ]
        
        for texto, comando in botones_nav:
            btn = tk.Button(frame_superior, text=texto, command=comando,
                           bg="#34495E", fg="white", relief="flat")
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Área principal
        self.frame_principal = tk.Frame(self)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar módulo por defecto
        self.mostrar_buscar_ferias()
    
    def mostrar_buscar_ferias(self):
        """Muestra el módulo de búsqueda de ferias"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Buscar Ferias", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame de filtros
        frame_filtros = tk.LabelFrame(self.frame_principal, text="Filtros de Búsqueda")
        frame_filtros.pack(fill=tk.X, pady=10)
        
        # Días de la semana
        frame_dias = tk.Frame(frame_filtros)
        frame_dias.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_dias, text="Días:").pack(side=tk.LEFT)
        
        self.dias_seleccionados = {}
        dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
        for dia in dias_semana:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_dias, text=dia, variable=var)
            chk.pack(side=tk.LEFT, padx=2)
            self.dias_seleccionados[dia] = var
        
        # Rango horario
        frame_horario = tk.Frame(frame_filtros)
        frame_horario.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_horario, text="Horario:").pack(side=tk.LEFT)
        self.entry_hora_desde = tk.Entry(frame_horario, width=8)
        self.entry_hora_desde.pack(side=tk.LEFT, padx=5)
        self.entry_hora_desde.insert(0, "08:00")
        
        tk.Label(frame_horario, text="a").pack(side=tk.LEFT)
        self.entry_hora_hasta = tk.Entry(frame_horario, width=8)
        self.entry_hora_hasta.pack(side=tk.LEFT, padx=5)
        self.entry_hora_hasta.insert(0, "18:00")
        
        # Ubicación
        frame_ubicacion = tk.Frame(frame_filtros)
        frame_ubicacion.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_ubicacion, text="Ubicación:").pack(side=tk.LEFT)
        self.entry_ubicacion = tk.Entry(frame_ubicacion, width=30)
        self.entry_ubicacion.pack(side=tk.LEFT, padx=5)
        
        # Rubro
        frame_rubro = tk.Frame(frame_filtros)
        frame_rubro.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_rubro, text="Rubro:").pack(side=tk.LEFT)
        self.combo_rubro = ttk.Combobox(frame_rubro, values=[
            "Alimentación", "Ropa", "Artículos para el hogar", "Electrónica",
            "Juguetes", "Libros", "Artesanías", "Otros"
        ])
        self.combo_rubro.pack(side=tk.LEFT, padx=5)
        
        # Botón buscar
        btn_buscar = tk.Button(frame_filtros, text="Buscar Ferias", 
                              command=self.buscar_ferias, bg="#3498DB", fg="white")
        btn_buscar.pack(pady=10)
        
        # Calendario
        frame_calendario = tk.LabelFrame(self.frame_principal, text="Calendario de Ferias Disponibles")
        frame_calendario.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.calendario = CalendarioWidget(frame_calendario, modo_lectura=True)
        self.calendario.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def buscar_ferias(self):
        """Ejecuta la búsqueda de ferias con los filtros aplicados"""
        # En una implementación completa, aquí se filtrarían las ferias
        self.calendario.actualizar_calendario()
        messagebox.showinfo("Búsqueda", "Búsqueda ejecutada (funcionalidad de demostración)")
    
    def mostrar_mis_solicitudes(self):
        """Muestra el módulo de mis solicitudes"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Mis Solicitudes", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame de filtros de estado
        frame_filtros = tk.Frame(self.frame_principal)
        frame_filtros.pack(fill=tk.X, pady=10)
        
        estados = ["Pendientes", "Aceptadas", "Rechazadas", "Todas"]
        for estado in estados:
            btn = tk.Button(frame_filtros, text=state, 
                           command=lambda e=estado: self.filtrar_solicitudes(e))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview para mostrar solicitudes
        frame_tabla = tk.Frame(self.frame_principal)
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        columnas = ("Feria", "Puesto", "Tipo", "Fecha Envío", "Estado")
        self.tree_solicitudes = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            self.tree_solicitudes.heading(col, text=col)
            self.tree_solicitudes.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, 
                                 command=self.tree_solicitudes.yview)
        self.tree_solicitudes.configure(yscrollcommand=scrollbar.set)
        
        self.tree_solicitudes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos de ejemplo
        self.cargar_solicitudes_ejemplo()
    
    def cargar_solicitudes_ejemplo(self):
        """Carga datos de ejemplo en la tabla de solicitudes"""
        datos_ejemplo = [
            ("Feria Central", "Puesto 15", "Regular", "01/03/2024", "Pendiente"),
            ("Mercado Artesanal", "Puesto 8", "Ocasional", "28/02/2024", "Aceptada"),
            ("Plaza Comercial", "Puesto 22", "Regular", "25/02/2024", "Rechazada")
        ]
        
        for dato in datos_ejemplo:
            self.tree_solicitudes.insert("", tk.END, values=dato)
    
    def filtrar_solicitudes(self, estado: str):
        """Filtra las solicitudes por estado"""
        # En una implementación completa, aquí se filtrarían las solicitudes reales
        messagebox.showinfo("Filtro", f"Mostrando solicitudes: {estado}")
    
    def mostrar_calculadora(self):
        """Muestra el módulo de calculadora de ganancias"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Calculadora de Ganancias", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Campos de entrada
        frame_entradas = tk.LabelFrame(self.frame_principal, text="Datos de Entrada")
        frame_entradas.pack(fill=tk.X, pady=10)
        
        campos = [
            ("Ventas estimadas por día:", "ventas_dia"),
            ("Costo de productos/materia prima:", "costo_productos"),
            ("Gastos de transporte:", "gastos_transporte"),
            ("Costo de alquiler del puesto:", "costo_alquiler"),
            ("Otros gastos:", "otros_gastos")
        ]
        
        self.variables_calculadora = {}
        
        for texto, clave in campos:
            frame = tk.Frame(frame_entradas)
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame, text=texto, width=25, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar(value="0")
            entry = tk.Entry(frame, textvariable=var, width=15)
            entry.pack(side=tk.LEFT, padx=5)
            
            self.variables_calculadora[clave] = var
        
        # Botón calcular
        btn_calcular = tk.Button(frame_entradas, text="Calcular Ganancia", 
                                command=self.calcular_ganancias, bg="#27AE60", fg="white")
        btn_calcular.pack(pady=10)
        
        # Resultados
        frame_resultados = tk.LabelFrame(self.frame_principal, text="Resultados")
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.lbl_ganancia_diaria = tk.Label(frame_resultados, text="Ganancia diaria neta: $0.00")
        self.lbl_ganancia_diaria.pack(pady=5)
        
        self.lbl_ganancia_semanal = tk.Label(frame_resultados, text="Ganancia semanal: $0.00")
        self.lbl_ganancia_semanal.pack(pady=5)
        
        self.lbl_ganancia_mensual = tk.Label(frame_resultados, text="Ganancia mensual: $0.00")
        self.lbl_ganancia_mensual.pack(pady=5)
        
        self.lbl_roi = tk.Label(frame_resultados, text="ROI: 0%")
        self.lbl_roi.pack(pady=5)
    
    def calcular_ganancias(self):
        """Calcula las ganancias basadas en los datos ingresados"""
        try:
            ventas = float(self.variables_calculadora["ventas_dia"].get() or 0)
            costos = float(self.variables_calculadora["costo_productos"].get() or 0)
            transporte = float(self.variables_calculadora["gastos_transporte"].get() or 0)
            alquiler = float(self.variables_calculadora["costo_alquiler"].get() or 0)
            otros = float(self.variables_calculadora["otros_gastos"].get() or 0)
            
            ganancia_diaria = ventas - costos - transporte - alquiler - otros
            ganancia_semanal = ganancia_diaria * 5  # 5 días por semana
            ganancia_mensual = ganancia_semanal * 4  # 4 semanas por mes
            
            inversion_total = costos + transporte + alquiler + otros
            roi = (ganancia_diaria / inversion_total * 100) if inversion_total > 0 else 0
            
            self.lbl_ganancia_diaria.config(text=f"Ganancia diaria neta: ${ganancia_diaria:.2f}")
            self.lbl_ganancia_semanal.config(text=f"Ganancia semanal: ${ganancia_semanal:.2f}")
            self.lbl_ganancia_mensual.config(text=f"Ganancia mensual: ${ganancia_mensual:.2f}")
            self.lbl_roi.config(text=f"ROI: {roi:.1f}%")
            
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
    
    def mostrar_mi_perfil(self):
        """Muestra el módulo de perfil del usuario"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Mi Perfil", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Cargar datos del feriante
        feriantes = JSONHandler.cargar_archivo("feriantes.json").get("feriantes", [])
        datos_feriante = None
        
        for f in feriantes:
            if f["id_usuario"] == self.usuario["id"]:
                datos_feriante = f
                break
        
        if not datos_feriante:
            datos_feriante = {
                "nombre_completo": "",
                "telefono": "",
                "rubro_principal": "",
                "horarios_preferidos": {"dias": [], "horario": {"inicio": "08:00", "fin": "18:00"}},
                "ubicaciones_preferidas": []
            }
        
        # Formulario de edición
        frame_formulario = tk.LabelFrame(self.frame_principal, text="Información Personal")
        frame_formulario.pack(fill=tk.X, pady=10)
        
        # Nombre completo
        frame_nombre = tk.Frame(frame_formulario)
        frame_nombre.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_nombre, text="Nombre completo:", width=15, anchor="w").pack(side=tk.LEFT)
        self.entry_nombre = tk.Entry(frame_nombre, width=30)
        self.entry_nombre.insert(0, datos_feriante.get("nombre_completo", ""))
        self.entry_nombre.pack(side=tk.LEFT, padx=5)
        
        # Teléfono
        frame_telefono = tk.Frame(frame_formulario)
        frame_telefono.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_telefono, text="Teléfono:", width=15, anchor="w").pack(side=tk.LEFT)
        self.entry_telefono = tk.Entry(frame_telefono, width=30)
        self.entry_telefono.insert(0, datos_feriante.get("telefono", ""))
        self.entry_telefono.pack(side=tk.LEFT, padx=5)
        
        # Email
        frame_email = tk.Frame(frame_formulario)
        frame_email.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_email, text="Email:", width=15, anchor="w").pack(side=tk.LEFT)
        self.entry_email = tk.Entry(frame_email, width=30)
        self.entry_email.insert(0, self.usuario.get("email", ""))
        self.entry_email.config(state="readonly")
        self.entry_email.pack(side=tk.LEFT, padx=5)
        
        # Rubro principal
        frame_rubro = tk.Frame(frame_formulario)
        frame_rubro.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_rubro, text="Rubro principal:", width=15, anchor="w").pack(side=tk.LEFT)
        self.combo_rubro_perfil = ttk.Combobox(frame_rubro, values=[
            "Alimentación", "Ropa", "Artículos para el hogar", "Electrónica",
            "Juguetes", "Libros", "Artesanías", "Otros"
        ], width=27)
        self.combo_rubro_perfil.set(datos_feriante.get("rubro_principal", ""))
        self.combo_rubro_perfil.pack(side=tk.LEFT, padx=5)
        
        # Botones
        frame_botones = tk.Frame(frame_formulario)
        frame_botones.pack(pady=10)
        
        btn_guardar = tk.Button(frame_botones, text="Guardar Cambios", 
                               command=self.guardar_perfil, bg="#27AE60", fg="white")
        btn_guardar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = tk.Button(frame_botones, text="Cancelar", 
                                command=self.mostrar_mi_perfil)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def guardar_perfil(self):
        """Guarda los cambios del perfil"""
        # En una implementación completa, aquí se guardarían los datos
        messagebox.showinfo("Perfil", "Cambios guardados correctamente (funcionalidad de demostración)")
    
    def limpiar_frame_principal(self):
        """Limpia el frame principal"""
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self.destroy()
        self.master.deiconify()

class InterfazPuestero(tk.Toplevel):
    """Interfaz principal para usuarios Puesteros"""
    
    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.title("Sistema de Ferias - Puestero")
        self.geometry("1000x700")
        self.usuario = usuario
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del puestero"""
        # Barra superior de navegación
        frame_superior = tk.Frame(self, bg="#2C3E50", height=40)
        frame_superior.pack(fill=tk.X, side=tk.TOP)
        frame_superior.pack_propagate(False)
        
        botones_nav = [
            ("Calendario", self.mostrar_calendario),
            ("Clientes", self.mostrar_clientes),
            ("Ferias", self.mostrar_ferias),
            ("Ingresos", self.mostrar_ingresos),
            ("Notificaciones", self.mostrar_notificaciones),
            ("Cerrar Sesión", self.cerrar_sesion)
        ]
        
        for texto, comando in botones_nav:
            btn = tk.Button(frame_superior, text=texto, command=comando,
                           bg="#34495E", fg="white", relief="flat")
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Área principal
        self.frame_principal = tk.Frame(self)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra inferior de resumen
        frame_inferior = tk.Frame(self, bg="#ECF0F1", height=60)
        frame_inferior.pack(fill=tk.X, side=tk.BOTTOM)
        frame_inferior.pack_propagate(False)
        
        # Mostrar módulo por defecto
        self.mostrar_calendario()
    
    def mostrar_calendario(self):
        """Muestra el módulo de calendario del puestero"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Calendario de Ferias", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Calendario interactivo
        frame_calendario = tk.LabelFrame(self.frame_principal, text="Mis Ferias")
        frame_calendario.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.calendario_puestero = CalendarioWidget(frame_calendario, modo_lectura=False)
        self.calendario_puestero.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Información adicional
        frame_info = tk.Frame(self.frame_principal)
        frame_info.pack(fill=tk.X, pady=10)
        
        # Leyenda de colores
        leyenda_frame = tk.LabelFrame(frame_info, text="Leyenda")
        leyenda_frame.pack(side=tk.LEFT, padx=10)
        
        colores_leyenda = [
            ("Verde", "Feria disponible para feriantes"),
            ("Azul claro", "Tiene solicitudes pendientes"),
            ("Blanco", "Sin ferias programadas")
        ]
        
        for color, descripcion in colores_leyenda:
            frame_color = tk.Frame(leyenda_frame)
            frame_color.pack(anchor="w", pady=2)
            
            if color == "Verde":
                bg_color = "#90EE90"
            elif color == "Azul claro":
                bg_color = "#ADD8E6"
            else:
                bg_color = "white"
            
            lbl_color = tk.Label(frame_color, text="   ", bg=bg_color, width=3)
            lbl_color.pack(side=tk.LEFT, padx=5)
            
            lbl_desc = tk.Label(frame_color, text=descripcion)
            lbl_desc.pack(side=tk.LEFT)
    
    def mostrar_clientes(self):
        """Muestra el módulo de gestión de clientes"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Gestión de Clientes", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Notebook para pestañas de clientes
        notebook = ttk.Notebook(self.frame_principal)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña Regulares
        frame_regulares = ttk.Frame(notebook)
        notebook.add(frame_regulares, text="Clientes Regulares")
        
        # Pestaña Ocasionales
        frame_ocasionales = ttk.Frame(notebook)
        notebook.add(frame_ocasionales, text="Clientes Ocasionales")
        
        # Pestaña Todos
        frame_todos = ttk.Frame(notebook)
        notebook.add(frame_todos, text="Todos los Clientes")
        
        self.crear_tabla_clientes(frame_regulares, "regulares")
        self.crear_tabla_clientes(frame_ocasionales, "ocasionales")
        self.crear_tabla_clientes(frame_todos, "todos")
    
    def crear_tabla_clientes(self, parent, tipo: str):
        """Crea una tabla de clientes"""
        # Frame de botones
        frame_botones = tk.Frame(parent)
        frame_botones.pack(fill=tk.X, pady=5)
        
        if tipo == "regulares":
            btn_agregar = tk.Button(frame_botones, text="Agregar Regular", 
                                   command=self.agregar_cliente_regular)
            btn_agregar.pack(side=tk.LEFT, padx=5)
        elif tipo == "ocasionales":
            btn_agregar = tk.Button(frame_botones, text="Agregar Ocasional", 
                                   command=self.agregar_cliente_ocasional)
            btn_agregar.pack(side=tk.LEFT, padx=5)
        
        # Treeview para clientes
        frame_tabla = tk.Frame(parent)
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        if tipo == "todos":
            columnas = ("Tipo", "Nombre", "Rubro", "Feria", "Teléfono", "Última Asistencia")
        elif tipo == "regulares":
            columnas = ("Nombre", "Rubro", "Feria", "Puesto", "Días", "Teléfono")
        else:  # ocasionales
            columnas = ("Nombre", "Rubro", "Teléfono", "Última Asistencia", "Fechas Totales")
        
        tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos de ejemplo
        self.cargar_clientes_ejemplo(tree, tipo)
    
    def cargar_clientes_ejemplo(self, tree, tipo: str):
        """Carga datos de ejemplo en la tabla de clientes"""
        if tipo == "regulares":
            datos = [
                ("Juan Pérez", "Alimentación", "Feria Central", "Puesto 15", "L-M-X-J-V", "123-456-789"),
                ("María García", "Ropa", "Mercado Artesanal", "Puesto 8", "S-D", "987-654-321")
            ]
        elif tipo == "ocasionales":
            datos = [
                ("Carlos López", "Electrónica", "555-123-456", "01/03/2024", "3"),
                ("Ana Martínez", "Juguetes", "555-789-012", "28/02/2024", "1")
            ]
        else:  # todos
            datos = [
                ("Regular", "Juan Pérez", "Alimentación", "Feria Central", "123-456-789", "01/03/2024"),
                ("Regular", "María García", "Ropa", "Mercado Artesanal", "987-654-321", "28/02/2024"),
                ("Ocasional", "Carlos López", "Electrónica", "Feria Central", "555-123-456", "01/03/2024")
            ]
        
        for dato in datos:
            tree.insert("", tk.END, values=dato)
    
    def agregar_cliente_regular(self):
        """Abre formulario para agregar cliente regular"""
        messagebox.showinfo("Agregar Cliente", "Formulario para agregar cliente regular (funcionalidad de demostración)")
    
    def agregar_cliente_ocasional(self):
        """Abre formulario para agregar cliente ocasional"""
        messagebox.showinfo("Agregar Cliente", "Formulario para agregar cliente ocasional (funcionalidad de demostración)")
    
    def mostrar_ferias(self):
        """Muestra el módulo de gestión de ferias"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Gestión de Ferias", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Botón nueva feria
        btn_nueva_feria = tk.Button(self.frame_principal, text="Nueva Feria", 
                                   command=self.crear_nueva_feria, bg="#3498DB", fg="white")
        btn_nueva_feria.pack(pady=10)
        
        # Lista de ferias
        frame_lista = tk.LabelFrame(self.frame_principal, text="Mis Ferias Activas")
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para ferias
        columnas = ("Nombre", "Días", "Color", "Puestos", "Estado", "Visible")
        self.tree_ferias = ttk.Treeview(frame_lista, columns=columnas, show="headings")
        
        for col in columnas:
            self.tree_ferias.heading(col, text=col)
            self.tree_ferias.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_ferias.yview)
        self.tree_ferias.configure(yscrollcommand=scrollbar.set)
        
        self.tree_ferias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de acciones
        frame_acciones = tk.Frame(frame_lista)
        frame_acciones.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        btn_editar = tk.Button(frame_acciones, text="Editar", command=self.editar_feria)
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        btn_eliminar = tk.Button(frame_acciones, text="Eliminar", command=self.eliminar_feria)
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        btn_mostrar_ocultar = tk.Button(frame_acciones, text="Mostrar/Ocultar", 
                                       command=self.mostrar_ocultar_feria)
        btn_mostrar_ocultar.pack(side=tk.LEFT, padx=5)
        
        # Cargar datos de ejemplo
        self.cargar_ferias_ejemplo()
    
    def cargar_ferias_ejemplo(self):
        """Carga datos de ejemplo en la tabla de ferias"""
        datos_ejemplo = [
            ("Feria Central", "L-M-X-J-V", "🔵", "25/30", "Activa", "Sí"),
            ("Mercado Artesanal", "S-D", "🟢", "15/15", "Activa", "Sí"),
            ("Feria Nocturna", "V-S", "🔴", "0/10", "Inactiva", "No")
        ]
        
        for dato in datos_ejemplo:
            self.tree_ferias.insert("", tk.END, values=dato)
    
    def crear_nueva_feria(self):
        """Abre formulario para crear nueva feria"""
        messagebox.showinfo("Nueva Feria", "Formulario para crear nueva feria (funcionalidad de demostración)")
    
    def editar_feria(self):
        """Abre formulario para editar feria seleccionada"""
        seleccion = self.tree_ferias.selection()
        if seleccion:
            messagebox.showinfo("Editar Feria", "Formulario para editar feria (funcionalidad de demostración)")
        else:
            messagebox.showwarning("Selección", "Seleccione una feria para editar")
    
    def eliminar_feria(self):
        """Elimina la feria seleccionada"""
        seleccion = self.tree_ferias.selection()
        if seleccion:
            respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta feria?")
            if respuesta:
                self.tree_ferias.delete(seleccion)
                messagebox.showinfo("Éxito", "Feria eliminada correctamente")
        else:
            messagebox.showwarning("Selección", "Seleccione una feria para eliminar")
    
    def mostrar_ocultar_feria(self):
        """Cambia la visibilidad de la feria seleccionada"""
        seleccion = self.tree_ferias.selection()
        if seleccion:
            messagebox.showinfo("Visibilidad", "Visibilidad de feria cambiada (funcionalidad de demostración)")
        else:
            messagebox.showwarning("Selección", "Seleccione una feria")
    
    def mostrar_ingresos(self):
        """Muestra el módulo de ingresos"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Reporte de Ingresos", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Selector de período
        frame_periodo = tk.Frame(self.frame_principal)
        frame_periodo.pack(fill=tk.X, pady=10)
        
        tk.Label(frame_periodo, text="Período:").pack(side=tk.LEFT)
        
        periodos = ["Diario", "Semanal", "Mensual", "Anual", "Personalizado"]
        self.periodo_seleccionado = tk.StringVar(value="Mensual")
        
        for periodo in periodos:
            rb = tk.Radiobutton(frame_periodo, text=periodo, variable=self.periodo_seleccionado,
                               value=periodo, command=self.actualizar_reportes)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Frame de resultados
        frame_resultados = tk.LabelFrame(self.frame_principal, text="Resumen Financiero")
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Métricas clave
        frame_metricas = tk.Frame(frame_resultados)
        frame_metricas.pack(fill=tk.X, pady=10)
        
        metricas = [
            ("Ingresos por Alquileres:", "$1,250.00"),
            ("Gastos de Mantenimiento:", "$450.00"),
            ("Ganancia Neta:", "$800.00"),
            ("Porcentaje de Ocupación:", "75%")
        ]
        
        for texto, valor in metricas:
            frame_metrica = tk.Frame(frame_metricas)
            frame_metrica.pack(side=tk.LEFT, padx=20)
            
            tk.Label(frame_metrica, text=texto, font=("Arial", 10)).pack()
            tk.Label(frame_metrica, text=valor, font=("Arial", 12, "bold")).pack()
        
        # Gráficos (simulados con labels)
        frame_graficos = tk.Frame(frame_resultados)
        frame_graficos.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gráfico de columnas
        frame_columna = tk.LabelFrame(frame_graficos, text="Ingresos vs Gastos")
        frame_columna.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        lbl_grafico_columna = tk.Label(frame_columna, text="[Gráfico de columnas]\nIngresos: ████████\nGastos:  ████", 
                                      height=8)
        lbl_grafico_columna.pack(pady=10)
        
        # Gráfico circular
        frame_circular = tk.LabelFrame(frame_graficos, text="Distribución por Feria")
        frame_circular.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        lbl_grafico_circular = tk.Label(frame_circular, text="[Gráfico circular]\nFeria Central: 50%\nMercado Artesanal: 30%\nOtras: 20%", 
                                       height=8)
        lbl_grafico_circular.pack(pady=10)
    
    def actualizar_reportes(self):
        """Actualiza los reportes según el período seleccionado"""
        periodo = self.periodo_seleccionado.get()
        messagebox.showinfo("Actualizar", f"Reportes actualizados para período: {periodo}")
    
    def mostrar_notificaciones(self):
        """Muestra el módulo de notificaciones"""
        self.limpiar_frame_principal()
        
        tk.Label(self.frame_principal, text="Bandeja de Notificaciones", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Filtros de estado
        frame_filtros = tk.Frame(self.frame_principal)
        frame_filtros.pack(fill=tk.X, pady=10)
        
        estados = ["Todas", "Pendientes", "Aceptadas", "Rechazadas"]
        for estado in estados:
            btn = tk.Button(frame_filtros, text=estado, 
                           command=lambda e=estado: self.filtrar_notificaciones(e))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Lista de notificaciones
        frame_notificaciones = tk.LabelFrame(self.frame_principal, text="Solicitudes Recibidas")
        frame_notificaciones.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para notificaciones
        columnas = ("Estado", "Feriante", "Rubro", "Feria", "Puesto", "Tipo", "Fecha")
        self.tree_notificaciones = ttk.Treeview(frame_notificaciones, columns=columnas, show="headings")
        
        for col in columnas:
            self.tree_notificaciones.heading(col, text=col)
            self.tree_notificaciones.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_notificaciones, orient=tk.VERTICAL, 
                                 command=self.tree_notificaciones.yview)
        self.tree_notificaciones.configure(yscrollcommand=scrollbar.set)
        
        self.tree_notificaciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de acciones
        frame_acciones = tk.Frame(frame_notificaciones)
        frame_acciones.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        btn_aceptar = tk.Button(frame_acciones, text="Aceptar", command=self.aceptar_solicitud,
                               bg="#27AE60", fg="white")
        btn_aceptar.pack(side=tk.LEFT, padx=5)
        
        btn_rechazar = tk.Button(frame_acciones, text="Rechazar", command=self.rechazar_solicitud,
                                bg="#E74C3C", fg="white")
        btn_rechazar.pack(side=tk.LEFT, padx=5)
        
        btn_ver_perfil = tk.Button(frame_acciones, text="Ver Perfil Feriante", 
                                  command=self.ver_perfil_feriante)
        btn_ver_perfil.pack(side=tk.LEFT, padx=5)
        
        # Cargar datos de ejemplo
        self.cargar_notificaciones_ejemplo()
    
    def cargar_notificaciones_ejemplo(self):
        """Carga datos de ejemplo en la tabla de notificaciones"""
        datos_ejemplo = [
            ("Pendiente", "Juan Pérez", "Alimentación", "Feria Central", "Puesto 15", "Regular", "01/03/2024"),
            ("Aceptada", "María García", "Ropa", "Mercado Artesanal", "Puesto 8", "Ocasional", "28/02/2024"),
            ("Rechazada", "Carlos López", "Electrónica", "Feria Central", "Puesto 22", "Regular", "25/02/2024")
        ]
        
        for dato in datos_ejemplo:
            self.tree_notificaciones.insert("", tk.END, values=dato)
    
    def filtrar_notificaciones(self, estado: str):
        """Filtra las notificaciones por estado"""
        messagebox.showinfo("Filtro", f"Mostrando notificaciones: {estado}")
    
    def aceptar_solicitud(self):
        """Acepta la solicitud seleccionada"""
        seleccion = self.tree_notificaciones.selection()
        if seleccion:
            respuesta = messagebox.askyesno("Confirmar", "¿Aceptar esta solicitud?")
            if respuesta:
                messagebox.showinfo("Éxito", "Solicitud aceptada correctamente")
        else:
            messagebox.showwarning("Selección", "Seleccione una solicitud")
    
    def rechazar_solicitud(self):
        """Rechaza la solicitud seleccionada"""
        seleccion = self.tree_notificaciones.selection()
        if seleccion:
            respuesta = messagebox.askyesno("Confirmar", "¿Rechazar esta solicitud?")
            if respuesta:
                # Pedir motivo opcional
                motivo = tk.simpledialog.askstring("Motivo", "Ingrese motivo de rechazo (opcional):")
                messagebox.showinfo("Éxito", "Solicitud rechazada correctamente")
        else:
            messagebox.showwarning("Selección", "Seleccione una solicitud")
    
    def ver_perfil_feriante(self):
        """Muestra el perfil del feriante seleccionado"""
        seleccion = self.tree_notificaciones.selection()
        if seleccion:
            messagebox.showinfo("Perfil Feriante", "Mostrando perfil del feriante (funcionalidad de demostración)")
        else:
            messagebox.showwarning("Selección", "Seleccione una solicitud")
    
    def limpiar_frame_principal(self):
        """Limpia el frame principal"""
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        self.destroy()
        self.master.deiconify()

def main():
    """Función principal"""
    # Crear archivos JSON si no existen
    archivos = ["usuarios.json", "feriantes.json", "puestos.json", "ferias.json",
               "clientes_regulares.json", "clientes_ocasionales.json", 
               "solicitudes.json", "asistencias.json"]
    
    for archivo in archivos:
        JSONHandler.cargar_archivo(archivo)
    
    # Iniciar aplicación
    app = VentanaLogin()
    app.mainloop()

if __name__ == "__main__":
    main()