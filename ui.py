import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser, os, sys

sys.path.insert(0, os.path.dirname(__file__))

from lexer            import Lexer
from parser           import Parser
from csv_reader       import LigaBotCSV
from reportes         import generar_reporte_tokens, generar_reporte_errores
from reportes_fase2   import (generar_reporte_errores_sintacticos,
generar_reporte_jornada,generar_reporte_tabla,generar_reporte_partidos)

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')
RUTA_TOKENS    = os.path.join(CARPETA_SALIDA, 'Reporte_Token.html')
RUTA_ERRORES   = os.path.join(CARPETA_SALIDA, 'Reporte_Errores.html')
RUTA_ERR_SIN   = os.path.join(CARPETA_SALIDA, 'Reporte_Errores_S.html')
RUTA_CSV       = os.path.join(os.path.dirname(__file__), 'LaLigaBot-LFP.csv')

# Colores
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
# Carga el CSV al iniciar
        self.db = LigaBotCSV(RUTA_CSV)
        self._todos_tokens  = []
        self._todos_errores = []
        self._todos_err_sin = []
        self._configurar_ventana()
        self._construir_ui()
        self._bienvenida()

# Configuracion de la ventana
    def _configurar_ventana(self):
        self.root.title('LigaBot — Fase 1')
        self.root.geometry('960x660')
        self.root.minsize(720, 480)
        self.root.configure(bg=COLOR_BG)

#Construccion de la UI

    def _construir_ui(self):
        # Barra superior
        tk.Frame(self.root, bg=COLOR_ACENTO, height=4).pack(fill='x')
        header = tk.Frame(self.root, bg=COLOR_BG, pady=8)
        header.pack(fill='x', padx=16)
        tk.Label(header, text='LigaBot', font=('Segoe UI',15,'bold'),
                bg=COLOR_BG, fg=COLOR_TEXTO).pack(side='left')
        estado_csv = 'CSV cargado' if self.db.cargado else 'CSV no encontrado'
        color_csv  = COLOR_OK if self.db.cargado else COLOR_ERROR
        tk.Label(header, text=estado_csv, font=('Segoe UI', 9),
                bg=COLOR_BG, fg=color_csv).pack(side='left', padx=14)

#Cuerpo
        cuerpo = tk.Frame(self.root, bg=COLOR_BG)
        cuerpo.pack(fill='both', expand=True, padx=16, pady=(0,8))

#area de chat
        self._chat = scrolledtext.ScrolledText(
            cuerpo, bg=COLOR_PANEL, fg=COLOR_TEXTO,
            font=('Consolas',11), wrap='word',
            insertbackground=COLOR_TEXTO, relief='flat', bd=0,
            state='disabled', padx=12, pady=10)
        self._chat.pack(side='left', fill='both', expand=True)

        for tag, fg, bold in [
            ('bot',   COLOR_BOT,       True),
            ('user',  COLOR_USER,      False),
            ('ok',    COLOR_OK,        False),
            ('error', COLOR_ERROR,     False),
            ('dim',   COLOR_TEXTO_DIM, False),
            ('sep',   '#334455',       False),
        ]:
            font = ('Consolas', 11, 'bold') if bold else ('Consolas', 11)
            self._chat.tag_config(tag, foreground=fg, font=font)

