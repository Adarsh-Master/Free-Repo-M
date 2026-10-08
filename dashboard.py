# NCSC Predictive IoT Framework: Live AI Dashboard (CustomTkinter Pro Edition)
# Ultra-Modern UI | Dynamic Serial Connection | Hardware Independence

import serial
import serial.tools.list_ports
import time
import customtkinter as ctk
from tkinter import messagebox
import joblib
import pandas as pd

# --- System Initialization ---
# Force a highly modern dark-green aesthetic
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

try:
    ai_model = joblib.load('spoilage_model.pkl')
    print("System Boot: AI Model loaded successfully.")
except Exception as e:
    root = ctk.CTk()
    root.withdraw()
    messagebox.showerror("Critical Error", "Model 'spoilage_model.pkl' not found.\nPlease run train_model.py first.")
    exit()

arduino = None
gas_history = []

# --- Hardware Connection Logic ---
def connect_hardware():
    global arduino
    selected_port = port_combo.get()
    
    if not selected_port or selected_port == "No Ports Found":
        hw_status_label.configure(text="Status: No Port Selected", text_color="#ff5252")
        return

    # Extract COM port name (e.g., 'COM3' from 'COM3 - Arduino Uno')
    port_name = selected_port.split(" ")[0]
    
    try:
        if arduino and arduino.is_open:
            arduino.close()
            
        hw_status_label.configure(text=f"Connecting to {port_name}...", text_color="#ffd740")
        app.update()
        
        arduino = serial.Serial(port_name, 9600, timeout=1)
        time.sleep(2) # Wait for Arduino reset
        
        hw_status_label.configure(text=f"Status: Connected ({port_name})", text_color="#69f0ae")
        connect_btn.configure(text="Reconnect")
    except Exception as e:
        hw_status_label.configure(text="Status: Connection Failed", text_color="#ff5252")
        arduino = None

def refresh_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [f"{port.device} - {port.description}" for port in ports]
    if port_list:
        port_combo.configure(values=port_list)
        port_combo.set(port_list[0])
    else:
        port_combo.configure(values=["No Ports Found"])
        port_combo.set("No Ports Found")

# --- Core AI Update Loop ---
def update_dashboard():
    global arduino, gas_history
    
    if arduino and arduino.is_open:
        try:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                
                if line.isdigit():
                    current_gas = int(line)
                    
                    # Update History & Calculate Trend
                    gas_history.append(current_gas)
                    if len(gas_history) > 8:
                        gas_history.pop(0)
                    avg_gas = sum(gas_history) / len(gas_history)
                    
                    # AI Prediction
                    live_data = pd.DataFrame({'Current_Gas': [current_gas], 'Avg_Gas': [avg_gas]})
                    risk_percentage = ai_model.predict(live_data)[0]
                    
                    # Update Metrics
                    val_live_gas.configure(text=f"{current_gas} ppm")
                    val_trend.configure(text=f"{int(avg_gas)} ppm")
                    val_risk.configure(text=f"{risk_percentage:.1f}%")
                    
                    # Update Progress Bar (CustomTkinter uses 0.0 to 1.0)
                    risk_progress.set(risk_percentage / 100.0)
                    
                    # AI Risk Assessment & Color Coding
                    if risk_percentage > 75.0:
                        sys_status_label.configure(text="SYSTEM ALERT: HIGH SPOILAGE RISK DETECTED!", text_color="#ff5252")
                        val_risk.configure(text_color="#ff5252")
                        risk_progress.configure(progress_color="#ff5252")
                    elif risk_percentage > 40.0:
                        sys_status_label.configure(text="WARNING: Early Stage Spoilage Forming", text_color="#ffd740")
                        val_risk.configure(text_color="#ffd740")
                        risk_progress.configure(progress_color="#ffd740")
                    else:
                        sys_status_label.configure(text="SYSTEM STATUS: Batch is Secure & Healthy", text_color="#69f0ae")
                        val_risk.configure(text_color="#69f0ae")
                        risk_progress.configure(progress_color="#69f0ae")
                        
        except Exception as e:
            hw_status_label.configure(text="Status: Hardware Disconnected", text_color="#ff5252")
            arduino = None

    # Loop 5 times a second
    app.after(200, update_dashboard)

# --- UI / UX Design Build ---
app = ctk.CTk()
app.title("NCSC AI Engine | Predictive IoT Framework")
app.geometry("950x650")

