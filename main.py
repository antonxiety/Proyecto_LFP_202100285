
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def main():
    try:
        import tkinter as tk
        from ui import LigaBotUI
        root = tk.Tk()
        LigaBotUI(root)
        root.mainloop()

    except ImportError:
        
        print('[LigaBot] tkinter no encontrado. Iniciando interfaz web')
        from app_web import iniciar
        iniciar()


if __name__ == '__main__':
    main()