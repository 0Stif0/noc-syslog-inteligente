import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import sqlite3
import paramiko
from datetime import datetime

# ==========================================
# 1. BASE DE DATOS Y CONFIGURACIÓN
# ==========================================
def init_db():
    conn = sqlite3.connect('network_management.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT, ip TEXT UNIQUE, sistema TEXT, estado TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT, ip TEXT, severidad INTEGER, mensaje TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT, ip TEXT, criticidad TEXT, estado TEXT, descripcion TEXT)''')
    conn.commit()
    conn.close()

SEVERIDADES = {
    0: "0 - Emergencia (Caída/Crítico)",
    1: "1 - Alerta",
    2: "2 - Crítico",
    3: "3 - Error",
    4: "4 - Advertencia",
    5: "5 - Notificación",
    6: "6 - Información",
    7: "7 - Depuración"
}

# ==========================================
# 2. SERVIDOR SYSLOG (HILO SECUNDARIO)
# ==========================================
def registrar_log(ip, severidad, mensaje):
    conn = sqlite3.connect('network_management.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, ip, severidad, mensaje) VALUES (?, ?, ?, ?)",
                   (timestamp, ip, severidad, mensaje))
    
    if severidad == 0:
        cursor.execute("INSERT INTO incidentes (timestamp, ip, criticidad, estado, descripcion) VALUES (?, ?, ?, ?, ?)",
                       (timestamp, ip, "CRÍTICA (Grado 0)", "Abierto", f"ALERTA AUTOMÁTICA: {mensaje}"))
        threading.Thread(target=lambda: messagebox.showerror(
            "¡ALERTA MÁXIMA - GRADO 0!", 
            f"Se ha detectado una caída inmediata en el equipo {ip}.\nAnalizar de inmediato.\n\nDetalle: {mensaje}"
        )).start()
        
    conn.commit()
    conn.close()

def syslog_server_loop():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 1514
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print(f"No se pudo iniciar el puerto Syslog 1514: {e}")
        return

    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode('utf-8', errors='ignore')
        severidad = 5 
        if msg.startswith("<"):
            try:
                end_idx = msg.find(">")
                pri = int(msg[1:end_idx])
                severidad = pri % 8
                msg = msg[end_idx+1:]
            except:
                pass
        registrar_log(addr[0], severidad, msg)

        # ==========================================
