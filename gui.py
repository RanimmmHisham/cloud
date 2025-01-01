import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import subprocess
import docker
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Initialize Docker client
client = docker.from_env()


def run_function(func, *args):
    """Run a function in a separate thread to prevent GUI blocking."""
    def target():
        try:
            result = func(*args)
            if result:
                messagebox.showinfo("Result", result)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    threading.Thread(target=target).start()


# Feature 1: Create Virtual Machine
def create_vm_gui():
    vm_window = tb.Toplevel()
    vm_window.title("Create Virtual Machine")
    vm_window.geometry("500x400")
    frame = ttk.Frame(vm_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Number of CPUs:").pack(pady=5, anchor="w")
    cpu_entry = ttk.Entry(frame)
    cpu_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Memory Size (MB):").pack(pady=5, anchor="w")
    memory_entry = ttk.Entry(frame)
    memory_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Path to Disk Image:").pack(pady=5, anchor="w")
    disk_entry = ttk.Entry(frame)
    disk_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Path to Ubuntu ISO:").pack(pady=5, anchor="w")
    iso_entry = ttk.Entry(frame)
    iso_entry.pack(fill="x", pady=5)

    def submit():
        run_function(create_vm, cpu_entry.get(), memory_entry.get(), disk_entry.get(), iso_entry.get())
        vm_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=SUCCESS).pack(pady=10)


def create_vm(cpu_count, memory, disk, iso):
    """Backend logic for creating a virtual machine."""
    if not os.path.isfile(disk):
        raise Exception(f"Error: Disk image '{disk}' does not exist.")
    if not os.path.isfile(iso):
        raise Exception(f"Error: ISO file '{iso}' does not exist.")

    command = f'qemu-system-x86_64 -cpu qemu64 -smp {cpu_count} -m {memory} -hda "{disk}" -cdrom "{iso}" -boot d'
    subprocess.run(command, shell=True)


# Feature 2: Create Dockerfile
def create_dockerfile_gui():
    dockerfile_window = tb.Toplevel()
    dockerfile_window.title("Create Dockerfile")
    dockerfile_window.geometry("600x400")
    frame = ttk.Frame(dockerfile_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Path to Save Dockerfile:").pack(pady=5, anchor="w")
    path_entry = ttk.Entry(frame)
    path_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Enter Dockerfile Content (line by line):").pack(pady=5, anchor="w")
    content_text = tk.Text(frame, height=10, width=50)
    content_text.pack(fill="both", pady=5)

    def submit():
        path = path_entry.get()
        content = content_text.get("1.0", tk.END).strip().splitlines()
        if path and content:
            run_function(create_dockerfile, path, content)
            dockerfile_window.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    ttk.Button(frame, text="Submit", command=submit, bootstyle=SUCCESS).pack(pady=10)


def create_dockerfile(path, content):
    """Backend logic for creating a Dockerfile."""
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "Dockerfile"), "w") as file:
        file.write("\n".join(content))


# Feature 3: Build Docker Image
def build_docker_image_gui():
    build_window = tb.Toplevel()
    build_window.title("Build Docker Image")
    build_window.geometry("500x300")
    frame = ttk.Frame(build_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Path to Dockerfile:").pack(pady=5, anchor="w")
    path_entry = ttk.Entry(frame)
    path_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Enter Image Name:").pack(pady=5, anchor="w")
    name_entry = ttk.Entry(frame)
    name_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Enter Tag (default: latest):").pack(pady=5, anchor="w")
    tag_entry = ttk.Entry(frame)
    tag_entry.pack(fill="x", pady=5)

    def submit():
        run_function(build_docker_image, path_entry.get(), name_entry.get(), tag_entry.get())
        build_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=SUCCESS).pack(pady=10)


def build_docker_image(path, image_name, tag="latest"):
    """Backend logic for building a Docker image."""
    client.images.build(path=path, tag=f"{image_name}:{tag}")


# Feature 4: List Docker Images
def list_docker_images_gui():
    try:
        images = client.images.list() 
        if not images:
            messagebox.showinfo("Docker Images", "No Docker images found.")
        else:
            result = "\n".join([
                f"Image ID: {image.id[:12]}\nTags: {', '.join(image.tags) if image.tags else '<untagged>'}\n"
                for image in images
            ])
            messagebox.showinfo("Docker Images", result)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Feature 5: List Running Containers
def list_running_containers_gui():
    try:
        containers = client.containers.list()
        if not containers:
            messagebox.showinfo("Running Containers", "No running containers found.")
        else:
            result = "\n".join([f"{container.name}: {container.status}" for container in containers])
            messagebox.showinfo("Running Containers", result)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Feature 6: Stop a Container
def stop_container_gui():
    stop_window = tb.Toplevel()
    stop_window.title("Stop a Container")
    stop_window.geometry("500x300")
    frame = ttk.Frame(stop_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Container ID or Name:").pack(pady=5, anchor="w")
    container_entry = ttk.Entry(frame)
    container_entry.pack(fill="x", pady=5)

    def submit():
        run_function(stop_container, container_entry.get())
        stop_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=DANGER).pack(pady=10)


