import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser
import os
import sys

# Aseguramos que Python encuentre los modulos del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from lexer   import Lexer
from reportes import generar_reporte_tokens, generar_reporte_errores

# Rutas de salida de reportes
CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')
RUTA_TOKENS  = os.path.join(CARPETA_SALIDA, 'Reporte_Token.html')
RUTA_ERRORES = os.path.join(CARPETA_SALIDA, 'Reporte_Errores.html')

# Paleta de colores
COLOR_BG         = '#1a1a2e'
COLOR_PANEL      = '#16213e'
COLOR_ENTRADA    = '#0f3460'
COLOR_ACENTO     = '#e94560'
COLOR_TEXTO      = '#eaeaea'
COLOR_TEXTO_DIM  = '#8899aa'
COLOR_BOT        = '#00b4d8'
COLOR_USER       = '#90e0ef'
COLOR_ERROR      = '#ff6b6b'
COLOR_OK         = '#06d6a0'
COLOR_BTN        = '#e94560'
COLOR_BTN_HOVER  = '#c73652'
COLOR_BTN2       = '#0f3460'
COLOR_BTN2_HOVER = '#1a4a80'


class LigaBotUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._configurar_ventana()
        self._construir_ui()
        self._bienvenida()

        # Acumuladores globales de tokens y errores
        self._todos_tokens  = []
        self._todos_errores = []

    #Configuracion inicial
    def _configurar_ventana(self):
        self.root.title('LigaBot — Analizador Léxico')
        self.root.geometry('900x620')
        self.root.minsize(720, 480)
        self.root.configure(bg=COLOR_BG)
        
        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass

    #Construccion de la UI

    def _construir_ui(self):
        #Barra de tutulo 
        barra = tk.Frame(self.root, bg=COLOR_ACENTO, height=4)
        barra.pack(fill='x', side='top')

        header = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        header.pack(fill='x', padx=16)
        tk.Label(header, text='LigaBot',
                font=('Segoe UI', 16, 'bold'),
                bg=COLOR_BG, fg=COLOR_TEXTO).pack(side='left')
        tk.Label(header, text='Analizador Léxico — Fase 1',
                font=('Segoe UI', 10),
                bg=COLOR_BG, fg=COLOR_TEXTO_DIM).pack(side='left', padx=10)

        #Cuerpo principal 
        cuerpo = tk.Frame(self.root, bg=COLOR_BG)
        cuerpo.pack(fill='both', expand=True, padx=16, pady=(0, 8))

        #Area de conversacion de la izquierda
        self._area_chat = scrolledtext.ScrolledText(
            cuerpo,
            bg=COLOR_PANEL, fg=COLOR_TEXTO,
            font=('Consolas', 11),
            wrap='word',
            insertbackground=COLOR_TEXTO,
            relief='flat', bd=0,
            state='disabled',
            padx=12, pady=10,
        )
        self._area_chat.pack(side='left', fill='both', expand=True)

        # Configurar tags de color para mensajes
        self._area_chat.tag_config('bot',      foreground=COLOR_BOT,    font=('Consolas', 11, 'bold'))
        self._area_chat.tag_config('user',     foreground=COLOR_USER)
        self._area_chat.tag_config('ok',       foreground=COLOR_OK)
        self._area_chat.tag_config('error',    foreground=COLOR_ERROR)
        self._area_chat.tag_config('dim',      foreground=COLOR_TEXTO_DIM)
        self._area_chat.tag_config('separador',foreground='#334455')

        # Panel lateral derecho
        panel = tk.Frame(cuerpo, bg=COLOR_PANEL, width=180, padx=12, pady=12)
        panel.pack(side='right', fill='y', padx=(10, 0))
        panel.pack_propagate(False)

        tk.Label(panel, text='REPORTES',
                 font=('Segoe UI', 9, 'bold'),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO_DIM).pack(anchor='w', pady=(0, 8))

        self._btn(panel, 'Reporte de Tokens',  self._abrir_tokens).pack(fill='x', pady=3)
        self._btn(panel, 'Reporte de Errores', self._abrir_errores).pack(fill='x', pady=3)

        tk.Frame(panel, bg='#334455', height=1).pack(fill='x', pady=12)

        tk.Label(panel, text='LIMPIAR',
                font=('Segoe UI', 9, 'bold'),
                bg=COLOR_PANEL, fg=COLOR_TEXTO_DIM).pack(anchor='w', pady=(0, 8))

        self._btn(panel, 'Limpiar Tokens',  self._limpiar_tokens,  secundario=True).pack(fill='x', pady=3)
        self._btn(panel, 'Limpiar Errores', self._limpiar_errores, secundario=True).pack(fill='x', pady=3)
        self._btn(panel, 'Limpiar Todo',    self._limpiar_todo,    secundario=True).pack(fill='x', pady=3)

        tk.Frame(panel, bg='#334455', height=1).pack(fill='x', pady=12)

        # Contador en tiempo real
        self._lbl_tokens  = tk.Label(panel, text='Tokens: 0',
                                    font=('Segoe UI', 9), bg=COLOR_PANEL, fg=COLOR_OK)
        self._lbl_tokens.pack(anchor='w')
        self._lbl_errores = tk.Label(panel, text='Errores: 0',
                                    font=('Segoe UI', 9), bg=COLOR_PANEL, fg=COLOR_ERROR)
        self._lbl_errores.pack(anchor='w')

        #Barra de entrada
        barra_entrada = tk.Frame(self.root, bg=COLOR_ENTRADA, pady=8, padx=12)
        barra_entrada.pack(fill='x', side='bottom', padx=16, pady=(0, 12))

        self._entrada = tk.Entry(
            barra_entrada,
            bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
            font=('Consolas', 12),
            insertbackground=COLOR_TEXTO,
            relief='flat', bd=0,
        )
        self._entrada.pack(side='left', fill='both', expand=True, ipady=6)
        self._entrada.bind('<Return>', lambda e: self._analizar())
        self._entrada.focus()

        self._btn(barra_entrada, 'Analizar',
                self._analizar, width=12).pack(side='right', padx=(10, 0))

    def _btn(self, parent, texto, comando, secundario=False, width=None):
        """Crea un boton estilizado"""
        bg  = COLOR_BTN2       if secundario else COLOR_BTN
        hov = COLOR_BTN2_HOVER if secundario else COLOR_BTN_HOVER
        b = tk.Button(
            parent, text=texto,
            command=comando,
            bg=bg, fg=COLOR_TEXTO,
            font=('Segoe UI', 9),
            relief='flat', bd=0,
            cursor='hand2',
            padx=8, pady=5,
            activebackground=hov,
            activeforeground=COLOR_TEXTO,
            **(dict(width=width) if width else {}),
        )
        b.bind('<Enter>', lambda e, b=b, h=hov: b.config(bg=h))
        b.bind('<Leave>', lambda e, b=b, c=bg: b.config(bg=c))
        return b

    #Logica principal
    def _bienvenida(self):
        self._escribir('LigaBot', 'Bienvenido a LigaBot — Analizador Lexico.\n'
                       'Escribe cualquier comando y presiona Analizar', 'bot')
        self._escribir('LigaBot', 'Ejemplo: RESULTADO "Betis" VS "Rayo" TEMPORADA <1979-1980>', 'dim')
        self._separador()

    def _analizar(self):
        texto = self._entrada.get().strip()
        if not texto:
            return

        self._entrada.delete(0, 'end')
        self._escribir('Tú', texto, 'user')

        # Ejecutar el analizador lexico
        lex = Lexer(texto)
        tokens, errores = lex.analizar()

        # Acumular para reportes
        self._todos_tokens.extend(tokens)
        self._todos_errores.extend(errores)

        # Mostrar resumen en el chat
        if not errores:
            self._escribir('LigaBot',
                f'Comando aceptado {len(tokens)} token(s).', 'ok')
        else:
            self._escribir('LigaBot',
                f'Comando con errores {len(tokens)} token(s) reconocidos, '
                f'{len(errores)} error(es) lexico(s)', 'error')

        # Detalle de tokens
        for t in tokens:
            self._escribir('',
                f'   [{t.fila}:{t.columna}]  {t.tipo:<18} → "{t.lexema}"', 'dim')

        # Detalle de errores
        if errores:
            for e in errores:
                self._escribir('',
                    f'   [{e.fila}:{e.columna}]  {e.descripcion}', 'error')

        # Generar reportes HTML automaticamente
        os.makedirs(CARPETA_SALIDA, exist_ok=True)
        generar_reporte_tokens(self._todos_tokens, RUTA_TOKENS)
        generar_reporte_errores(self._todos_errores, RUTA_ERRORES)

        # Actualizar contadores del panel
        self._actualizar_contadores()
        self._separador()

    #Acciones del panel lateral

    def _abrir_tokens(self):
        if not os.path.exists(RUTA_TOKENS):
            messagebox.showinfo('LigaBot', 'Aun no se ha generado el reporte de tokens.\nAnaliza algun texto primero')
            return
        webbrowser.open(f'file://{os.path.abspath(RUTA_TOKENS)}')

    def _abrir_errores(self):
        if not os.path.exists(RUTA_ERRORES):
            messagebox.showinfo('LigaBot', 'Aun no se ha generado el reporte de errores\nAnaliza algun texto primero')
            return
        webbrowser.open(f'file://{os.path.abspath(RUTA_ERRORES)}')

    def _limpiar_tokens(self):
        self._todos_tokens.clear()
        if os.path.exists(RUTA_TOKENS):
            os.remove(RUTA_TOKENS)
        self._actualizar_contadores()
        self._escribir('LigaBot', ' Tokens limpiados.', 'dim')
        self._separador()

    def _limpiar_errores(self):
        self._todos_errores.clear()
        if os.path.exists(RUTA_ERRORES):
            os.remove(RUTA_ERRORES)
        self._actualizar_contadores()
        self._escribir('LigaBot', ' Errores limpiados.', 'dim')
        self._separador()

    def _limpiar_todo(self):
        self._limpiar_tokens()
        self._limpiar_errores()
        self._area_chat.config(state='normal')
        self._area_chat.delete('1.0', 'end')
        self._area_chat.config(state='disabled')
        self._bienvenida()

    #Utilidades de escritura 
    def _escribir(self, quien: str, texto: str, tag: str = ''):
        self._area_chat.config(state='normal')
        if quien:
            self._area_chat.insert('end', f'{quien}: ', tag or 'bot')
        self._area_chat.insert('end', f'{texto}\n', tag)
        self._area_chat.config(state='disabled')
        self._area_chat.see('end')

    def _separador(self):
        self._escribir('', '─' * 55, 'separador')

    def _actualizar_contadores(self):
        self._lbl_tokens.config(text=f'Tokens:  {len(self._todos_tokens)}')
        self._lbl_errores.config(text=f'Errores: {len(self._todos_errores)}')


def main():
    root = tk.Tk()
    LigaBotUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()