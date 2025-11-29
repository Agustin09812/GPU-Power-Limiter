[![Download Latest Release](https://img.shields.io/github/v/release/Agustin09812/GPU-Power-Limiter?label=Download%20Latest%20Release&style=for-the-badge)](https://github.com/Agustin09812/GPU-Power-Limiter/releases/latest)


---


# ⚡ GPU Power Limiter (Windows · NVIDIA)

GPU Power Limiter es una herramienta para Windows que permite modificar el **TDP (Power Limit)** de GPUs NVIDIA utilizando un **servicio en segundo plano** administrado con WinSW.  
Incluye una interfaz moderna en modo oscuro y mantiene el límite de potencia incluso después de cerrar la aplicación.

> **⚠️ Importante:** NVIDIA deshabilitó el control del TDP en drivers recientes.  
> **Esta herramienta solo funciona con drivers 527.99 o anteriores.**

---

## 🚀 Características
- Modificación del Power Limit de GPUs NVIDIA mediante `nvidia-smi`.
- Servicio de Windows persistente que aplica el TDP automáticamente.
- Instalación y desinstalación del servicio con un solo clic.
- Interfaz gráfica moderna (Tkinter · Dark Mode).
- Estados en tiempo real: **NOT_INSTALLED · INSTALLED · ACTIVE**.
- Ejecución completamente silenciosa (sin ventanas CMD).
- Logs rotativos automáticos generados por WinSW.

---

## 📦 Instalación
1. Ejecutar **GPU Power Limiter.exe**.  
2. Elegir el TDP deseado.  
3. Instalar el servicio para mantener el TDP incluso al cerrar la app.  
4. Verificar información de la GPU con el botón **“View Status”**.

---

## 🛠️ Compilación (opcional)
Si querés generar tu propio `.exe`:

pyinstaller main.py --name "GPU Power Limiter" --onefile --noconsole --icon "logo.ico" --add-data "logo.ico;." --add-data "winsw.exe;."

---

# ⚡ GPU Power Limiter (Windows · NVIDIA)

GPU Power Limiter is a Windows tool that allows you to modify the **TDP (Power Limit)** of NVIDIA GPUs by using a **background service** managed through WinSW.  
It features a modern dark-mode interface and keeps the power limit applied even after closing the application.

> **⚠️ Important:** NVIDIA disabled TDP control in newer drivers.  
> **This tool only works with driver version 527.99 or earlier.**

---

## 🚀 Features
- Modify NVIDIA GPU Power Limit using `nvidia-smi`.
- Persistent Windows service that automatically applies the selected TDP.
- One-click installation and uninstallation of the service.
- Modern graphical interface (Tkinter · Dark Mode).
- Real-time states: **NOT_INSTALLED · INSTALLED · ACTIVE**.
- Completely silent execution (no CMD windows).
- Automatic rotating logs handled by WinSW.

---

## 📦 Installation
1. Run **GPU Power Limiter.exe**.  
2. Select the desired TDP value.  
3. Install the service to keep the TDP applied even after closing the app.  
4. View GPU information using the **“View Status”** button.

---

## 🛠️ Build (optional)
If you want to generate your own `.exe`:

pyinstaller main.py --name "GPU Power Limiter" --onefile --noconsole --icon "logo.ico" --add-data "logo.ico;." --add-data "winsw.exe;."
