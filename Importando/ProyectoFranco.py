import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import date

# -----------------------------
# Clase principal del sistema
# -----------------------------
class SistemaAlquiler:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Alquiler de Puestos de Feria")
        self.root.geometry("800x600")

        self.archivo_puestos = "puestos.txt"
        self.archivo_regulares = "clientes_regulares.txt"
        self.archivo_rubros = "rubros.txt"

        self.puestos = self.cargar_datos(self.archivo_puestos, 12)
        self.clientes_regulares = self.cargar_datos(self.archivo_regulares)
        self.rubros = self.cargar_datos(self.archivo_rubros)

        self.crear_interfaz()

    # -------------------------------------
    # Cargar o crear datos por defecto
    # -------------------------------------
    def cargar_datos(self, archivo, cantidad=None):
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return [] if cantidad is None else [{"estado": "libre"} for _ in range(cantidad)]
        else:
            if cantidad:
                return [{"estado": "libre"} for _ in range(cantidad)]
            return []

    # -------------------------------------
    # Guardar datos
    # -------------------------------------
    def guardar_datos(self, archivo, datos):
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    # -------------------------------------
    # Crear la interfaz
    # -------------------------------------
    def crear_interfaz(self):
        frame_puestos = ttk.LabelFrame(self.root, text="Puestos disponibles", padding=10)
        frame_puestos.pack(pady=10, fill="both", expand=True)

        self.botones_puestos = []
        for i in range(12):
            btn = tk.Button(
                frame_puestos,
                text=f"Puesto {i+1}",
                width=15,
                height=3,
                bg=self.color_estado(self.puestos[i]["estado"]),
                command=lambda i=i: self.ver_puesto(i)
            )
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)
            self.botones_puestos.append(btn)

        frame_control = ttk.Frame(self.root, padding=10)
        frame_control.pack(fill="x")

        ttk.Button(frame_control, text="Alquilar Puesto", command=self.alquilar_puesto).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(frame_control, text="Liberar Puesto", command=self.liberar_puesto).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(frame_control, text="Gestionar Regulares", command=self.gestionar_regulares).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))

    # -------------------------------------
    # Colores de estado
    # -------------------------------------
    def color_estado(self, estado):
        return {"libre": "lightgreen", "ocupado": "salmon"}.get(estado, "lightgray")

    # -------------------------------------
    # Ver detalles del puesto
    # -------------------------------------
    def ver_puesto(self, idx):
        puesto = self.puestos[idx]
        if puesto["estado"] == "ocupado":
            info = f"Puesto {idx+1}\nOcupado por: {puesto.get('nombre')}\nRubro: {puesto.get('rubro')}\nFecha: {puesto.get('fecha')}"
        else:
            info = f"Puesto {idx+1}\nEstado: Libre"
        messagebox.showinfo("Detalle del Puesto", info)

    # -------------------------------------
    # Alquilar un puesto
    # -------------------------------------
    def alquilar_puesto(self):
        libres = [i for i, p in enumerate(self.puestos) if p["estado"] == "libre"]
        if not libres:
            messagebox.showwarning("Sin puestos", "No hay puestos libres.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Alquilar Puesto")

        ttk.Label(ventana, text="Seleccione Puesto:").grid(row=0, column=0)
        combo_puesto = ttk.Combobox(ventana, values=[f"Puesto {i+1}" for i in libres])
        combo_puesto.grid(row=0, column=1)

        ttk.Label(ventana, text="Nombre del Cliente:").grid(row=1, column=0)
        entry_nombre = ttk.Entry(ventana)
        entry_nombre.grid(row=1, column=1)

        ttk.Label(ventana, text="Rubro:").grid(row=2, column=0)
        entry_rubro = ttk.Entry(ventana)
        entry_rubro.grid(row=2, column=1)

        def confirmar():
            if not combo_puesto.get() or not entry_nombre.get() or not entry_rubro.get():
                messagebox.showerror("Error", "Complete todos los campos.")
                return

            idx = int(combo_puesto.get().split()[1]) - 1
            self.puestos[idx] = {
                "estado": "ocupado",
                "nombre": entry_nombre.get(),
                "rubro": entry_rubro.get(),
                "fecha": str(date.today())
            }
            self.guardar_datos(self.archivo_puestos, self.puestos)
            self.actualizar_colores()
            messagebox.showinfo("Éxito", "Puesto alquilado correctamente.")
            ventana.destroy()

        ttk.Button(ventana, text="Confirmar", command=confirmar).grid(row=3, column=0, columnspan=2, pady=5)

    # -------------------------------------
    # Liberar puesto
    # -------------------------------------
    def liberar_puesto(self):
        ocupados = [i for i, p in enumerate(self.puestos) if p["estado"] == "ocupado"]
        if not ocupados:
            messagebox.showinfo("Información", "No hay puestos ocupados.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Liberar Puesto")

        ttk.Label(ventana, text="Seleccione Puesto:").grid(row=0, column=0)
        combo = ttk.Combobox(ventana, values=[f"Puesto {i+1}" for i in ocupados])
        combo.grid(row=0, column=1)

        def confirmar():
            if not combo.get():
                return
            idx = int(combo.get().split()[1]) - 1
            self.puestos[idx] = {"estado": "libre"}
            self.guardar_datos(self.archivo_puestos, self.puestos)
            self.actualizar_colores()
            messagebox.showinfo("Listo", "Puesto liberado.")
            ventana.destroy()

        ttk.Button(ventana, text="Confirmar", command=confirmar).grid(row=1, column=0, columnspan=2, pady=5)

    # -------------------------------------
    # Gestionar clientes regulares
    # -------------------------------------
    def gestionar_regulares(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Clientes Regulares")

        ttk.Label(ventana, text="Nombre:").grid(row=0, column=0)
        entry_nombre = ttk.Entry(ventana)
        entry_nombre.grid(row=0, column=1)

        ttk.Label(ventana, text="Rubro:").grid(row=1, column=0)
        entry_rubro = ttk.Entry(ventana)
        entry_rubro.grid(row=1, column=1)

        def agregar():
            nombre = entry_nombre.get()
            rubro = entry_rubro.get()
            if not nombre or not rubro:
                return messagebox.showerror("Error", "Complete los campos.")
            self.clientes_regulares.append({"nombre": nombre, "rubro": rubro})
            self.guardar_datos(self.archivo_regulares, self.clientes_regulares)
            messagebox.showinfo("Agregado", "Cliente agregado correctamente.")
            entry_nombre.delete(0, tk.END)
            entry_rubro.delete(0, tk.END)
            listar_clientes()

        ttk.Button(ventana, text="Agregar", command=agregar).grid(row=2, column=0, columnspan=2, pady=5)

        frame_lista = ttk.Frame(ventana)
        frame_lista.grid(row=3, column=0, columnspan=2, pady=5)
        lista = tk.Listbox(frame_lista, width=40)
        lista.pack()

        def listar_clientes():
            lista.delete(0, tk.END)
            for c in self.clientes_regulares:
                lista.insert(tk.END, f"{c['nombre']} ({c['rubro']})")

        listar_clientes()

    # -------------------------------------
    # Actualizar colores visuales
    # -------------------------------------
    def actualizar_colores(self):
        for i, p in enumerate(self.puestos):
            self.botones_puestos[i].config(bg=self.color_estado(p["estado"]))

# -----------------------------
# Ejecución principal
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaAlquiler(root)
    root.mainloop()