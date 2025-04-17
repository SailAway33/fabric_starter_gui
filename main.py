import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import threading

def run_command(command):
    try:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            return f"Error: {error.decode().strip()}"
        else:
            return output.decode().strip()
    except Exception as e:
        return str(e)

def start_command(button, port_label, command, cwd=None):
    def run_in_thread():
        print(f"[DEBUG] Start button clicked. Command: {command}, CWD: {cwd}")
        button.config(state=tk.DISABLED)
        try:
            # Open the command in a new terminal with the specified working directory
            subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', f"{command}; exec bash"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd  # Set the working directory
            )
            status = "Running in new terminal"
        except Exception as e:
            status = f"Error: {str(e)}"
        print(f"[DEBUG] Command execution completed. Status: {status}")
        button.config(state=tk.NORMAL)
        port_label.config(text=f"Status: {status}")
        
    # Run the command in a separate thread
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True  # Ensure the thread exits when the main ends
    thread.start()

def open_browser(port_label):
    port_text = port_label.cget("text")
    print(f"[DEBUG] Open Browser button clicked. Port label text: {port_text}")
    if "Port:" in port_text:
        try:
            port = int(port_text.split(": ")[1])
            print(f"[DEBUG]Opening browser http://localhost:{port}")
            webbrowser.open(f"http://localhost:{port}")
        except ValueError:
            print("[DEBUG] Invalid port number.")
            messagebox.showerror("Error", "Invalid port number.")

root = tk.Tk()
root.title("Command Runner")

# Create a frame for each row
frames = []
for i in range(6):
    frame = ttk.Frame(root, padding="10")
    frames.append(frame)
    frame.grid(row=i, column=0, sticky=(tk.W, tk.E))

labels = []
buttons_start = []
buttons_stop = []
port_labels = []

# Define commands and ports for each row
commands = [
    "fabric --serve",
    "npm run dev --prefix /home/andy/go/pkg/mod/github.com/danielmiessler/fabric@v1.4.168/web",
    "streamlit run streamlit.py",
    "go install github.com/danielmiessler/fabric@latest",
    "open-webui serve",
    "docker start heuristic_hermann"
]

ports = [
    "Port: 5000",
    "Port: 3000",
    "Port: 8501",
    "Port: latest",
    "Port: 4242",
    "Port: 8080"  # Assuming the bettercap container doesn't expose a specific port
]

for frame, command, port in zip(frames, commands, ports):
    ttk.Label(frame, text=f"Command {command}").pack(pady=5)
    
    port_label = ttk.Label(frame, text=port)
    port_labels.append(port_label)
    port_label.pack(pady=5)
    
    # Determine the working directory for specific commands
    cwd = None
    if "streamlit run streamlit.py" in command:
        cwd = "/home/andy/go/pkg/mod/github.com/danielmiessler/fabric@v1.4.168"
    
    button_start = ttk.Button(
        frame,
        text="Start",
        command=lambda cmd=command, cwd=cwd: (
            print(f"[DEBUG] Start button initialized for command: {cmd}, CWD: {cwd}"),
            start_command(button_start, port_label, cmd, cwd)
        )
    )
    buttons_start.append(button_start)
    button_start.pack(side=tk.LEFT, padx=10)
    
    button_stop = ttk.Button(
        frame,
        text="Stop",
        state=tk.DISABLED,
        command=lambda: print(f"[DEBUG] Stop button clicked for command: {command}")
    )
    buttons_stop.append(button_stop)
    button_stop.pack(side=tk.LEFT, padx=10)

# Add a "Open Browser" button at the bottom
open_browser_button = ttk.Button(
    root,
    text="Open Browser for Running Ports",
    command=lambda: (
        print("[DEBUG] Open browser button clicked."),
        open_browser(port_labels[-1])
    )
)

open_browser_button.grid(row=6, column=0, pady=20)

root.mainloop()
