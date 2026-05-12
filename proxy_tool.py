import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

class ProxyTrayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("代理管理助手")
        self.root.geometry("350x250")
        self.REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        
        # 拦截关闭按钮，隐藏到托盘
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        self.proxy_var = tk.BooleanVar()
        self.setup_ui()
        
        # 初始化托盘图标（先不运行）
        self.icon = None
        self.create_tray_icon()
        
        # 初始加载设置并更新图标
        self.load_settings()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # 界面上的开关，绑定 apply_settings
        self.check_btn = ttk.Checkbutton(
            main_frame, text="启用手动代理服务器", 
            variable=self.proxy_var, command=self.apply_settings
        )
        self.check_btn.pack(pady=10, anchor="w")

        config_frame = ttk.LabelFrame(main_frame, text=" 代理配置 ", padding="10")
        config_frame.pack(fill="x", pady=10)
        
        self.entry_addr = ttk.Entry(config_frame)
        self.entry_addr.pack(side="left", fill="x", expand=True, padx=2)
        self.entry_addr.insert(0, "127.0.0.1")
        
        self.entry_port = ttk.Entry(config_frame, width=8)
        self.entry_port.pack(side="left", padx=2)
        self.entry_port.insert(0, "7890")

    def create_state_image(self, is_on):
        """根据状态生成不同的图标：开启为绿色，关闭为灰色"""
        color = "#4CAF50" if is_on else "#9E9E9E" # 绿色 vs 灰色
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0)) # 透明背景
        draw = ImageDraw.Draw(image)
        # 画一个圆角矩形或圆形作为状态标识
        draw.ellipse((4, 4, 60, 60), fill=color)
        draw.text((15, 20), "ON" if is_on else "OFF", fill="white")
        return image

    def update_tray_visuals(self):
        """同步更新托盘图标和悬停文字"""
        if self.icon:
            is_on = self.proxy_var.get()
            self.icon.icon = self.create_state_image(is_on)
            self.icon.title = f"代理状态: {'已打开' if is_on else '已关闭'}"

    def load_settings(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH)
            enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            self.proxy_var.set(bool(enabled))
            try:
                server, _ = winreg.QueryValueEx(key, "ProxyServer")
                if ":" in server:
                    addr, port = server.split(":")
                    self.entry_addr.delete(0, tk.END); self.entry_addr.insert(0, addr)
                    self.entry_port.delete(0, tk.END); self.entry_port.insert(0, port)
            except: pass
            winreg.CloseKey(key)
            self.update_tray_visuals()
        except: pass

    def apply_settings(self):
        is_enabled = 1 if self.proxy_var.get() else 0
        server_str = f"{self.entry_addr.get()}:{self.entry_port.get()}"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, is_enabled)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, server_str)
            winreg.CloseKey(key)
            self.update_tray_visuals() # 更新托盘
        except Exception as e:
            messagebox.showerror("错误", f"应用失败: {e}")

    # --- 托盘交互 ---
    def toggle_proxy_from_tray(self, icon=None, item=None):
        # 切换状态
        new_status = not self.proxy_var.get()
        self.proxy_var.set(new_status)
        self.apply_settings()

    def show_window(self):
        self.root.after(0, self.root.deiconify)

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self, icon, item):
        self.icon.stop()
        self.root.after(0, self.root.destroy)

    def create_tray_icon(self):
        menu = pystray.Menu(
            item('显示界面', self.show_window, default=True),
            item('一键开关', self.toggle_proxy_from_tray),
            item('退出程序', self.exit_app)
        )
        # 初始化图标，根据当前 proxy_var 状态生成
        self.icon = pystray.Icon("proxy_manager", self.create_state_image(self.proxy_var.get()), "代理管理", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyTrayApp(root)
    root.mainloop()