import paramiko
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

class SFTPClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SFTP Client")

        self.create_widgets()
        self.sftp = None
        self.transport = None

    def create_widgets(self):
        self.host_label = tk.Label(self.root, text="Host:")
        self.host_label.grid(row=0, column=0, padx=10, pady=5)
        self.host_entry = tk.Entry(self.root)
        self.host_entry.grid(row=0, column=1, padx=10, pady=5)

        self.port_label = tk.Label(self.root, text="Port:")
        self.port_label.grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.port_entry.insert(0, "22")

        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.grid(row=2, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5)

        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.grid(row=3, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file, state=tk.DISABLED)
        self.upload_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.download_button = tk.Button(self.root, text="Download File", command=self.download_file, state=tk.DISABLED)
        self.download_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.console_button = tk.Button(self.root, text="Open Console", command=self.open_console, state=tk.DISABLED)
        self.console_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.root)
        self.tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
        self.tree.heading('#0', text='Remote Directory', anchor='w')

    def connect(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.transport = paramiko.Transport((host, port))
            self.transport.connect(username=username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            messagebox.showinfo("Connection", "Connected successfully!")
            self.upload_button.config(state=tk.NORMAL)
            self.download_button.config(state=tk.NORMAL)
            self.console_button.config(state=tk.NORMAL)
            self.load_remote_directory('/')
        except Exception as e:
            messagebox.showerror("Connection", f"Failed to connect: {e}")

    def upload_file(self):
        if not self.sftp:
            messagebox.showerror("Error", "Not connected to any server.")
            return

        local_file = filedialog.askopenfilename()
        if local_file:
            remote_path = simpledialog.askstring("Remote Path", "Enter remote path:")
            if remote_path:
                try:
                    self.sftp.put(local_file, remote_path)
                    messagebox.showinfo("Upload", "File uploaded successfully!")
                    self.load_remote_directory('/')
                except Exception as e:
                    messagebox.showerror("Upload", f"Failed to upload file: {e}")

    def download_file(self):
        if not self.sftp:
            messagebox.showerror("Error", "Not connected to any server.")
            return

        remote_file = simpledialog.askstring("Remote Path", "Enter remote path:")
        if remote_file:
            local_path = filedialog.asksaveasfilename()
            if local_path:
                try:
                    self.sftp.get(remote_file, local_path)
                    messagebox.showinfo("Download", "File downloaded successfully!")
                except Exception as e:
                    messagebox.showerror("Download", f"Failed to download file: {e}")

    def open_console(self):
        if not self.transport:
            messagebox.showerror("Error", "Not connected to any server.")
            return

        console_window = tk.Toplevel(self.root)
        console_window.title("SFTP Console")

        console_text = tk.Text(console_window)
        console_text.grid(row=0, column=0, padx=10, pady=10)

        command_entry = tk.Entry(console_window)
        command_entry.grid(row=1, column=0, padx=10, pady=5)

        def execute_command():
            command = command_entry.get()
            stdin, stdout, stderr = self.transport.open_session().exec_command(command)
            console_text.insert(tk.END, f"$ {command}\n")
            console_text.insert(tk.END, stdout.read().decode() + '\n')
            console_text.insert(tk.END, stderr.read().decode() + '\n')
            command_entry.delete(0, tk.END)

        command_entry.bind("<Return>", lambda event: execute_command())
        execute_button = tk.Button(console_window, text="Execute", command=execute_command)
        execute_button.grid(row=2, column=0, pady=5)

    def load_remote_directory(self, path):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            for item in self.sftp.listdir_attr(path):
                self.tree.insert('', 'end', text=item.filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load directory: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SFTPClientApp(root)
    root.mainloop()