#Panel lateral
        panel = tk.Frame(cuerpo, bg=COLOR_PANEL, width=185, padx=12, pady=12)
        panel.pack(side='right', fill='y', padx=(10,0))
        panel.pack_propagate(False)

        def label_sec(txt):
            tk.Label(panel, text=txt, font=('Segoe UI',9,'bold'),
                    bg=COLOR_PANEL, fg=COLOR_TEXTO_DIM).pack(anchor='w', pady=(8,4))

        label_sec('REPORTES')
        self._btn(panel, 'Tokens',           self._abrir_tokens).pack(fill='x', pady=2)
        self._btn(panel, 'Errores Lexicos', self._abrir_errores).pack(fill='x', pady=2)
        self._btn(panel, 'Errores Sintacticos', self._abrir_err_sin).pack(fill='x', pady=2)

        tk.Frame(panel, bg='#334455', height=1).pack(fill='x', pady=8)

        label_sec('LIMPIAR')
        self._btn(panel, 'Tokens',  self._limpiar_tokens,  True).pack(fill='x', pady=2)
        self._btn(panel, 'Errores', self._limpiar_errores, True).pack(fill='x', pady=2)
        self._btn(panel, 'Todo',    self._limpiar_todo,    True).pack(fill='x', pady=2)

        tk.Frame(panel, bg='#334455', height=1).pack(fill='x', pady=8)

        self._lbl_t = tk.Label(panel, text='Tokens:  0',
                            font=('Segoe UI',9), bg=COLOR_PANEL, fg=COLOR_OK)
        self._lbl_t.pack(anchor='w')
        self._lbl_e = tk.Label(panel, text='Errores: 0',
                            font=('Segoe UI',9), bg=COLOR_PANEL, fg=COLOR_ERROR)
        self._lbl_e.pack(anchor='w')
        
#Barra de entrada
        barra = tk.Frame(self.root, bg=COLOR_ENTRADA, pady=8, padx=12)
        barra.pack(fill='x', side='bottom', padx=16, pady=(0,12))
        self._entrada = tk.Entry(barra, bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                font=('Consolas',12), insertbackground=COLOR_TEXTO,
                                relief='flat', bd=0)
        self._entrada.pack(side='left', fill='both', expand=True, ipady=6)
        self._entrada.bind('<Return>', lambda e: self._analizar())
        self._entrada.focus()
        self._btn(barra, 'Enviar', self._analizar, width=10).pack(side='right', padx=(10,0))

    def _btn(self, parent, texto, cmd, sec=False, width=None):
        bg  = COLOR_BTN2       if sec else COLOR_BTN
        hov = COLOR_BTN2_HOVER if sec else COLOR_BTN_HOVER
        b = tk.Button(parent, text=texto, command=cmd,
                    bg=bg, fg=COLOR_TEXTO, font=('Segoe UI',9),
                    relief='flat', bd=0, cursor='hand2',
                    padx=8, pady=5,
                    activebackground=hov, activeforeground=COLOR_TEXTO,
                      **(dict(width=width) if width else {}))
        b.bind('<Enter>', lambda e, b=b: b.config(bg=hov))
        b.bind('<Leave>', lambda e, b=b: b.config(bg=bg))
        return b
#Inicio

    def _bienvenida(self):
        self._escribir('LigaBot', 'Bienvenido a LigaBot, Ingrese un comando por favor', 'bot')
        if not self.db.cargado:
            self._escribir('LigaBot', 'No se encontro LaLigaBot-LFP.csv en la carpeta del proyecto', 'error')
        else:
            self._escribir('LigaBot', f'CSV cargado: {len(self.db.datos)} partidos disponibles', 'ok')
        self._escribir('LigaBot', 'Ejemplo: RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA <1979-1980>', 'dim')
        self._sep()
        
#Logica

    def _analizar(self):
        texto = self._entrada.get().strip()
        if not texto:
            return
        self._entrada.delete(0, 'end')
        self._escribir('Tú', texto, 'user')

#Analisis lexico
        lex = Lexer(texto)
        tokens, err_lex = lex.analizar()
        self._todos_tokens.extend(tokens)
        self._todos_errores.extend(err_lex)

        if err_lex:
            for e in err_lex:
                self._escribir('', f'Error lexico [{e.fila}:{e.columna}]: {e.descripcion}', 'error')

#Analisis sintactico
        p = Parser(tokens)
        comando, err_sin = p.analizar()
        self._todos_err_sin.extend(err_sin)

        if err_sin:
            for e in err_sin:
                self._escribir('', f'Error sintactico [{e.linea}:{e.columna}]: {e.descripcion}', 'error')

