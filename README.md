# WinProxyTool
It is a fast tool to switch Proxy Setting in Windows

## Quick Start
1. Install `Python`
2. Download the source `.py` file
3. Install dependence by command: `pip install pystray Pillow`
4. Run the `.py` file
5. Option: if you want to pack it to a `exe` file, you need:
   
   `pip install pyinstaller`
   
   `pyinstaller --noconsole --onefile --uac-admin --collect-all pystray --collect-all Pillow --name "Your_EXE_Name" proxy_tool.py`
