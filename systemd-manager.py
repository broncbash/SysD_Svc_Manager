#!/usr/bin/env python3
"""
Systemd Service Manager - A GTK GUI for managing systemd services on Arch Linux.
Requires: python-gobject, gtk3, polkit
Install: sudo pacman -S python-gobject gtk3 polkit
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Pango, Gdk
import subprocess
import threading
import json
import os
import sys

# ── Colour tokens ────────────────────────────────────────────────────────────
# Uses system fonts only — GTK CSS does not support @import url() from the web.
# Monospace fallback chain covers JetBrains Mono (if installed), then common
# Arch system mono fonts.  Sans fallback covers most desktop installs.
CSS = b"""
* {
    font-family: 'Cantarell', 'Noto Sans', 'DejaVu Sans', sans-serif;
}

window {
    background-color: #0d1117;
    color: #e6edf3;
}

.header {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border-bottom: 1px solid #21262d;
    padding: 16px 24px;
}

.header-title {
    font-size: 22px;
    font-weight: 600;
    color: #58a6ff;
    letter-spacing: -0.5px;
}

.header-subtitle {
    font-size: 12px;
    color: #8b949e;
    margin-top: 2px;
}

.toolbar {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 8px 16px;
}

.search-entry {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    padding: 6px 12px;
    min-width: 280px;
    font-family: 'JetBrains Mono', 'Source Code Pro', 'Noto Mono', monospace;
    font-size: 13px;
}

.search-entry:focus {
    border-color: #58a6ff;
    outline: none;
}

.filter-btn {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #8b949e;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.15s;
}