#Ejecutar comando si es valido
        if comando and not err_sin:
            self._ejecutar(comando)

#Generaciopn de reportes
        os.makedirs(CARPETA_SALIDA, exist_ok=True)
        generar_reporte_tokens(self._todos_tokens, RUTA_TOKENS)
        generar_reporte_errores(self._todos_errores, RUTA_ERRORES)
        generar_reporte_errores_sintacticos(self._todos_err_sin, RUTA_ERR_SIN)
        self._actualizar_contadores()
        self._sep()

    def _ejecutar(self, cmd: dict):
        """Ejecuta el comando y muestra la respuesta del chatbot"""
        tipo = cmd.get('tipo')

        if tipo == 'ADIOS':
            self._escribir('LigaBot', 'ADIOS', 'bot')
            self.root.after(1500, self.root.quit)

        elif tipo == 'RESULTADO':
            r = self.db.resultado(cmd['local'], cmd['visitante'], cmd['temporada'])
            if r['encontrado']:
                self._escribir('LigaBot',
                    f'El resultado fue: {r["local"]} {r["goles_local"]} - '
                    f'{r["goles_visitante"]} {r["visitante"]}', 'ok')
            else:
                self._escribir('LigaBot',
                    f'No se encontró el partido {cmd["local"]} vs {cmd["visitante"]} '
                    f'en la temporada {cmd["temporada"]}.', 'error')

        elif tipo == 'GOLES':
            sub  = cmd['subtipo']
            temp = cmd['temporada']
            eq   = cmd['equipo']
            if sub == 'LOCAL':
                r = self.db.goles_local(eq, temp)
                msg = f'Los goles anotados por {eq} en local en la temporada {temp} fueron {r["total"]}'
            elif sub == 'VISITANTE':
                r = self.db.goles_visitante(eq, temp)
                msg = f'Los goles anotados por {eq} en visitante en la temporada {temp} fueron {r["total"]}'
            else:
                r = self.db.goles_total(eq, temp)
                msg = f'Los goles anotados por {eq} en total en la temporada {temp} fueron {r["total"]}'
            if r['encontrado']:
                self._escribir('LigaBot', msg, 'ok')
            else:
                self._escribir('LigaBot', f'No se encontro al equipo "{eq}" en la temporada {temp}', 'error')

        elif tipo == 'TOP':
            superior = (cmd['subtipo'] == 'SUPERIOR')
            equipos  = self.db.top(cmd['temporada'], cmd['cantidad'], superior)
            tipo_str = 'superior' if superior else 'inferior'
            if equipos:
                self._escribir('LigaBot',
                    f'El top {tipo_str} de la temporada {cmd["temporada"]} fue:', 'ok')
                for e in equipos:
                    self._escribir('', f'   {e["posicion"]} {e["equipo"]} ({e["puntos"]} pts)', 'dim')
            else:
                self._escribir('LigaBot', f'No se encontraron datos para la temporada {cmd["temporada"]}', 'error')

        elif tipo == 'JORNADA':
            partidos = self.db.jornada(cmd['jornada'], cmd['temporada'])
            if partidos:
                ruta = generar_reporte_jornada(
                    partidos, cmd['jornada'], cmd['temporada'], cmd.get('archivo'))
                self._escribir('LigaBot',
                    f'Generando reporte de jornada {cmd["jornada"]} temporada {cmd["temporada"]}', 'ok')
                self._escribir('LigaBot', f'Reporte generado: {os.path.basename(ruta)}', 'dim')
                webbrowser.open(f'file://{os.path.abspath(ruta)}')
            else:
                self._escribir('LigaBot',
                    f'No se encontraron partidos para la jornada {cmd["jornada"]} en {cmd["temporada"]}', 'error')

        elif tipo == 'TABLA':
            tabla = self.db.tabla(cmd['temporada'])
            if tabla:
                ruta = generar_reporte_tabla(tabla, cmd['temporada'], cmd.get('archivo'))
                self._escribir('LigaBot',
                    f'Generando tabla de clasificacion temporada {cmd["temporada"]}', 'ok')
                self._escribir('LigaBot', f'Reporte generado: {os.path.basename(ruta)}', 'dim')
                webbrowser.open(f'file://{os.path.abspath(ruta)}')
            else:
                self._escribir('LigaBot'
                    f'No se encontraron datos para la temporada {cmd["temporada"]}', 'error')

        elif tipo == 'PARTIDOS':
            partidos = self.db.partidos(
                cmd['equipo'], cmd['temporada'], cmd.get('ji'), cmd.get('jf'))
            if partidos:
                ruta = generar_reporte_partidos(
                    partidos, cmd['equipo'], cmd['temporada'], cmd.get('archivo'))
                self._escribir('LigaBot',
                    f'Generando reporte de partidos de {cmd["equipo"]} en {cmd["temporada"]}', 'ok')
                self._escribir('LigaBot', f'Reporte generado: {os.path.basename(ruta)}', 'dim')
                webbrowser.open(f'file://{os.path.abspath(ruta)}')
            else:
                self._escribir('LigaBot',
                    f'No se encontraron partidos para "{cmd["equipo"]}" en {cmd["temporada"]}.', 'error')