def stop_container(container_id):
    """Backend logic for stopping a container."""
    container = client.containers.get(container_id)
    container.stop()


# Feature 7: Search Local Image
def search_local_image_gui():
    search_window = tb.Toplevel()
    search_window.title("Search Local Image")
    search_window.geometry("500x300")
    frame = ttk.Frame(search_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Image Name/Tag to Search:").pack(pady=5, anchor="w")
    query_entry = ttk.Entry(frame)
    query_entry.pack(fill="x", pady=5)

    def submit():
        query = query_entry.get()
        if query:
            run_function(search_local_image, query)
        search_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=PRIMARY).pack(pady=10)


def search_local_image(query):
    """Backend logic for searching local Docker images."""
    images = client.images.list()
    matches = [tag for image in images if image.tags for tag in image.tags if query in tag]
    if matches:
        messagebox.showinfo("Search Results", "\n".join(matches))
    else:
        messagebox.showinfo("Search Results", f"No images found matching '{query}'.")


# Feature 8: Search DockerHub
def search_dockerhub_gui():
    search_window = tb.Toplevel()
    search_window.title("Search DockerHub")
    search_window.geometry("500x300")
    frame = ttk.Frame(search_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Image Name to Search:").pack(pady=5, anchor="w")
    query_entry = ttk.Entry(frame)
    query_entry.pack(fill="x", pady=5)

    def submit():
        query = query_entry.get()
        if query:
            run_function(search_dockerhub, query)
        search_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=PRIMARY).pack(pady=10)


def search_dockerhub(query):
    """Backend logic for searching DockerHub."""
    result = subprocess.run(f"docker search {query}", shell=True, capture_output=True, text=True)
    if result.stdout:
        messagebox.showinfo("Search Results", result.stdout)
    else:
        messagebox.showinfo("Search Results", f"No results found for '{query}'.")


# Feature 9: Download/Pull Image
def pull_image_gui():
    pull_window = tb.Toplevel()
    pull_window.title("Download/Pull Image")
    pull_window.geometry("500x300")
    frame = ttk.Frame(pull_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Image Name to Pull:").pack(pady=5, anchor="w")
    image_entry = ttk.Entry(frame)
    image_entry.pack(fill="x", pady=5)

    def submit():
        run_function(pull_image, image_entry.get())
        pull_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=SUCCESS).pack(pady=10)


def pull_image(image_name):
    """Backend logic for pulling a Docker image."""
    client.images.pull(image_name)


# Feature 10: Run a Container
def run_container_gui():
    run_window = tb.Toplevel()
    run_window.title("Run a Container")
    run_window.geometry("500x400")
    frame = ttk.Frame(run_window, padding="10")
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter Image Name:").pack(pady=5, anchor="w")
    image_entry = ttk.Entry(frame)
    image_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Enter Container Name (optional):").pack(pady=5, anchor="w")
    container_name_entry = ttk.Entry(frame)
    container_name_entry.pack(fill="x", pady=5)

    ttk.Label(frame, text="Enter Port Mappings (e.g., 8080:80):").pack(pady=5, anchor="w")
    ports_entry = ttk.Entry(frame)
    ports_entry.pack(fill="x", pady=5)

    def submit():
        run_function(run_container, image_entry.get(), container_name_entry.get(), ports_entry.get())
        run_window.destroy()

    ttk.Button(frame, text="Submit", command=submit, bootstyle=SUCCESS).pack(pady=10)


def run_container(image_name, container_name, ports):
    """Backend logic for running a container."""
    kwargs = {}
    if container_name:
        kwargs['name'] = container_name
    if ports:
        port_mapping = {ports.split(":")[1]: ports.split(":")[0]}
        kwargs['ports'] = port_mapping
    client.containers.run(image_name, detach=True, **kwargs)


# Main GUI Window
def create_main_window():
    root = tb.Window(themename="superhero")
    root.title("Cloud Management System")
    root.geometry("900x800")
    root.resizable(True, True)
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(expand=True, fill="both")

    ttk.Label(main_frame, text="Cloud Management System", font=("Helvetica", 24, "bold")).pack(pady=20)

    options = [
        ("Create Virtual Machine", create_vm_gui),
        ("Create Dockerfile", create_dockerfile_gui),
        ("Build Docker Image", build_docker_image_gui),
        ("List Docker Images", list_docker_images_gui),
        ("List Running Containers", list_running_containers_gui),
        ("Stop a Container", stop_container_gui),
        ("Search Local Image", search_local_image_gui),
        ("Search DockerHub", search_dockerhub_gui),
        ("Download/Pull Image", pull_image_gui),
        ("Run a Container", run_container_gui),
    ]

    for text, command in options:
        ttk.Button(main_frame, text=text, command=command, bootstyle=PRIMARY, width=50).pack(pady=10)

    ttk.Button(main_frame, text="Exit", command=root.quit, bootstyle=DANGER, width=50).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    create_main_window()