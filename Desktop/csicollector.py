# -*- coding: utf-8 -*-
import flet as ft
import socket
import threading
import time
import queue
import sqlite3
from datetime import datetime

# Queue for communication between network threads and the User Interface (UI).
q = queue.Queue()

# --- REUSABLE UI COMPONENTS ---

class AppCard(ft.Card):
    """A styled card component to contain other controls."""
    def __init__(self, content, **kwargs):
        super().__init__(
            content=ft.Container(
                content=content,
                padding=20,
                width=400
            ),
            elevation=4,
            **kwargs,
        )

# --- NETWORK LOGIC ---

def get_local_ip():
    """Retrieves the local IP address of the host machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually send data but connects to a remote address
        # to determine the local IP for that route.
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def send_provision_command(command, page: ft.Page):
    """Transmits the provisioning command to the ESP32's fixed IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(command.encode('utf-8'), ('192.168.4.1', 50000))
        q.put(("provision_success", None))
    except Exception as e:
        q.put(("error", f"Failed to transmit command: {e}"))
    page.update()

def udp_listener_thread(esp_ip, collection_time, local_port, stop_event):
    """
    A thread that listens for CSI packets, dispatches 'start' commands,
    and forwards the data to be saved and displayed on the UI.
    """
    q.put(("log_system", f"Initiating listener on port {local_port}..."))
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        listen_socket.bind(('', int(local_port)))
        listen_socket.settimeout(1.0)
    except Exception as e:
        q.put(("error", f"Error binding to port {local_port}: {e}"))
        q.put(("collection_finished", None))
        return

    q.put(("log_system", f"Awaiting CSI data from ESP32 node at {esp_ip}..."))
    command_send_time = 0
    first_packet_received = False
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as command_socket:
        while not stop_event.is_set():
            # Persistently send the 'start' command until the first data packet is received.
            if not first_packet_received and time.time() - command_send_time > 3: # Send every 3 seconds
                try:
                    start_message = f"start,{collection_time}"
                    command_socket.sendto(start_message.encode('utf-8'), (esp_ip, 50000))
                    q.put(("log_system", f"Command '{start_message}' dispatched to {esp_ip}"))
                    command_send_time = time.time()
                except Exception as e:
                    q.put(("log_system", f"Error sending 'start' command: {e}"))
            
            try:
                data, addr = listen_socket.recvfrom(2048) # Increased buffer size for safety
                decoded_data = data.decode('utf-8', errors='ignore').strip()
                if decoded_data.startswith("CSI_DATA"):
                    if not first_packet_received:
                        q.put(("log_system", "Initial CSI packet received. Halting 'start' command transmission."))
                        first_packet_received = True
                    
                    q.put(("log_csi", decoded_data))
                    q.put(("buffer_data", decoded_data)) # Add to the in-memory buffer

            except socket.timeout:
                continue
            except Exception as e:
                q.put(("log_system", f"Error receiving data: {e}"))
                break

    listen_socket.close()
    q.put(("collection_finished", None))


def listen_for_esp_ip_thread(stop_event):
    """Listens for broadcast packets from the ESP32 for a limited time."""
    listen_ip = "0.0.0.0"
    listen_port = 50002
    search_duration = 75
    ip_found = False

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            s.bind((listen_ip, listen_port))
            s.settimeout(1.0)
            q.put(("log_system", f"Listening on port {listen_port} for {search_duration}s..."))
        except Exception as e:
            q.put(("log_system", f"ERROR: Failed to listen for broadcast: {e}"))
            q.put(("discovery_failed", "Error initiating listener."))
            return
        
        start_time = time.time()
        while not stop_event.is_set() and time.time() - start_time < search_duration:
            try:
                data, addr = s.recvfrom(1024)
                message = data.decode('utf-8')
                if message.startswith("CSI_IP,"):
                    discovered_ip = message.split(',')[1]
                    q.put(("ip_discovered", discovered_ip))
                    ip_found = True
                    break 
            except socket.timeout:
                continue
            except Exception as e:
                q.put(("log_system", f"ERROR in discovery thread: {e}"))
    
    if not ip_found:
        q.put(("discovery_failed", "No ESP32 node discovered. Please try again."))
        
    q.put(("log_system", "Discovery thread terminated."))


# --- MAIN APPLICATION FUNCTION ---