#panel lateral

    def _abrir_tokens(self):
        if os.path.exists(RUTA_TOKENS):
            webbrowser.open(f'file://{os.path.abspath(RUTA_TOKENS)}')
        else:
            messagebox.showinfo('LigaBot', 'Analiza un comando primero')

    def _abrir_errores(self):
        if os.path.exists(RUTA_ERRORES):
            webbrowser.open(f'file://{os.path.abspath(RUTA_ERRORES)}')
        else:
            messagebox.showinfo('LigaBot', 'Analiza un comando primero.')

    def _abrir_err_sin(self):
        if os.path.exists(RUTA_ERR_SIN):
            webbrowser.open(f'file://{os.path.abspath(RUTA_ERR_SIN)}')
        else:
            messagebox.showinfo('LigaBot', 'Analiza un comando primero.')

    def _limpiar_tokens(self):
        self._todos_tokens.clear()
        if os.path.exists(RUTA_TOKENS): os.remove(RUTA_TOKENS)
        self._actualizar_contadores()
        self._escribir('LigaBot', 'Tokens limpiados', 'dim')
        self._sep()

    def _limpiar_errores(self):
        self._todos_errores.clear()
        self._todos_err_sin.clear()
        for r in [RUTA_ERRORES, RUTA_ERR_SIN]:
            if os.path.exists(r): os.remove(r)
        self._actualizar_contadores()
        self._escribir('LigaBot', 'Errores limpiados', 'dim')
        self._sep()

    def _limpiar_todo(self):
        self._limpiar_tokens()
        self._limpiar_errores()
        self._chat.config(state='normal')
        self._chat.delete('1.0', 'end')
        self._chat.config(state='disabled')
        self._bienvenida()

#Utilidades

    def _escribir(self, quien: str, texto: str, tag: str = ''):
        self._chat.config(state='normal')
        if quien:
            self._chat.insert('end', f'{quien}: ', tag or 'bot')
        self._chat.insert('end', f'{texto}\n', tag)
        self._chat.config(state='disabled')
        self._chat.see('end')

    def _sep(self):
        self._escribir('', '─' * 55, 'sep')

    def _actualizar_contadores(self):
        self._lbl_t.config(text=f'Tokens:  {len(self._todos_tokens)}')
        self._lbl_e.config(text=f'Errores: {len(self._todos_errores) + len(self._todos_err_sin)}')


def main():
    root = tk.Tk()
    LigaBotUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