# 3. INTERFAZ GRÁFICA PRINCIPAL (GUI)
# ==========================================
class AppBetaRedes(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beta v1.0 - Panel de Administración de Redes")
        self.geometry("1000x650")
        
        tab_control = ttk.Notebook(self)
        self.tab_dash = ttk.Frame(tab_control)
        self.tab_inv = ttk.Frame(tab_control)
        self.tab_logs = ttk.Frame(tab_control)
        self.tab_inc = ttk.Frame(tab_control)
        self.tab_plantillas = ttk.Frame(tab_control)
        self.tab_ssh = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_dash, text='Dashboard')
        tab_control.add(self.tab_inv, text='Inventario')
        tab_control.add(self.tab_logs, text='Syslog/Eventos')
        tab_control.add(self.tab_inc, text='Incidentes')
        tab_control.add(self.tab_plantillas, text='Plantillas de Config')
        tab_control.add(self.tab_ssh, text='Consola SSH (PuTTY)')
        tab_control.pack(expand=1, fill="both")
        
        self.build_dashboard()
        self.build_inventario()
        self.build_syslog_view()
        self.build_incidentes()
        self.build_plantillas()
        self.build_ssh()
        
    def build_dashboard(self):
        lbl = tk.Label(self.tab_dash, text="Estado General de la Red", font=("Arial", 16, "bold"))
        lbl.pack(pady=10)
        btn_simular = tk.Button(self.tab_dash, text="Simular Caída de Equipo (Grado 0)", bg="red", fg="white", font=("Arial", 11, "bold"), command=self.simular_caida)
        btn_simular.pack(pady=20)
        self.lbl_resumen = tk.Label(self.tab_dash, text="Haga clic en 'Actualizar' para cargar métricas.", font=("Arial", 11))
        self.lbl_resumen.pack(pady=20)
        tk.Button(self.tab_dash, text="Actualizar Dashboard", command=self.refresh_dashboard).pack()

    def simular_caida(self):
        registrar_log("192.168.100.1", 0, "CRITICAL_FAIL: Interfaz Backbone Caída (Link Down). No responde Ping.")
        self.refresh_dashboard()

    def refresh_dashboard(self):
        conn = sqlite3.connect('network_management.db')
        c = conn.cursor()
        devs = c.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]
        logs_count = c.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        inc_count = c.execute("SELECT COUNT(*) FROM incidentes WHERE estado='Abierto'").fetchone()[0]
        conn.close()
        self.lbl_resumen.config(text=f"Dispositivos en Inventario: {devs}\n\nLogs Recibidos Totales: {logs_count}\n\nIncidentes Críticos Abiertos: {inc_count}")

    def build_inventario(self):
        frame_top = tk.Frame(self.tab_inv)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text="Nombre:").grid(row=0, column=0)
        self.ent_name = tk.Entry(frame_top)
        self.ent_name.grid(row=0, column=1, padx=5)
        tk.Label(frame_top, text="IP:").grid(row=0, column=2)
        self.ent_ip = tk.Entry(frame_top)
        self.ent_ip.grid(row=0, column=3, padx=5)
        self.cmb_so = ttk.Combobox(frame_top, values=["Cisco IOS", "Fortinet FortiOS", "Huawei VRP"])
        self.cmb_so.grid(row=0, column=5, padx=5)
        self.cmb_so.current(0)
        tk.Button(frame_top, text="Añadir Equipo", command=self.add_device).grid(row=0, column=6, padx=10)
        self.tree_inv = ttk.Treeview(self.tab_inv, columns=("ID", "Nombre", "IP", "Sistema", "Estado"), show="headings")
        for col in ("ID", "Nombre", "IP", "Sistema", "Estado"): self.tree_inv.heading(col, text=col)
        self.tree_inv.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_inventario()

    def add_device(self):
        conn = sqlite3.connect('network_management.db')
        try:
            conn.cursor().execute("INSERT INTO inventario (nombre, ip, sistema, estado) VALUES (?, ?, ?, 'Activo')", (self.ent_name.get(), self.ent_ip.get(), self.cmb_so.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Dispositivo añadido correctamente.")
        except Exception as e: messagebox.showerror("Error", f"No se pudo guardar: {e}")
        conn.close()
        self.load_inventario()

    def load_inventario(self):
        for item in self.tree_inv.get_children(): self.tree_inv.delete(item)
        conn = sqlite3.connect('network_management.db')
        for row in conn.cursor().execute("SELECT * FROM inventario").fetchall(): self.tree_inv.insert("", "end", values=row)
        conn.close()

    def build_syslog_view(self):
        tk.Button(self.tab_logs, text="Refrescar Logs Normalizados (0-7)", command=self.load_syslogs).pack(pady=5)
        self.tree_logs = ttk.Treeview(self.tab_logs, columns=("ID", "Fecha/Hora", "IP Origen", "Severidad", "Mensaje"), show="headings")
        for col in ("ID", "Fecha/Hora", "IP Origen", "Severidad", "Mensaje"):
            self.tree_logs.heading(col, text=col)
        self.tree_logs.pack(fill="both", expand=True, padx=10, pady=10)

    def load_syslogs(self):
        for item in self.tree_logs.get_children(): self.tree_logs.delete(item)
        conn = sqlite3.connect('network_management.db')
        for row in conn.cursor().execute("SELECT * FROM logs ORDER BY id DESC").fetchall():
            sev_text = SEVERIDADES.get(row[3], f"{row[3]} - Desconocida")
            self.tree_logs.insert("", "end", values=(row[0], row[1], row[2], sev_text, row[4]))
        conn.close()

    def build_incidentes(self):
        tk.Button(self.tab_inc, text="Actualizar Incidentes Abiertos", command=self.load_incidentes).pack(pady=5)
        self.tree_inc = ttk.Treeview(self.tab_inc, columns=("ID", "Fecha", "IP", "Criticidad", "Estado", "Descripción"), show="headings")
        for col in ("ID", "Fecha", "IP", "Criticidad", "Estado", "Descripción"): self.tree_inc.heading(col, text=col)
        self.tree_inc.pack(fill="both", expand=True, padx=10, pady=10)

    def load_incidentes(self):
        for item in self.tree_inc.get_children(): self.tree_inc.delete(item)
        conn = sqlite3.connect('network_management.db')
        for row in conn.cursor().execute("SELECT * FROM incidentes ORDER BY id DESC").fetchall(): self.tree_inc.insert("", "end", values=row)
        conn.close()

    def build_plantillas(self):
        frame_p = tk.Frame(self.tab_plantillas)
        frame_p.pack(side="left", fill="y", padx=10, pady=10)
        tk.Label(frame_p, text="Seleccione Vendor:", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Button(frame_p, text="Cisco IOS / IOS XE", width=20, command=lambda: self.ver_plantilla("cisco")).pack(pady=5)
        tk.Button(frame_p, text="Fortinet FortiOS", width=20, command=lambda: self.ver_plantilla("fortinet")).pack(pady=5)
        tk.Button(frame_p, text="Huawei VRP", width=20, command=lambda: self.ver_plantilla("huawei")).pack(pady=5)
        self.txt_plantilla = scrolledtext.ScrolledText(self.tab_plantillas, width=70, height=30)
        self.txt_plantilla.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def ver_plantilla(self, vendor):
        self.txt_plantilla.delete('1.0', tk.END)
        if vendor == "cisco": text = "! === PLANTILLA CISCO IOS ===\nhostname RUTA-CISCO-BETA\nlogging host 192.168.1.50\nlogging trap 6\n"
        elif vendor == "fortinet": text = "# === PLANTILLA FORTINET FORTIOS ===\nconfig log syslogd setting\nset status enable\nset server \"192.168.1.50\"\nend\n"
        else: text = "* === PLANTILLA HUAWEI VRP ===\ninfo-center enable\ninfo-center loghost 192.168.1.50\n"
        self.txt_plantilla.insert(tk.END, text)

    def build_ssh(self):
        frame_ssh = tk.Frame(self.tab_ssh)
        frame_ssh.pack(pady=5)
        tk.Label(frame_ssh, text="Host IP:").grid(row=0, column=0)
        self.ent_ssh_host = tk.Entry(frame_ssh, width=15)
        self.ent_ssh_host.grid(row=0, column=1, padx=5)
        tk.Label(frame_ssh, text="User:").grid(row=0, column=2)
        self.ent_ssh_user = tk.Entry(frame_ssh, width=12)
        self.ent_ssh_user.grid(row=0, column=3, padx=5)
        tk.Label(frame_ssh, text="Pass:").grid(row=0, column=4)
        self.ent_ssh_pass = tk.Entry(frame_ssh, width=12, show="*")
        self.ent_ssh_pass.grid(row=0, column=5, padx=5)
        tk.Button(frame_ssh, text="Conectar SSH (Seguro)", command=self.ejecutar_ssh).grid(row=0, column=6, padx=5)
        self.txt_ssh_output = scrolledtext.ScrolledText(self.tab_ssh, height=25, bg="black", fg="lightgreen", font=("Consolas", 10))
        self.txt_ssh_output.pack(fill="both", expand=True, padx=10, pady=10)

    def ejecutar_ssh(self):
        host, user, passwd = self.ent_ssh_host.get(), self.ent_ssh_user.get(), self.ent_ssh_pass.get()
        if not host or not user or not passwd: return
        self.txt_ssh_output.insert(tk.END, f"\n--- Conectando de manera segura a {host}... ---\n")
        def ssh_thread():
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(hostname=host, username=user, password=passwd, timeout=5)
                stdin, stdout, stderr = client.exec_command("show version || get system status")
                self.txt_ssh_output.insert(tk.END, stdout.read().decode('utf-8', errors='ignore'))
            except Exception as e: self.txt_ssh_output.insert(tk.END, f"\n[ERROR]: {e}\n")
            finally: client.close()
        threading.Thread(target=ssh_thread).start()
        # ==========================================
# 4. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    init_db()
    threading.Thread(target=syslog_server_loop, daemon=True).start()
    AppBetaRedes().mainloop()