def main(page: ft.Page):
    page.title = "CSI Data Acquisition Framework"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 800
    page.window_height = 850

    # State variables
    stop_collection_event = threading.Event()
    stop_discovery_event = threading.Event()
    network_thread = None
    discovery_thread = None
    collected_data_buffer = []
    selected_db_path = None

    # --- UI Controls ---
    prov_auth_type = ft.Dropdown(label="Authentication Protocol",options=[ft.dropdown.Option("wpa2psk", "WPA2-PSK (Personal)"),ft.dropdown.Option("peap", "WPA2-Enterprise (PEAP)")],value="wpa2psk")
    prov_ssid = ft.TextField(label="Network Name (SSID)", hint_text="e.g., MyResearchWiFi")
    prov_identity = ft.TextField(label="EAP Identity (Username)", hint_text="e.g., user@domain.com", visible=False)
    prov_password = ft.TextField(label="Network Passphrase", password=True, can_reveal_password=True)
    prov_server_ip = ft.TextField(label="Server IP Address (This Host)", value=get_local_ip())
    prov_server_port = ft.TextField(label="Server Port", value="50001")
    collect_esp_ip = ft.TextField(label="ESP32 Receiver IP Address", hint_text="Click 'Discover'", expand=True)
    collect_time = ft.TextField(label="Acquisition Duration (seconds)", value="60", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"))
    collect_port = ft.TextField(label="Listening Port (This Host)", value="50001", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"))
    
    cenario_input = ft.TextField(label="Experiment Scenario", hint_text="Describe the activity during the acquisition")
    selected_db_text = ft.Text("No database file selected.", italic=True, color="grey")

    console_output = ft.ListView(expand=True, spacing=5, auto_scroll=True)
    console_stop_button = ft.ElevatedButton("Stop Acquisition", on_click=lambda _: stop_collection(), color="white", bgcolor="red700")
    console_back_button = ft.ElevatedButton("Return", on_click=lambda _: discard_and_go_back(), visible=False)
    console_save_button = ft.ElevatedButton("Save Data", icon="save", on_click=lambda _: trigger_save_dialog(), visible=False)
    discovery_button = ft.ElevatedButton("Discover", icon="search", on_click=lambda e: start_discovery())
    discovery_progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    
    # --- Dialogs and File Logic ---
    def save_to_db(path: str, cenario: str):
        nonlocal collected_data_buffer
        try:
            with sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS csi_data (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT, scenario TEXT, type TEXT, seq INTEGER, mac TEXT, rssi INTEGER, rate REAL, 
                        sig_mode INTEGER, mcs INTEGER, bandwidth INTEGER, smoothing INTEGER, 
                        not_sounding INTEGER, aggregation INTEGER, stbc INTEGER, fec_coding INTEGER, 
                        sgi INTEGER, noise_floor INTEGER, ampdu_cnt INTEGER, channel INTEGER,
                        secondary_channel INTEGER, local_timestamp INTEGER, ant INTEGER,
                        sig_len INTEGER, rx_state INTEGER, len INTEGER, first_word INTEGER, data TEXT
                    )
                ''')
                
                processed_data = []
                timestamp_now = datetime.now().isoformat()
                for row_str in collected_data_buffer:
                    # Split only up to the data field to handle commas in the data itself
                    parts = row_str.split(',', 24) 
                    if len(parts) == 25:
                        parts[24] = parts[24].strip('"')
                        processed_data.append([timestamp_now, cenario] + parts)
                
                sql_insert_command = """
                    INSERT INTO csi_data (
                        timestamp, scenario, type, seq, mac, rssi, rate, sig_mode, mcs, bandwidth, 
                        smoothing, not_sounding, aggregation, stbc, fec_coding, sgi, noise_floor, 
                        ampdu_cnt, channel, secondary_channel, local_timestamp, ant, sig_len, 
                        rx_state, len, first_word, data
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """
                cursor.executemany(sql_insert_command, processed_data)
                conn.commit()
            page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Data successfully committed to: {path}"), open=True))
        except Exception as ex:
            show_dialog("Save Error", f"Failed to commit data to the database: {ex}")
        finally:
            collected_data_buffer.clear()
            q.put(("disable_save_button", None))

    def on_select_db_result(e: ft.FilePickerResultEvent):
        nonlocal selected_db_path
        if e.path:
            selected_db_path = e.path
            selected_db_text.value = f"Target Database: {selected_db_path}"
            selected_db_text.italic = False
            selected_db_text.color = "white"
        else:
            selected_db_path = None
            selected_db_text.value = "No database file selected."
            selected_db_text.italic = True
            selected_db_text.color = "grey"
        page.update()

    select_db_dialog = ft.FilePicker(on_result=on_select_db_result)
    page.overlay.append(select_db_dialog)
    
    # --- Control Functions ---
    def trigger_save_dialog():
        if not selected_db_path:
            show_dialog("Error", "No target database has been selected. Please return and select a file.")
            return
        save_data_to_selected_db()

    def save_data_to_selected_db():
        if not collected_data_buffer:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("No data available to save."), open=True))
            return
        
        save_to_db(selected_db_path, cenario_input.value or "N/A")

    def discard_and_go_back():
        nonlocal collected_data_buffer
        collected_data_buffer.clear()
        go_to_view('/collect')

    def go_to_view(route):
        page.go(route)
        
    def start_discovery():
        nonlocal discovery_thread
        discovery_button.disabled = True
        discovery_progress.visible = True
        collect_esp_ip.value = ""
        collect_esp_ip.hint_text = "Discovering for 75 seconds..."
        stop_discovery_event.clear()
        discovery_thread = threading.Thread(target=listen_for_esp_ip_thread,args=(stop_discovery_event,),daemon=True)
        discovery_thread.start()
        page.update()

    def on_auth_type_change(e):
        prov_identity.visible = (e.control.value == "peap")
        page.update()
    prov_auth_type.on_change = on_auth_type_change

    def submit_provision(e):
        if prov_auth_type.value == 'wpa2psk':
            command = f"wpa2psk,{prov_ssid.value},{prov_password.value},{prov_server_ip.value},{prov_server_port.value}"
        else:
            command = f"peap,{prov_ssid.value},{prov_identity.value},{prov_password.value},{prov_server_ip.value},{prov_server_port.value}"
        threading.Thread(target=send_provision_command, args=(command, page), daemon=True).start()

    def start_collection():
        nonlocal network_thread, stop_collection_event, collected_data_buffer
        
        if not selected_db_path:
            show_dialog("Warning", "Please select a database file to store the data before initiating the acquisition.")
            return

        try:
            stop_discovery_event.set()
            collected_data_buffer.clear()
            go_to_view('/console')
            stop_collection_event.clear()
            network_thread = threading.Thread(target=udp_listener_thread,args=(collect_esp_ip.value,collect_time.value,collect_port.value,stop_collection_event),daemon=True)
            network_thread.start()
        except Exception as e:
            show_dialog("Initialization Error", f"Could not start acquisition: {e}")
            go_to_view('/collect')


    def stop_collection():
        stop_collection_event.set()
        q.put(("log_system", "\n--- Acquisition terminated by user. ---"))

    def process_queue():
        needs_update = False
        new_console_items = []
        
        while not q.empty():
            try:
                message_type, data = q.get_nowait()
                needs_update = True

                if message_type == "ip_discovered":
                    if page.route == "/collect":
                        collect_esp_ip.value = data
                        collect_esp_ip.hint_text = "IP Address Discovered!"
                        discovery_progress.visible = False
                        discovery_button.disabled = False
                elif message_type == "discovery_failed":
                    if page.route == "/collect":
                        collect_esp_ip.hint_text = data if data else "No ESP32 node discovered."
                        discovery_progress.visible = False
                        discovery_button.disabled = False
                elif message_type == "log_csi":
                    new_console_items.append(ft.Text(data, font_family="monospace", size=12, selectable=True, color="white"))
                elif message_type == "log_system":
                    new_console_items.append(ft.Text(data, font_family="monospace", size=11, color="grey", selectable=True))
                elif message_type == "buffer_data":
                    collected_data_buffer.append(data)
                elif message_type == "collection_finished":
                    console_stop_button.visible = False
                    if collected_data_buffer:
                        console_save_button.visible = True
                    console_back_button.visible = True
                elif message_type == "disable_save_button":
                    console_save_button.disabled = True
                elif message_type == "provision_success":
                    show_dialog("Success", "Configuration submitted! The ESP32 node will now restart.")
                    go_to_view('/')
                elif message_type == "error":
                    show_dialog("Error", data)
            
            except queue.Empty:
                break
            except Exception as e:
                print(f"UNEXPECTED ERROR IN PROCESS_QUEUE: {e}")
        
        if new_console_items:
            console_output.controls.extend(new_console_items)
        
        if needs_update:
            page.update()

    def show_dialog(title, content):
        dlg = ft.AlertDialog(modal=True,title=ft.Text(title),content=ft.Text(content),actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(e.page, dlg))],actions_alignment=ft.MainAxisAlignment.END)
        page.dialog = dlg
        dlg.open = True
        page.update()
        
    def close_dialog(page, dlg):
        dlg.open = False
        page.update()
        
    def window_event(e):
        if e.data == "close":
            stop_discovery_event.set()
            stop_collection_event.set()
            page.window_destroy()

    page.on_window_event = window_event
    
    # --- View Definitions (Screens) ---
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(route="/",
                appbar=ft.AppBar(title=ft.Text("CSI Data Acquisition Framework"), bgcolor="surfaceVariant"),
                controls=[AppCard(content=ft.Column([ft.Text("CSI Acquisition Control", size=20, text_align=ft.TextAlign.CENTER),ft.Text("Has the ESP32 node been previously provisioned?", text_align=ft.TextAlign.CENTER),ft.ElevatedButton("Yes, Already Provisioned", on_click=lambda _: go_to_view('/collect')),ft.ElevatedButton("No, Configure Now", on_click=lambda _: go_to_view('/check_prov'), style=ft.ButtonStyle(bgcolor="white24"))],spacing=20,horizontal_alignment=ft.CrossAxisAlignment.CENTER))],vertical_alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        if page.route == "/check_prov":
            page.views.append(
                ft.View(route="/check_prov",appbar=ft.AppBar(leading=ft.IconButton(icon="arrow_back_rounded", on_click=lambda _: go_to_view('/')),title=ft.Text("Configure ESP32 Node"),bgcolor="surfaceVariant"),controls=[AppCard(ft.Column([ft.Icon(name="wifi_rounded", size=60, color="cyan"),ft.Text("Connect to the Provisioning Network", size=18, weight=ft.FontWeight.BOLD),ft.Text('Navigate to your system\'s Wi-Fi settings and connect to the "ESP_PROV" network.',text_align=ft.TextAlign.CENTER,color="grey400"),ft.ElevatedButton("I Am Connected", on_click=lambda _: go_to_view('/provision_form'))],spacing=15,horizontal_alignment=ft.CrossAxisAlignment.CENTER))],vertical_alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        if page.route == "/provision_form":
            page.views.append(
                ft.View(route="/provision_form",appbar=ft.AppBar(leading=ft.IconButton(icon="arrow_back_rounded", on_click=lambda _: go_to_view('/check_prov')),title=ft.Text("Provisioning Parameters"),bgcolor="surfaceVariant"),controls=[AppCard(ft.Column([prov_auth_type,prov_ssid,prov_identity,prov_password,prov_server_ip,prov_server_port,ft.ElevatedButton("Submit Configuration", on_click=submit_provision)]))],scroll=ft.ScrollMode.AUTO,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        if page.route == "/collect":
            page.views.append(
                ft.View(route="/collect",appbar=ft.AppBar(leading=ft.IconButton(icon="arrow_back_rounded", on_click=lambda _: go_to_view('/')),title=ft.Text("Configure Data Acquisition"),bgcolor="surfaceVariant"),controls=[AppCard(ft.Column([
                    ft.Row(controls=[collect_esp_ip, discovery_progress, discovery_button], alignment=ft.MainAxisAlignment.START),
                    collect_time,
                    collect_port,
                    ft.Divider(),
                    cenario_input,
                    ft.Row(controls=[
                        ft.ElevatedButton("Select Database", icon="folder_open", on_click=lambda _: select_db_dialog.save_file(
                            dialog_title="Select or Create a Database File",
                            file_name="csi_acquisition.db",
                            allowed_extensions=["db"]
                        )),
                        ft.Container(content=selected_db_text, expand=True, padding=ft.padding.only(left=10))
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(),

                    ft.ElevatedButton(
                        "Start Acquisition", 
                        icon="play_arrow", 
                        on_click=lambda _: start_collection()
                    )
                ]))],vertical_alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        if page.route == "/console":
            console_output.controls.clear()
            console_stop_button.visible = True
            console_save_button.visible = False
            console_save_button.disabled = False
            console_back_button.visible = False
            page.views.append(
                ft.View(
                    route="/console",
                    appbar=ft.AppBar(title=ft.Text("CSI Acquisition Console"),bgcolor="surfaceVariant", automatically_imply_leading=False),
                    controls=[
                        ft.Container(content=console_output, expand=True, bgcolor="black", border=ft.border.all(1, "white24"), border_radius=ft.border_radius.all(5), padding=10),
                        ft.Container(
                            content=ft.Row([console_stop_button, console_save_button, console_back_button], alignment=ft.MainAxisAlignment.CENTER),
                            margin=ft.margin.only(top=10)
                        )
                    ]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    
    # Main application loop to process events from the queue
    while True:
        process_queue()
        time.sleep(0.05)

if __name__ == "__main__":
    ft.app(target=main)
