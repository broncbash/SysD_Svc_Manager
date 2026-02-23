<div align="center">
  <img src="systemd-manager.png" width="96" alt="systemd-manager icon"/>
  <h1>Systemd Service Manager</h1>
  <p>A graphical GTK3 tool for managing systemd system and user services on Arch Linux.</p>

  ![Python](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white)
  ![GTK](https://img.shields.io/badge/GTK-3-blueviolet?logo=gtk)
  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?logo=arch-linux&logoColor=white)
</div>

---

## Features

- **Browse all services** — system-wide and per-user, including stopped and disabled units
- **At-a-glance status** — color-coded badges for active/inactive/failed and enabled/disabled/static/masked states
- **Full control** — Start, Stop, Restart, Enable, and Disable any service from the UI
- **Graphical sudo prompt** — system-level actions use `pkexec` (polkit) for a GUI authentication dialog; no terminal required
- **Search & filter** — filter by name, description, scope (System / User), or status (Active / Inactive / Failed)
- **Live refresh** — service state badges update immediately after each action

---

## Screenshots

> *(Add screenshots here)*

---

## Dependencies

| Package | Purpose |
|---|---|
| `python` | Runtime |
| `python-gobject` | GTK3 Python bindings |
| `gtk3` | GUI toolkit |
| `polkit` | Graphical privilege escalation (`pkexec`) |

### Optional

| Package | Purpose |
|---|---|
| `ttf-jetbrains-mono` | Preferred monospace font for the UI |
| `polkit-gnome` | Polkit agent for GNOME, i3, Sway, and other non-KDE desktops |
| `lxqt-policykit` | Polkit agent for LXQt |

---

## Installation

### Option 1 — `makepkg` (recommended)

```bash
# Clone this repository
git clone https://github.com/YOURUSERNAME/systemd-manager.git
cd systemd-manager

# Build and install
makepkg -si
```

This installs the script to `/usr/bin/systemd-manager`, registers the `.desktop` entry so it appears in your application launcher, and installs the icons into the hicolor icon theme.

### Option 2 — Manual install

```bash
git clone https://github.com/YOURUSERNAME/systemd-manager.git
cd systemd-manager

# Install dependencies
sudo pacman -S python python-gobject gtk3 polkit

# Copy files manually
sudo install -Dm755 systemd-manager.py /usr/bin/systemd-manager
sudo install -Dm644 systemd-manager.svg /usr/share/icons/hicolor/scalable/apps/systemd-manager.svg
sudo install -Dm644 systemd-manager.png /usr/share/icons/hicolor/128x128/apps/systemd-manager.png
sudo install -Dm644 systemd-manager.desktop /usr/share/applications/systemd-manager.desktop

# Refresh icon cache
sudo gtk-update-icon-cache /usr/share/icons/hicolor
```

### Option 3 — Run directly (no install)

```bash
git clone https://github.com/YOURUSERNAME/systemd-manager.git
cd systemd-manager
sudo pacman -S python python-gobject gtk3 polkit
python systemd-manager.py
```

---

## Polkit Authentication Agent

System-level service operations (start, stop, enable, disable) call `pkexec`, which requires a **polkit authentication agent** to be running in your session in order to show the graphical password prompt.

| Desktop | Agent | Notes |
|---|---|---|
| KDE Plasma | Built-in | Works automatically |
| GNOME | Built-in | Works automatically |
| i3 / Sway / Openbox / others | Manual | See below |

For tiling WMs and other minimal setups, add one of the following to your autostart:

```bash
# GNOME polkit agent (from polkit-gnome)
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &

# LXQt agent
lxqt-policykit-agent &
```

---

## Usage

Launch from your application menu (search **"Systemd"**) or run from a terminal:

```bash
systemd-manager
```

No root required to launch the application. Privilege is requested on demand only when performing system-level operations.

---

## Repository Layout

```
systemd-manager/
├── systemd-manager.py      # Main application
├── systemd-manager.svg     # Scalable icon
├── systemd-manager.png     # 128×128 raster icon (titlebar / launchers)
├── systemd-manager.desktop # Freedesktop launcher entry
├── PKGBUILD                # Arch Linux package build script
├── LICENSE
└── README.md
```

---

## License

[MIT](LICENSE) — © 2025 Your Name