# --- Layout: Sidebar Navigation ---
sidebar = ctk.CTkFrame(app, width=220, corner_radius=0)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="NCSC 2026", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 5))
ctk.CTkLabel(sidebar, text="AI EDGE NODE", font=ctk.CTkFont(size=12), text_color="#69f0ae").pack(pady=(0, 30))

nav_btns = ["Live Dashboard", "Data Analytics", "Godown Logs", "System Settings"]
for btn in nav_btns:
    # Using modern flat buttons for navigation
    ctk.CTkButton(sidebar, text=btn, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", pady=5, padx=20)

# --- Layout: Main Workspace ---
workspace = ctk.CTkFrame(app, fg_color="transparent")
workspace.pack(side="right", fill="both", expand=True, padx=30, pady=30)

sys_status_label = ctk.CTkLabel(workspace, text="SYSTEM STATUS: Waiting for Hardware Stream...", font=ctk.CTkFont(size=18, weight="bold"), text_color="gray60")
sys_status_label.pack(anchor="w", pady=(0, 25))

# Metrics Grid (3 Modern Floating Boxes)
metrics_frame = ctk.CTkFrame(workspace, fg_color="transparent")
metrics_frame.pack(fill="x", pady=10)
metrics_frame.columnconfigure((0, 1, 2), weight=1)

def create_metric_box(parent, title, default_val, col):
    box = ctk.CTkFrame(parent, corner_radius=15)
    box.grid(row=0, column=col, padx=10, sticky="nsew", ipadx=20, ipady=20)
    ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray60").pack(pady=(10, 5))
    val_label = ctk.CTkLabel(box, text=default_val, font=ctk.CTkFont(size=32, weight="bold"))
    val_label.pack(pady=(0, 10))
    return val_label

val_live_gas = create_metric_box(metrics_frame, "LIVE VOC LEVEL", "-- ppm", 0)
val_trend = create_metric_box(metrics_frame, "MOVING AVERAGE", "-- ppm", 1)
val_risk = create_metric_box(metrics_frame, "AI SPOILAGE RISK", "-- %", 2)

# Analytics Progress Section
analytics_frame = ctk.CTkFrame(workspace, corner_radius=15)
analytics_frame.pack(fill="x", pady=25, ipadx=20, ipady=20)
ctk.CTkLabel(analytics_frame, text="AI Risk Analytics Prediction", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10)

risk_progress = ctk.CTkProgressBar(analytics_frame, height=15, corner_radius=8)
risk_progress.pack(fill="x", pady=15, padx=10)
risk_progress.set(0) # Start at 0

scale_frame = ctk.CTkFrame(analytics_frame, fg_color="transparent")
scale_frame.pack(fill="x", padx=10)
ctk.CTkLabel(scale_frame, text="0% (Healthy)", font=ctk.CTkFont(size=12), text_color="gray60").pack(side="left")
ctk.CTkLabel(scale_frame, text="100% (Critical)", font=ctk.CTkFont(size=12), text_color="gray60").pack(side="right")

# --- Layout: Hardware Configuration Box ---
config_frame = ctk.CTkFrame(workspace, corner_radius=15)
config_frame.pack(fill="x", pady=10, ipadx=20, ipady=15)

ctk.CTkLabel(config_frame, text="Hardware Interface (Arduino Edge Node)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(0, 10))

control_row = ctk.CTkFrame(config_frame, fg_color="transparent")
control_row.pack(fill="x", padx=10)

ctk.CTkLabel(control_row, text="COM Port:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 10))

# Modern rounded dropdown menu
port_combo = ctk.CTkOptionMenu(control_row, values=["Loading..."], width=200)
port_combo.pack(side="left", padx=10)

refresh_btn = ctk.CTkButton(control_row, text="↻ Refresh", width=80, fg_color="gray30", hover_color="gray40", command=refresh_ports)
refresh_btn.pack(side="left", padx=5)

connect_btn = ctk.CTkButton(control_row, text="CONNECT HARDWARE", command=connect_hardware, font=ctk.CTkFont(weight="bold"))
connect_btn.pack(side="left", padx=20)

hw_status_label = ctk.CTkLabel(control_row, text="Status: Offline", font=ctk.CTkFont(size=13), text_color="gray60")
hw_status_label.pack(side="right")

# Initialize
refresh_ports()
app.after(500, update_dashboard)
app.mainloop()