.filter-btn:hover { border-color: #58a6ff; color: #58a6ff; }
.filter-btn.active { background-color: #1f3a5f; border-color: #58a6ff; color: #58a6ff; }

.service-list {
    background-color: #0d1117;
}

.service-row {
    background-color: #0d1117;
    border-bottom: 1px solid #161b22;
    padding: 0;
    transition: background-color 0.1s;
}

.service-row:hover { background-color: #161b22; }
.service-row:selected { background-color: #1f3a5f; }

.service-name {
    font-family: 'JetBrains Mono', 'Source Code Pro', 'Noto Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #e6edf3;
}

.service-desc {
    font-size: 12px;
    color: #8b949e;
    margin-top: 2px;
}

.badge {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'JetBrains Mono', 'Source Code Pro', 'Noto Mono', monospace;
    letter-spacing: 0.5px;
}

.badge-active   { background-color: #0f3d1f; color: #3fb950; border: 1px solid #238636; }
.badge-inactive { background-color: #21262d; color: #8b949e; border: 1px solid #30363d; }
.badge-failed   { background-color: #3d1010; color: #f85149; border: 1px solid #6e2020; }
.badge-enabled  { background-color: #1a2d4f; color: #58a6ff; border: 1px solid #1f4f8f; }
.badge-disabled { background-color: #21262d; color: #6e7681; border: 1px solid #30363d; }
.badge-static   { background-color: #2d2a1a; color: #e3b341; border: 1px solid #6e5708; }
.badge-masked   { background-color: #3d1010; color: #ff7b72; border: 1px solid #6e2020; }
.badge-user     { background-color: #1e2a3d; color: #79c0ff; border: 1px solid #2060a0; }
.badge-system   { background-color: #2a1e3d; color: #d2a8ff; border: 1px solid #6040a0; }

.action-btn {
    border-radius: 5px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid transparent;
    transition: all 0.15s;
    min-width: 0;
}

.btn-start  { background-color: #0f3d1f; color: #3fb950; border-color: #238636; }
.btn-start:hover  { background-color: #1a5c2e; }
.btn-stop   { background-color: #3d1010; color: #f85149; border-color: #6e2020; }
.btn-stop:hover   { background-color: #5c1818; }
.btn-enable { background-color: #1a2d4f; color: #58a6ff; border-color: #1f4f8f; }
.btn-enable:hover { background-color: #243d6b; }
.btn-disable{ background-color: #2d2a1a; color: #e3b341; border-color: #6e5708; }
.btn-disable:hover{ background-color: #453f26; }
.btn-restart{ background-color: #21262d; color: #8b949e; border-color: #30363d; }
.btn-restart:hover{ background-color: #30363d; color: #e6edf3; }

.statusbar {
    background-color: #161b22;
    border-top: 1px solid #21262d;
    padding: 6px 16px;
    font-size: 11px;
    color: #8b949e;
    font-family: 'JetBrains Mono', 'Source Code Pro', 'Noto Mono', monospace;
}

.spinner-box {
    background-color: #0d1117;
    padding: 40px;
}

.loading-label {
    color: #58a6ff;
    font-size: 14px;
    margin-top: 12px;
}

.notification {
    border-radius: 8px;
    padding: 10px 16px;
    margin: 8px;
    font-size: 12px;
    font-weight: 600;
}
.notification-success { background-color: #0f3d1f; color: #3fb950; border: 1px solid #238636; }
.notification-error   { background-color: #3d1010; color: #f85149; border: 1px solid #6e2020; }
.notification-info    { background-color: #1a2d4f; color: #58a6ff; border: 1px solid #1f4f8f; }

scrolledwindow { background-color: #0d1117; }
scrollbar { background-color: #0d1117; }
scrollbar slider { background-color: #30363d; border-radius: 4px; min-width: 6px; min-height: 6px; }
scrollbar slider:hover { background-color: #58a6ff; }
"""


def run_cmd(cmd, capture=True):
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, timeout=10)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def run_privileged(cmd_list):
    """Run a command with pkexec (graphical sudo prompt)."""
    full_cmd = ["pkexec"] + cmd_list
    try:
        r = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Authentication timed out"
    except Exception as e:
        return 1, "", str(e)


def get_services(user_mode=False):
    """Fetch list of services with name, description, load, active, sub, unit_file state."""
    flag = "--user" if user_mode else "--system"
    code, out, err = run_cmd([
        "systemctl", flag, "list-units",
        "--type=service",
        "--all",
        "--no-legend",
        "--no-pager",
        "--plain",
        "--output=json"
    ])
    services = []
    if code == 0 and out:
        try:
            data = json.loads(out)
            for item in data:
                unit = item.get("unit", "")
                desc = item.get("description", "")
                load = item.get("load", "")
                active = item.get("active", "")
                sub = item.get("sub", "")
                # Get enabled/disabled state
                ec, es, _ = run_cmd(["systemctl", flag, "is-enabled", unit])
                enabled_state = es if es else ("enabled" if ec == 0 else "disabled")
                services.append({
                    "name": unit,
                    "description": desc,
                    "load": load,
                    "active": active,
                    "sub": sub,
                    "enabled": enabled_state,
                    "mode": "user" if user_mode else "system"
                })
        except json.JSONDecodeError:
            # Fallback: parse plain text
            services = _parse_plain_services(out, flag, user_mode)
    else:
        # JSON might not be supported, try plain
        code2, out2, _ = run_cmd([
            "systemctl", flag, "list-units",
            "--type=service", "--all", "--no-legend", "--no-pager", "--plain"
        ])
        if code2 == 0 and out2:
            services = _parse_plain_services(out2, flag, user_mode)

    # Also grab unit-file list to catch disabled/static services not running
    code3, out3, _ = run_cmd([
        "systemctl", flag, "list-unit-files",
        "--type=service", "--no-legend", "--no-pager", "--plain"
    ])
    existing_names = {s["name"] for s in services}
    if code3 == 0 and out3:
        for line in out3.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                uname, ustate = parts[0], parts[1]
                if uname not in existing_names:
                    ec, es, _ = run_cmd(["systemctl", flag, "is-active", uname])
                    active = "active" if ec == 0 else "inactive"
                    ed, desc, _ = run_cmd(["systemctl", flag, "show", uname, "--property=Description", "--value"])
                    services.append({
                        "name": uname,
                        "description": desc if ed == 0 else "",
                        "load": "loaded",
                        "active": active,
                        "sub": active,
                        "enabled": ustate,
                        "mode": "user" if user_mode else "system"
                    })
    return services


def _parse_plain_services(text, flag, user_mode):
    services = []
    for line in text.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 4:
            continue
        unit, load, active, sub = parts[0], parts[1], parts[2], parts[3]
        desc = parts[4] if len(parts) > 4 else ""
        if not unit.endswith(".service"):
            continue
        ec, es, _ = run_cmd(["systemctl", flag, "is-enabled", unit])
        enabled_state = es if es else ("enabled" if ec == 0 else "disabled")
        services.append({
            "name": unit,
            "description": desc,
            "load": load,
            "active": active,
            "sub": sub,
            "enabled": enabled_state,
            "mode": "user" if user_mode else "system"
        })
    return services


class ServiceRow(Gtk.ListBoxRow):
    def __init__(self, service_data, on_action):
        super().__init__()
        self.service = service_data
        self.on_action = on_action
        self.get_style_context().add_class("service-row")
        self._build()

    def _build(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        outer.set_margin_top(10)
        outer.set_margin_bottom(10)
        outer.set_margin_start(16)
        outer.set_margin_end(16)

        # Left: name + description
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)

        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_lbl = Gtk.Label(label=self.service["name"])
        name_lbl.get_style_context().add_class("service-name")
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        name_box.pack_start(name_lbl, False, False, 0)

        # Mode badge
        mode_badge = Gtk.Label(label=self.service["mode"].upper())
        ctx = "badge-user" if self.service["mode"] == "user" else "badge-system"
        mode_badge.get_style_context().add_class("badge")
        mode_badge.get_style_context().add_class(ctx)
        name_box.pack_start(mode_badge, False, False, 0)

        info.pack_start(name_box, False, False, 0)

        desc = self.service.get("description", "") or "(no description)"
        desc_lbl = Gtk.Label(label=desc)
        desc_lbl.get_style_context().add_class("service-desc")
        desc_lbl.set_halign(Gtk.Align.START)
        desc_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        info.pack_start(desc_lbl, False, False, 0)

        outer.pack_start(info, True, True, 0)

        # Status badges
        badge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        badge_box.set_margin_end(12)
        badge_box.set_valign(Gtk.Align.CENTER)

        active_badge = Gtk.Label(label=self.service["active"].upper())
        active_style = {
            "active": "badge-active",
            "inactive": "badge-inactive",
            "failed": "badge-failed",
        }.get(self.service["active"], "badge-inactive")
        active_badge.get_style_context().add_class("badge")
        active_badge.get_style_context().add_class(active_style)
        badge_box.pack_start(active_badge, False, False, 0)

        enabled_badge = Gtk.Label(label=self.service["enabled"].upper())
        enabled_style = {
            "enabled": "badge-enabled",
            "disabled": "badge-disabled",
            "static": "badge-static",
            "masked": "badge-masked",
        }.get(self.service["enabled"], "badge-disabled")
        enabled_badge.get_style_context().add_class("badge")
        enabled_badge.get_style_context().add_class(enabled_style)
        badge_box.pack_start(enabled_badge, False, False, 0)

        outer.pack_start(badge_box, False, False, 0)

        # Action buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        btn_box.set_valign(Gtk.Align.CENTER)

        actions = [
            ("▶ Start",   "btn-start",   "start"),
            ("■ Stop",    "btn-stop",    "stop"),
            ("↺ Restart", "btn-restart", "restart"),
            ("✓ Enable",  "btn-enable",  "enable"),
            ("✗ Disable", "btn-disable", "disable"),
        ]
        for label, css_class, action in actions:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("action-btn")
            btn.get_style_context().add_class(css_class)
            svc = self.service
            btn.connect("clicked", lambda b, a=action, s=svc: self.on_action(a, s))
            btn_box.pack_start(btn, False, False, 0)

        outer.pack_start(btn_box, False, False, 0)
        self.add(outer)

    def update(self, new_data):
        self.service = new_data
        for child in self.get_children():
            self.remove(child)
        self._build()
        self.show_all()


class ServiceManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Systemd Service Manager")
        self.set_default_size(1280, 800)
        self.set_border_width(0)

        # Window icon — check installed hicolor path first, then alongside script
        _icon_candidates = [
            "/usr/share/icons/hicolor/128x128/apps/systemd-manager.png",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "systemd-manager.png"),
        ]
        for _ico in _icon_candidates:
            if os.path.exists(_ico):
                try:
                    self.set_icon_from_file(_ico)
                except Exception:
                    pass
                break
        else:
            self.set_icon_name("systemd-manager")

        # Apply CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self._filter_mode = "all"   # all | system | user
        self._filter_status = "all" # all | active | inactive | failed
        self._search_text = ""
        self._all_services = []
        self._rows = {}  # name -> ServiceRow

        self._build_ui()
        self._load_services()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.get_style_context().add_class("header")

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title = Gtk.Label(label="⚙ Systemd Service Manager")
        title.get_style_context().add_class("header-title")
        title.set_halign(Gtk.Align.START)
        subtitle = Gtk.Label(label="Manage system and user services")
        subtitle.get_style_context().add_class("header-subtitle")
        subtitle.set_halign(Gtk.Align.START)
        title_box.pack_start(title, False, False, 0)
        title_box.pack_start(subtitle, False, False, 0)
        header.pack_start(title_box, True, True, 0)

        refresh_btn = Gtk.Button(label="⟳  Refresh")
        refresh_btn.get_style_context().add_class("action-btn")
        refresh_btn.get_style_context().add_class("btn-restart")
        refresh_btn.connect("clicked", lambda _: self._load_services())
        header.pack_end(refresh_btn, False, False, 0)

        main_box.pack_start(header, False, False, 0)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.get_style_context().add_class("toolbar")
        toolbar.set_margin_top(0)

        # Search
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Filter services...")
        self.search.get_style_context().add_class("search-entry")
        self.search.connect("search-changed", self._on_search)
        toolbar.pack_start(self.search, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_start(8)
        sep.set_margin_end(8)
        toolbar.pack_start(sep, False, False, 0)

        # Mode filters
        mode_label = Gtk.Label(label="MODE:")
        mode_label.get_style_context().add_class("header-subtitle")
        toolbar.pack_start(mode_label, False, False, 0)

        self._mode_btns = {}
        for label, key in [("All", "all"), ("System", "system"), ("User", "user")]:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("filter-btn")
            if key == "all":
                btn.get_style_context().add_class("active")
            btn.connect("clicked", self._on_mode_filter, key)
            self._mode_btns[key] = btn
            toolbar.pack_start(btn, False, False, 0)

        sep2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep2.set_margin_start(8)
        sep2.set_margin_end(8)
        toolbar.pack_start(sep2, False, False, 0)

        # Status filters
        status_label = Gtk.Label(label="STATUS:")
        status_label.get_style_context().add_class("header-subtitle")
        toolbar.pack_start(status_label, False, False, 0)

        self._status_btns = {}
        for label, key in [("All", "all"), ("Active", "active"), ("Inactive", "inactive"), ("Failed", "failed")]:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("filter-btn")
            if key == "all":
                btn.get_style_context().add_class("active")
            btn.connect("clicked", self._on_status_filter, key)
            self._status_btns[key] = btn
            toolbar.pack_start(btn, False, False, 0)

        # Count label (right-aligned)
        self.count_label = Gtk.Label(label="")
        self.count_label.get_style_context().add_class("header-subtitle")
        self.count_label.set_margin_start(16)
        toolbar.pack_end(self.count_label, False, False, 0)

        main_box.pack_start(toolbar, False, False, 0)

        # Notification bar
        self.notif_bar = Gtk.Label(label="")
        self.notif_bar.set_no_show_all(True)
        self.notif_bar.set_margin_start(8)
        self.notif_bar.set_margin_end(8)
        self.notif_bar.set_margin_top(4)
        main_box.pack_start(self.notif_bar, False, False, 0)

        # Content area (spinner or list)
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        # Loading view
        spinner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        spinner_box.get_style_context().add_class("spinner-box")
        spinner_box.set_halign(Gtk.Align.CENTER)
        spinner_box.set_valign(Gtk.Align.CENTER)
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(48, 48)
        spinner_box.pack_start(self.spinner, False, False, 0)
        loading_lbl = Gtk.Label(label="Loading services...")
        loading_lbl.get_style_context().add_class("loading-label")
        spinner_box.pack_start(loading_lbl, False, False, 0)
        self.content_stack.add_named(spinner_box, "loading")

        # List view
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("service-list")
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_filter_func(self._filter_row)
        scroll.add(self.listbox)
        self.content_stack.add_named(scroll, "list")

        main_box.pack_start(self.content_stack, True, True, 0)

        # Status bar
        self.statusbar = Gtk.Label(label="Ready")
        self.statusbar.get_style_context().add_class("statusbar")
        self.statusbar.set_halign(Gtk.Align.START)
        main_box.pack_start(self.statusbar, False, False, 0)

        self.add(main_box)
        self.show_all()

    def _load_services(self):
        self.content_stack.set_visible_child_name("loading")
        self.spinner.start()
        self.statusbar.set_text("Loading services...")
        self.count_label.set_text("")

        def worker():
            system_svcs = get_services(user_mode=False)
            user_svcs = get_services(user_mode=True)
            all_svcs = system_svcs + user_svcs
            GLib.idle_add(self._populate, all_svcs)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _populate(self, services):
        self._all_services = services

        # Clear existing rows
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        self._rows = {}

        for svc in services:
            row = ServiceRow(svc, self._on_action)
            self.listbox.add(row)
            self._rows[svc["name"]] = row

        self.listbox.show_all()
        self.spinner.stop()
        self.content_stack.set_visible_child_name("list")

        n = len(services)
        active_n = sum(1 for s in services if s["active"] == "active")
        self.statusbar.set_text(f"Loaded {n} services ({active_n} active)")
        self.count_label.set_text(f"{n} services")
        return False

    def _filter_row(self, row):
        if not isinstance(row, ServiceRow):
            return True
        svc = row.service
        if self._filter_mode != "all" and svc["mode"] != self._filter_mode:
            return False
        if self._filter_status != "all" and svc["active"] != self._filter_status:
            return False
        if self._search_text:
            q = self._search_text.lower()
            if q not in svc["name"].lower() and q not in svc.get("description", "").lower():
                return False
        return True

    def _on_search(self, entry):
        self._search_text = entry.get_text()
        self.listbox.invalidate_filter()

    def _on_mode_filter(self, btn, key):
        self._filter_mode = key
        for k, b in self._mode_btns.items():
            ctx = b.get_style_context()
            if k == key:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
        self.listbox.invalidate_filter()

    def _on_status_filter(self, btn, key):
        self._filter_status = key
        for k, b in self._status_btns.items():
            ctx = b.get_style_context()
            if k == key:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
        self.listbox.invalidate_filter()

    def _on_action(self, action, service):
        name = service["name"]
        mode = service["mode"]
        flag = "--user" if mode == "user" else "--system"
        is_privileged = (mode == "system")

        self.statusbar.set_text(f"Running: systemctl {action} {name}...")

        def worker():
            cmd = ["systemctl", flag, action, name]
            if is_privileged:
                code, out, err = run_privileged(["systemctl", flag, action, name])
            else:
                code, out, err = run_cmd(cmd)
            GLib.idle_add(self._action_done, action, name, flag, mode, code, err)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _action_done(self, action, name, flag, mode, code, err):
        if code == 0 or code == 126:  # 126 = cancelled auth
            if code == 0:
                self._show_notification(f"✓ {action} {name}", "success")
                # Refresh service status
                self._refresh_service(name, flag, mode)
            else:
                self._show_notification(f"Authentication cancelled", "info")
        else:
            self._show_notification(f"✗ Failed to {action} {name}: {err[:80]}", "error")
        self.statusbar.set_text(f"Done: systemctl {action} {name}  (exit {code})")
        return False

    def _refresh_service(self, name, flag, mode):
        def worker():
            ec, active, _ = run_cmd(["systemctl", flag, "is-active", name])
            active_state = active if active else ("active" if ec == 0 else "inactive")
            ec2, enabled, _ = run_cmd(["systemctl", flag, "is-enabled", name])
            enabled_state = enabled if enabled else ("enabled" if ec2 == 0 else "disabled")
            ec3, desc, _ = run_cmd(["systemctl", flag, "show", name, "--property=Description", "--value"])
            GLib.idle_add(self._update_row, name, active_state, enabled_state, mode)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _update_row(self, name, active_state, enabled_state, mode):
        if name in self._rows:
            row = self._rows[name]
            row.service["active"] = active_state
            row.service["enabled"] = enabled_state
            row.update(row.service)
        return False

    def _show_notification(self, msg, kind="info"):
        self.notif_bar.set_text(msg)
        self.notif_bar.get_style_context().remove_class("notification-success")
        self.notif_bar.get_style_context().remove_class("notification-error")
        self.notif_bar.get_style_context().remove_class("notification-info")
        self.notif_bar.get_style_context().add_class("notification")
        self.notif_bar.get_style_context().add_class(f"notification-{kind}")
        self.notif_bar.show()

        def hide():
            self.notif_bar.hide()
            return False

        GLib.timeout_add(4000, hide)
        return False


def main():
    app = ServiceManager()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
