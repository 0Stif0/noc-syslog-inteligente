import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import datetime
import uuid
import requests
import hashlib

TELEGRAM_TOKEN = "8760607288:AAFvaJUSbz5JUVFZHCfjvCzpTzeL0rPyioA"
TELEGRAM_CHAT_ID = "6826219416"

COLOR_BG = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_TEXTO = "#f8fafc"
COLOR_ACCENT = "#38bdf8"
COLOR_CRITICO = "#ef4444"
COLOR_WARN = "#f59e0b"
COLOR_INFO = "#22c55e"
COLOR_AZUL = "#3b82f6"

class AppSmartNOC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart NOC Syslog - Enterprise Operations Suite v4.0 (AI & Crypto Secure)")
        self.geometry("1400x850")
        self.configure(bg=COLOR_BG)

        # Control de Acceso por Roles (RBAC) inicial
        self.rol_actual = tk.StringVar(value="Administrador") # Operador L1, Ingeniero L2, Administrador
        
        self.tickets = []
        self.blockchain_audit_trail = [] # Registro criptográfico SHA-256 de auditoría
        self.ultimo_hash = "00000000000000000000000000000000"

        self.inventario_equipos = [
            {"id": "SW-CORE-01", "ip": "192.168.1.10", "mnemonico": "LINK_DOWN", "tipo": "Switch Cisco 2960", "estado": "🟢 OPERATIVO (UP)", "syslog_asociado": "Ninguno (Estable)", "tiempo": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tag": "VERDE"},
            {"id": "RTR-BPL-02", "ip": "192.168.1.1", "mnemonico": "BGP_PEER_DOWN", "tipo": "Router Borde", "estado": "🟢 OPERATIVO (UP)", "syslog_asociado": "Ninguno (Estable)", "tiempo": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tag": "VERDE"},
            {"id": "FW-EDGE-01", "ip": "192.168.2.1", "mnemonico": "SECURITY_ALERT", "tipo": "Firewall Perimetral", "estado": "🟢 OPERATIVO (UP)", "syslog_asociado": "Ninguno (Estable)", "tiempo": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tag": "VERDE"},
            {"id": "AP-PISO2-05", "ip": "192.168.10.55", "mnemonico": "AUTH_FAIL", "tipo": "Access Point Enterprise", "estado": "🟢 OPERATIVO (UP)", "syslog_asociado": "Ninguno (Estable)", "tiempo": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tag": "VERDE"}
        ]
        
        self.plantillas_configs = {
            "Router Cisco": "enable\nconfigure terminal\nhostname RTR-CORE\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n no shutdown\nline vty 0 4\n password cisco\n login\nend",
            "Switch Cisco": "enable\nconfigure terminal\nhostname SW-ACCESS\nvlan 10\n name DATOS\ninterface range FastEthernet0/1 - 24\n switchport mode access\n switchport access vlan 10\nend",
            "Firewall": "set system hostname FW-NOC\nset system timezone America/Bogota\nset interface ethernet1/1 zone internal\nset interface ethernet1/2 zone external\ncommit",
            "Access Point": "set hostname AP-OFICINAS\nset ssid CORP-WIFI security wpa2-aes pre-shared-key Enterprise2026\nenable radio 5ghz\ncommit"
        }

        self.comandos_por_falla = {
            "Caída de Enlace (LINK_DOWN)": ["show ip interface brief", "show interfaces status", "ping 192.168.1.10"],
            "Degradación de Enlace": ["show interfaces counters error", "show controllers", "tracert 8.8.8.8"],
            "Problema de Rutas / BGP": ["show ip bgp summary", "bgp summ", "show ip route"],
            "Resolución ARP / MAC": ["show arp", "arp -a"]
        }

        self.kpi_total = 0
        self.kpi_criticos = 0
        self.kpi_automatizados = 0

        self.configurar_estilos()
        self.crear_interfaz_pestanas()
        self.registrar_auditoria_segura("SISTEMA", "ARRANQUE", "POLITICA_BASE", "ALLOW")

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_PANEL, foreground=COLOR_TEXTO, padding=[8, 5], font=("Consolas", 8, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT)], foreground=[("selected", COLOR_BG)])

    def registrar_auditoria_segura(self, event_id, evento_tipo, politica, resultado):
        """Implementa inalterabilidad criptográfica Blockchain-lite con SHA-256."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = f"{self.ultimo_hash}|{timestamp}|{event_id}|{evento_tipo}|{politica}|{resultado}"
        nuevo_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        self.ultimo_hash = nuevo_hash

        audit_line = f"[AUDIT-SHA256] | Time: {timestamp} | EID: {event_id} | Res: {resultado} | Hash: {nuevo_hash[:16]}...\n"
        self.blockchain_audit_trail.append(audit_line)
        print(audit_line)

    def crear_interfaz_pestanas(self):
        # Barra superior global de Rol (RBAC)
        frame_rbac = tk.Frame(self, bg=COLOR_PANEL, height=35)
        frame_rbac.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_rbac, text="🛡️ Control de Acceso (RBAC): Rol Activo ->", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=("Consolas", 9, "bold")).pack(side="left", padx=10)
        combo_rbac = ttk.Combobox(frame_rbac, textvariable=self.rol_actual, values=["Operador L1 (Básico)", "Ingeniero L2 (Avanzado)", "Administrador"], state="readonly", width=25, font=("Consolas", 9))
        combo_rbac.pack(side="left", padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_monitoreo = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_syslog = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_tickets = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_inventario = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_plantillas = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_ssh_trouble = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_ai_assistant = tk.Frame(self.notebook, bg=COLOR_BG) # Nueva pestaña de IA

        self.notebook.add(self.tab_monitoreo, text="🟢 Monitoreo")
        self.notebook.add(self.tab_syslog, text="📡 Syslog")
        self.notebook.add(self.tab_tickets, text="🎫 Tickets")
        self.notebook.add(self.tab_inventario, text="🖥️ Inventario")
        self.notebook.add(self.tab_plantillas, text="📝 Plantillas")
        self.notebook.add(self.tab_ssh_trouble, text="🛠️ SSH & Troubleshoot")
        self.notebook.add(self.tab_ai_assistant, text="🤖 Asistente IA & RCA")

        self.construir_pestana_monitoreo()
        self.construir_pestana_syslog()
        self.construir_pestana_tickets()
        self.construir_pestana_inventario()
        self.construir_pestana_plantillas()
        self.construir_pestana_ssh_trouble()
        self.construir_pestana_ai_assistant()

    def construir_pestana_monitoreo(self):
        lbl_title = tk.Label(self.tab_monitoreo, text="🟢 Estado de Infraestructura en Tiempo Real", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        columns = ("ID Equipo", "Dirección IP", "Mnemónico", "Estado / Tipo de Falla", "Syslog Asociado & Tiempo UP")
        self.tree_monitoreo = ttk.Treeview(self.tab_monitoreo, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree_monitoreo.heading(col, text=col)
            self.tree_monitoreo.column(col, width=220, anchor="center")
        self.tree_monitoreo.pack(fill="both", expand=True, padx=15, pady=5)

        self.tree_monitoreo.tag_configure("VERDE", foreground=COLOR_INFO)
        self.tree_monitoreo.tag_configure("NARANJA", foreground=COLOR_WARN)
        self.tree_monitoreo.tag_configure("ROJO", foreground=COLOR_CRITICO)
        self.tree_monitoreo.tag_configure("AZUL", foreground=COLOR_AZUL)
        self.actualizar_vista_monitoreo()

    def actualizar_vista_monitoreo(self):
        for row in self.tree_monitoreo.get_children():
            self.tree_monitoreo.delete(row)
        for eq in self.inventario_equipos:
            self.tree_monitoreo.insert("", "end", values=(eq["id"], eq["ip"], eq["mnemonico"], eq["estado"], eq["tiempo"]), tags=(eq["tag"],))

    def construir_pestana_syslog(self):
        frame_kpi = tk.Frame(self.tab_syslog, bg=COLOR_PANEL, bd=1, relief="solid")
        frame_kpi.pack(fill="x", padx=10, pady=10)

        self.lbl_kpi_1 = tk.Label(frame_kpi, text="📊 Total Eventos: 0", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Consolas", 10, "bold"), padx=10, pady=8)
        self.lbl_kpi_1.pack(side="left", expand=True)
        self.lbl_kpi_2 = tk.Label(frame_kpi, text="🚨 Críticos (Nivel 0-4): 0", bg=COLOR_PANEL, fg=COLOR_CRITICO, font=("Consolas", 10, "bold"), padx=10, pady=8)
        self.lbl_kpi_2.pack(side="left", expand=True)
        self.lbl_kpi_3 = tk.Label(frame_kpi, text="🤖 Automatizados (Nivel 5-7): 0", bg=COLOR_PANEL, fg=COLOR_AZUL, font=("Consolas", 10, "bold"), padx=10, pady=8)
        self.lbl_kpi_3.pack(side="left", expand=True)

        frame_controles = tk.Frame(self.tab_syslog, bg=COLOR_BG)
        frame_controles.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_controles, text="Equipo:", bg=COLOR_BG, fg=COLOR_TEXTO, font=("Consolas", 9, "bold")).pack(side="left", padx=2)
        self.combo_equipos_syslog = ttk.Combobox(frame_controles, values=[eq["id"] for eq in self.inventario_equipos], state="readonly", width=15, font=("Consolas", 9))
        self.combo_equipos_syslog.pack(side="left", padx=5)
        self.combo_equipos_syslog.current(0)

        tk.Label(frame_controles, text="Nivel:", bg=COLOR_BG, fg=COLOR_TEXTO, font=("Consolas", 9, "bold")).pack(side="left", padx=2)
        self.combo_nivel_simulacion = ttk.Combobox(frame_controles, values=[
            "0 - Emergencia (Rojo)", "1 - Alerta (Rojo)", 
            "2 - Crítico (Naranja)", "3 - Error (Naranja)", "4 - Advertencia (Naranja)", 
            "5 - Notificación (Azul)", "6 - Informativo (Azul)", "7 - Depuración (Azul)"
        ], state="readonly", width=22, font=("Consolas", 9))
        self.combo_nivel_simulacion.pack(side="left", padx=5)
        self.combo_nivel_simulacion.current(0)

        btn_simular = tk.Button(frame_controles, text="🔴 Simular", bg=COLOR_CRITICO, fg="white", font=("Consolas", 9, "bold"), command=self.simular_caida_red)
        btn_simular.pack(side="left", padx=5)

        frame_consola = tk.Frame(self.tab_syslog, bg=COLOR_PANEL)
        frame_consola.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_consola = tk.Label(frame_consola, text="Terminal Colector Syslog Centralizado con Integridad Criptográfica", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=("Consolas", 10, "bold"))
        lbl_consola.pack(anchor="w", padx=10, pady=5)

        self.txt_logs = scrolledtext.ScrolledText(frame_consola, bg="#090d16", fg=COLOR_TEXTO, font=("Consolas", 10), insertbackground="white")
        self.txt_logs.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_logs.tag_config("CRITICO", foreground=COLOR_CRITICO)
        self.txt_logs.tag_config("WARN", foreground=COLOR_WARN)
        self.txt_logs.tag_config("AZUL", foreground=COLOR_AZUL)
        self.txt_logs.tag_config("AUDIT", foreground=COLOR_ACCENT)

    def construir_pestana_tickets(self):
        lbl_title = tk.Label(self.tab_tickets, text="🎫 Historial de Incidentes, Pruebas y Causa Raíz (IA)", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        frame_principal = tk.Frame(self.tab_tickets, bg=COLOR_BG)
        frame_principal.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("TicketID", "Dispositivo", "Estado", "Fecha/Hora")
        self.tree_tickets = ttk.Treeview(frame_principal, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_tickets.heading(col, text=col)
            self.tree_tickets.column(col, width=120, anchor="center")
        self.tree_tickets.pack(side="left", fill="both", expand=False, padx=5)
        self.tree_tickets.bind("<<TreeviewSelect>>", self.mostrar_detalle_ticket)

        frame_detalle = tk.Frame(frame_principal, bg=COLOR_PANEL, bd=1, relief="solid")
        frame_detalle.pack(side="right", fill="both", expand=True, padx=5)

        tk.Label(frame_detalle, text="📜 Bitácora Forense, Pruebas y Análisis de Causa Raíz (RCA)", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=("Consolas", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        self.txt_bitacora_ticket = scrolledtext.ScrolledText(frame_detalle, bg="#090d16", fg=COLOR_TEXTO, font=("Consolas", 9), height=12)
        self.txt_bitacora_ticket.pack(fill="both", expand=True, padx=10, pady=5)

        frame_acciones = tk.Frame(self.tab_tickets, bg=COLOR_BG)
        frame_acciones.pack(fill="x", padx=15, pady=10)

        btn_resolver = tk.Button(frame_acciones, text="✅ Resolver y Cerrar Ticket (Requiere Rol Admin/Ingeniero)", bg=COLOR_INFO, fg=COLOR_BG, font=("Consolas", 9, "bold"), command=self.resolver_ticket)
        btn_resolver.pack(side="left", padx=5)

    def construir_pestana_inventario(self):
        lbl_title = tk.Label(self.tab_inventario, text="🖥️ Inventario de Infraestructura Monitoreada", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)
        columns = ("ID Dispositivo", "Tipo de Equipo", "Dirección IP", "Mnemónico Syslog Asociado")
        tree_inv = ttk.Treeview(self.tab_inventario, columns=columns, show="headings", height=12)
        for col in columns:
            tree_inv.heading(col, text=col)
            tree_inv.column(col, width=220, anchor="center")
        for eq in self.inventario_equipos:
            tree_inv.insert("", "end", values=(eq["id"], eq["tipo"], eq["ip"], eq["mnemonico"]))
        tree_inv.pack(fill="both", expand=True, padx=15, pady=5)

    def construir_pestana_plantillas(self):
        lbl_title = tk.Label(self.tab_plantillas, text="📝 Repositorio de Plantillas de Configuración de Red", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)
        frame_selector = tk.Frame(self.tab_plantillas, bg=COLOR_BG)
        frame_selector.pack(fill="x", padx=15, pady=5)
        tk.Label(frame_selector, text="Seleccione Dispositivo:", bg=COLOR_BG, fg=COLOR_TEXTO, font=("Consolas", 9)).pack(side="left", padx=5)
        self.combo_plantillas = ttk.Combobox(frame_selector, values=list(self.plantillas_configs.keys()), state="readonly", width=25)
        self.combo_plantillas.pack(side="left", padx=5)
        self.combo_plantillas.current(0)
        self.combo_plantillas.bind("<<ComboboxSelected>>", self.mostrar_plantilla)
        self.txt_plantilla_view = scrolledtext.ScrolledText(self.tab_plantillas, bg="#090d16", fg=COLOR_TEXTO, font=("Consolas", 10))
        self.txt_plantilla_view.pack(fill="both", expand=True, padx=15, pady=10)
        self.mostrar_plantilla(None)

    def mostrar_plantilla(self, event):
        tipo = self.combo_plantillas.get()
        contenido = self.plantillas_configs.get(tipo, "")
        self.txt_plantilla_view.delete("1.0", tk.END)
        self.txt_plantilla_view.insert(tk.END, contenido)

    def construir_pestana_ssh_trouble(self):
        lbl_title = tk.Label(self.tab_ssh_trouble, text="🛠️ Consola SSH & Troubleshooting Blindado (Anti-Injection)", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        frame_filtros = tk.Frame(self.tab_ssh_trouble, bg=COLOR_PANEL, bd=1, relief="solid")
        frame_filtros.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_filtros, text="Seleccionar Ticket Abierto:", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Consolas", 9, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.combo_tickets_ssh = ttk.Combobox(frame_filtros, state="readonly", width=30, font=("Consolas", 9))
        self.combo_tickets_ssh.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_filtros, text="Tipo de Falla / Diagnóstico:", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Consolas", 9, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.combo_tipo_falla = ttk.Combobox(frame_filtros, values=list(self.comandos_por_falla.keys()), state="readonly", width=30, font=("Consolas", 9))
        self.combo_tipo_falla.grid(row=1, column=1, padx=10, pady=5)
        self.combo_tipo_falla.current(0)
        self.combo_tipo_falla.bind("<<ComboboxSelected>>", self.actualizar_guia_comandos)

        self.lbl_guia_dinamica = tk.Label(frame_filtros, text="Guía recomendada: show ip interface brief | ping 192.168.1.10", bg=COLOR_PANEL, fg=COLOR_WARN, font=("Consolas", 9), padx=10, pady=5)
        self.lbl_guia_dinamica.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        frame_cmd = tk.Frame(self.tab_ssh_trouble, bg=COLOR_BG)
        frame_cmd.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_cmd, text="Comando SSH a Ejecutar:", bg=COLOR_BG, fg=COLOR_TEXTO, font=("Consolas", 10)).pack(side="left", padx=5)
        self.entry_cmd = tk.Entry(frame_cmd, width=38, font=("Consolas", 10))
        self.entry_cmd.pack(side="left", padx=5)
        self.entry_cmd.insert(0, "show ip interface brief")

        btn_ejecutar = tk.Button(frame_cmd, text="Ejecutar y Documentar", bg=COLOR_ACCENT, fg=COLOR_BG, font=("Consolas", 9, "bold"), command=self.ejecutar_troubleshooting)
        btn_ejecutar.pack(side="left", padx=5)

        self.txt_trouble_out = scrolledtext.ScrolledText(self.tab_ssh_trouble, bg="#090d16", fg=COLOR_INFO, font=("Consolas", 10))
        self.txt_trouble_out.pack(fill="both", expand=True, padx=15, pady=10)

        self.actualizar_combos_tickets()

    def construir_pestana_ai_assistant(self):
        lbl_title = tk.Label(self.tab_ai_assistant, text="🤖 Asistente Cognitivo NOC & Consultas IA en Vivo", bg=COLOR_BG, fg=COLOR_ACCENT, font=("Consolas", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        frame_chat = tk.Frame(self.tab_ai_assistant, bg=COLOR_PANEL)
        frame_chat.pack(fill="both", expand=True, padx=15, pady=5)

        self.txt_ai_chat = scrolledtext.ScrolledText(frame_chat, bg="#090d16", fg="#38bdf8", font=("Consolas", 10))
        self.txt_ai_chat.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_ai_chat.insert(tk.END, "🤖 [SmartNOC AI]: Hola operador. Pregúntame sobre el estado de la red, análisis de causa raíz (RCA) o solicita un resumen de incidentes activos.\n\n")

        frame_input = tk.Frame(self.tab_ai_assistant, bg=COLOR_BG)
        frame_input.pack(fill="x", padx=15, pady=10)

        self.entry_ai_prompt = tk.Entry(frame_input, width=65, font=("Consolas", 10))
        self.entry_ai_prompt.pack(side="left", padx=5)
        self.entry_ai_prompt.insert(0, "¿Cuál es el estado actual de los dispositivos de red?")

        btn_enviar_ai = tk.Button(frame_input, text="Preguntar al Asistente IA", bg=COLOR_AZUL, fg="white", font=("Consolas", 9, "bold"), command=self.consultar_asistente_ia)
        btn_enviar_ai.pack(side="left", padx=5)

    def actualizar_combos_tickets(self):
        tickets_abiertos = [t["ticket_id"] for t in self.tickets if "ABIERTO" in t["estado"]]
        if not tickets_abiertos:
            tickets_abiertos = ["No hay tickets abiertos"]
        self.combo_tickets_ssh['values'] = tickets_abiertos
        self.combo_tickets_ssh.current(0)

    def actualizar_guia_comandos(self, event):
        falla = self.combo_tipo_falla.get()
        cmds = self.comandos_por_falla.get(falla, [])
        self.lbl_guia_dinamica.config(text=f"Guía recomendada ({falla}): " + " | ".join(cmds))
        if cmds:
            self.entry_cmd.delete(0, tk.END)
            self.entry_cmd.insert(0, cmds[0])

    def ejecutar_troubleshooting(self):
        cmd = self.entry_cmd.get().strip()
        caracteres_prohibidos = [";", "&", "|", "`", "$", "(", ")"]
        if any(char in cmd for char in caracteres_prohibidos):
            messagebox.showerror("Error de Ciberseguridad", "¡Inyección bloqueada! El comando contiene caracteres prohibidos o maliciosos.")
            self.registrar_auditoria_segura("SEC-ALERT", "COMMAND_INJECTION_ATTEMPT", "BLOCK", "Malicious payload rejected.")
            return

        ticket_seleccionado = self.combo_tickets_ssh.get()
        tipo_falla = self.combo_tipo_falla.get()

        if not ticket_seleccionado or ticket_seleccionado == "No hay tickets abiertos":
            messagebox.showwarning("Aviso", "Seleccione un ticket abierto válido.")
            return

        if "ping" in cmd:
            output_simulado = f"> Executing ICMP: {cmd}\nReply: bytes=32 time=1ms TTL=128 [OK 0% loss]."
        elif "tracert" in cmd:
            output_simulado = f"> Trace complete.\n  1  <1 ms  192.168.1.1\n  2  2 ms  10.10.20.1"
        elif "bgp" in cmd:
            output_simulado = f"> BGP Summary: Neighbor 192.168.1.2 State/PfxRcd = 5 [ESTABLISHED]"
        elif "arp" in cmd:
            output_simulado = f"> ARP Table: 192.168.1.10 - 001b.d456.7890 [DYNAMIC]"
        else:
            output_simulado = f"> SSH Executed: '{cmd}' -> [OK] Validated securely."

        self.txt_trouble_out.delete("1.0", tk.END)
        self.txt_trouble_out.insert(tk.END, output_simulado)

        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        for t in self.tickets:
            if t["ticket_id"] == ticket_seleccionado:
                t["acciones_log"].append(f"[{hora_actual}] SSH Cmd: {cmd} -> Éxito")
                messagebox.showinfo("Auditoría", f"Comando blindado documentado en ticket {ticket_seleccionado}")
                self.mostrar_detalle_ticket_por_id(ticket_seleccionado)
                break

    def consultar_asistente_ia(self):
        prompt = self.entry_ai_prompt.get().strip().lower()
        self.txt_ai_chat.insert(tk.END, f"👤 [Operador]: {prompt}\n")
        
        # Simulación de Inteligencia Artificial Analítica (RCA)
        respuesta = ""
        if "estado" in prompt or "red" in prompt:
            activos = sum(1 for eq in self.inventario_equipos if "OPERATIVO" in eq["estado"])
            respuesta = f"🤖 [SmartNOC AI]: Analizando topología... Hay {activos} de {len(self.inventario_equipos)} dispositivos operativos estables. Revisa la pestaña de Monitoreo para detalles de alertas activas.\n\n"
        elif "causa" in prompt or "rca" in prompt or "error" in prompt:
            respuesta = "🤖 [SmartNOC AI]: Análisis de Causa Raíz (RCA): Las fallas más comunes detectadas provienen de timeouts en interfaces físicas por latencia o pérdida de adyacencia BGP. Se recomienda validar con los comandos de la pestaña SSH.\n\n"
        else:
            respuesta = f"🤖 [SmartNOC AI]: He procesado tu consulta sobre '{prompt}'. Basado en las políticas del NOC, el sistema opera bajo parámetros seguros y sin anomalías de inyección.\n\n"

        self.txt_ai_chat.insert(tk.END, respuesta)
        self.txt_ai_chat.see(tk.END)
        self.entry_ai_prompt.delete(0, tk.END)

    def simular_caida_red(self):
         equipo_seleccionado_id = self.combo_equipos_syslog.get()
         seleccion_combo = self.combo_nivel_simulacion.get()
         nivel_sev = int(seleccion_combo.split(" ")[0])

         for eq in self.inventario_equipos:
             if eq["id"] == equipo_seleccionado_id and "🔴" in eq["estado"] and nivel_sev <= 4:
                 messagebox.showwarning("NOC Policy", f"El equipo {equipo_seleccionado_id} tiene un ticket abierto. Resuélvalo antes.")
                 return

         if nivel_sev <= 1:
             estado_texto = f"🔴 CAÍDO / EMERGENCIA (Sev {nivel_sev})"
             tag_color = "ROJO"
             mnemotecnico = "CRITICAL_LINK_DOWN"
         elif nivel_sev <= 4:
             estado_texto = f"🟠 DEGRADADO / ERROR (Sev {nivel_sev})"
             tag_color = "NARANJA"
             mnemotecnico = "LINK_DEGRADED_WARN"
         else:
             estado_texto = "🔵 GESTIONADO / RUTINA"
             tag_color = "AZUL"
             mnemotecnico = "ROUTINE_SYNC"

         raw_data = f"SYS-LOG: Event from {equipo_seleccionado_id} | Severity [{nivel_sev}]"
         evento = {
             "event_id": str(uuid.uuid4())[:8].upper(),
             "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "severity": nivel_sev,
             "mnemonic": mnemotecnico,
             "message": raw_data
         }
        
         self.kpi_total += 1
         for eq in self.inventario_equipos:
             if eq["id"] == equipo_seleccionado_id:
                 eq["estado"] = estado_texto
                 eq["syslog_asociado"] = f"EID:{evento['event_id']} | {mnemotecnico}"
                 eq["tiempo"] = evento["timestamp"]
                 eq["tag"] = tag_color

         self.actualizar_vista_monitoreo()
         self.registrar_auditoria_segura(evento["event_id"], mnemotecnico, "REVIEW" if nivel_sev <= 4 else "ALLOW", "SUCCESS")

         if nivel_sev <= 4:
             self.kpi_criticos += 1
             ticket_id = self.generar_ticket(evento, equipo_seleccionado_id, "ABIERTO (Requiere Humano)")
             self.txt_logs.insert(tk.END, f"[{evento['timestamp']}] 🚨 ALERTA [{equipo_seleccionado_id}] EID:{evento['event_id']} | Ticket: {ticket_id}\n", "CRITICO")
             threading.Thread(target=self.enviar_alerta_telegram, args=(evento, ticket_id, "HUMANO")).start()
         else:
             self.kpi_automatizados += 1
             ticket_id = self.generar_ticket(evento, equipo_seleccionado_id, "RESUELTO & CERRADO (Automático)")
             self.txt_logs.insert(tk.END, f"[{evento['timestamp']}] 🔵 RUTINA [{equipo_seleccionado_id}] EID:{evento['event_id']} | Automatismo OK\n", "AZUL")
             threading.Thread(target=self.enviar_alerta_telegram, args=(evento, ticket_id, "AUTO")).start()

         self.txt_logs.see(tk.END)
         self.actualizar_kpis()
         self.actualizar_combos_tickets()

    def generar_ticket(self, evento, dispositivo_afectado, estado_inicial):
        ticket_id = f"TICK-{str(uuid.uuid4())[:6].upper()}"
        # RCA Automático generado por IA simulada
        rca_ia = f"Análisis de Causa Raíz (IA): Evento originado por {evento['mnemonic']} en {dispositivo_afectado}. Comportamiento atípico nivel {evento['severity']}."
        nuevo_ticket = {
            "ticket_id": ticket_id,
            "event_id": evento["event_id"],
            "dispositivo": dispositivo_afectado,
            "mnemonico": evento["mnemonic"],
            "estado": estado_inicial,
            "timestamp": evento["timestamp"],
            "acciones_log": [f"[{evento['timestamp']}] Alerta detectada.", rca_ia]
        }
        self.tickets.append(nuevo_ticket)
        self.actualizar_vista_tickets()
        return ticket_id

    def actualizar_vista_tickets(self):
        for row in self.tree_tickets.get_children():
            self.tree_tickets.delete(row)
        for t in self.tickets:
            self.tree_tickets.insert("", "end", values=(t["ticket_id"], t["dispositivo"], t["estado"], t["timestamp"]))

    def mostrar_detalle_ticket(self, event):
        seleccion = self.tree_tickets.selection()
        if not seleccion:
            return
        item = self.tree_tickets.item(seleccion)
        self.mostrar_detalle_ticket_por_id(item['values'][0])

    def mostrar_detalle_ticket_por_id(self, t_id):
        for t in self.tickets:
            if t["ticket_id"] == t_id:
                detalle = (f"🎫 TICKET: {t['ticket_id']} | EID: {t['event_id']}\n"
                           f"🖥️ Equipo: {t['dispositivo']} | Estado: {t['estado']}\n\n"
                           f"--- BITÁCORA Y RCA (ASISTENTE IA) ---\n")
                for log in t["acciones_log"]:
                    detalle += f" • {log}\n"
                self.txt_bitacora_ticket.delete("1.0", tk.END)
                self.txt_bitacora_ticket.insert(tk.END, detalle)
                break

    def resolver_ticket(self):
        # Validación de RBAC (Control de Acceso por Roles)
        rol = self.rol_actual.get()
        if "Operador L1" in rol:
            messagebox.showerror("Acceso Denegado (RBAC)", "El rol 'Operador L1' no tiene privilegios para cerrar tickets. Cambie a Ingeniero L2 o Administrador.")
            return

        seleccion = self.tree_tickets.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un ticket.")
            return
        item = self.tree_tickets.item(seleccion)
        t_id = item['values'][0]

        disp = ""
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        for t in self.tickets:
            if t["ticket_id"] == t_id:
                t["estado"] = "RESUELTO & CERRADO"
                t["acciones_log"].append(f"[{hora_actual}] Cerrado por Rol: {rol}")
                disp = t["dispositivo"]

        for eq in self.inventario_equipos:
            if eq["id"] in disp:
                eq["estado"] = "🟢 OPERATIVO (UP)"
                eq["syslog_asociado"] = "Ninguno (Estable)"
                eq["tiempo"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                eq["tag"] = "VERDE"

        self.actualizar_vista_monitoreo()
        self.actualizar_vista_tickets()
        self.actualizar_combos_tickets()
        messagebox.showinfo("Éxito RBAC", f"Ticket {t_id} cerrado bajo permisos de {rol}. Dispositivo liberado.")

    def enviar_alerta_telegram(self, evento, ticket_id, tipo):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        msg = f"🚨 **SMART NOC - SEGURO v4.0**\n🆔 EID: `{evento['event_id']}`\n🎫 Ticket: `{ticket_id}`\n⚠️ Evento: `{evento['mnemonic']}`"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
        except Exception:
            pass

    def actualizar_kpis(self):
        self.lbl_kpi_1.config(text=f"📊 Total: {self.kpi_total}")
        self.lbl_kpi_2.config(text=f"🚨 Críticos: {self.kpi_criticos}")
        self.lbl_kpi_3.config(text=f"🤖 Automáticos: {self.kpi_automatizados}")

if __name__ == "__main__":
    app = AppSmartNOC()
    app.mainloop()