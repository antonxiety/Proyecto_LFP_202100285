#  app_web.py  —  Interfaz web de LigaBot (Fase 1)
#  Solo usa librerías de la stdlib: http.server, json, os


import json
import os
import sys
import webbrowser
from http.server    import BaseHTTPRequestHandler, HTTPServer
from urllib.parse   import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(__file__))

from lexer    import Lexer
from reportes import generar_reporte_tokens, generar_reporte_errores

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')
RUTA_TOKENS    = os.path.join(CARPETA_SALIDA, 'Reporte_Token.html')
RUTA_ERRORES   = os.path.join(CARPETA_SALIDA, 'Reporte_Errores.html')

# Estado global de la sesion
_sesion = {'tokens': [], 'errores': [], 'historial': []}

#HTML de la aplicacion 

HTML_APP = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LigaBot — Analizador Léxico</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #1a1a2e; color: #eaeaea;
    height: 100vh; display: flex; flex-direction: column;
  }
  header {
    background: #16213e; padding: 12px 20px;
    border-bottom: 3px solid #e94560;
    display: flex; align-items: center; gap: 12px;
  }
  header h1 { font-size: 18px; font-weight: 600; }
  header span { font-size: 12px; color: #8899aa; }
  .main { display: flex; flex: 1; overflow: hidden; padding: 12px; gap: 12px; }

  /* Chat */
  .chat-wrap { flex: 1; display: flex; flex-direction: column; gap: 8px; }
  #chat {
    flex: 1; background: #16213e; border-radius: 10px;
    padding: 16px; overflow-y: auto; font-size: 13px;
    font-family: 'Consolas', monospace; line-height: 1.6;
  }
  .msg-bot   { color: #00b4d8; }
  .msg-user  { color: #90e0ef; }
  .msg-ok    { color: #06d6a0; }
  .msg-error { color: #ff6b6b; }
  .msg-dim   { color: #556677; }
  .msg-sep   { color: #2a3a4a; }
  .entrada {
    display: flex; gap: 8px;
    background: #0f3460; border-radius: 8px; padding: 8px 12px;
  }
  #input {
    flex: 1; background: transparent; border: none; outline: none;
    color: #eaeaea; font-family: 'Consolas', monospace; font-size: 13px;
  }
  #input::placeholder { color: #556677; }
  button.primary {
    background: #e94560; color: #fff; border: none;
    padding: 8px 18px; border-radius: 6px; cursor: pointer;
    font-size: 13px; font-weight: 500;
  }
  button.primary:hover { background: #c73652; }

  /* Panel lateral */
  .panel {
    width: 180px; background: #16213e; border-radius: 10px;
    padding: 16px; display: flex; flex-direction: column; gap: 6px;
  }
  .panel-title {
    font-size: 10px; font-weight: 600; color: #8899aa;
    text-transform: uppercase; letter-spacing: .08em;
    margin-bottom: 4px; margin-top: 8px;
  }
  .panel-title:first-child { margin-top: 0; }
  button.sec {
    background: #0f3460; color: #eaeaea; border: none;
    padding: 7px 10px; border-radius: 6px; cursor: pointer;
    font-size: 12px; text-align: left; width: 100%;
  }
  button.sec:hover { background: #1a4a80; }
  .divider { border-top: 1px solid #2a3a4a; margin: 4px 0; }
  #contador-t { font-size: 11px; color: #06d6a0; }
  #contador-e { font-size: 11px; color: #ff6b6b; }
</style>
</head>
<body>
<header>
  <span style="font-size:22px"></span>
  <h1>LigaBot</h1>
  <span>Analizador Léxico — Fase 1</span>
</header>
<div class="main">
  <div class="chat-wrap">
    <div id="chat">
      <div class="msg-bot">LigaBot: Bienvenido. Escribe un comando o texto y presiona Analizar.</div>
      <div class="msg-dim">Ejemplo: RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA &lt;1979-1980&gt;</div>
      <div class="msg-sep">───────────────────────────────────────────────────</div>
    </div>
    <div class="entrada">
      <input id="input" type="text"
        placeholder='Escribe un comando de LigaBot...' autocomplete="off" />
      <button class="primary" onclick="analizar()">Analizar ▶</button>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">Reportes</div>
    <button class="sec" onclick="abrirReporte('tokens')"> Reporte de Tokens</button>
    <button class="sec" onclick="abrirReporte('errores')"> Reporte de Errores</button>
    <div class="divider"></div>
    <div class="panel-title">Limpiar</div>
    <button class="sec" onclick="limpiar('tokens')">🗑 Limpiar Tokens</button>
    <button class="sec" onclick="limpiar('errores')">🗑 Limpiar Errores</button>
    <button class="sec" onclick="limpiar('todo')">🗑 Limpiar Todo</button>
    <div class="divider"></div>
    <div id="contador-t">Tokens:  0</div>
    <div id="contador-e">Errores: 0</div>
  </div>
</div>
<script>
  const chat  = document.getElementById('chat');
  const input = document.getElementById('input');

  input.addEventListener('keydown', e => { if (e.key === 'Enter') analizar(); });

  function escribir(texto, cls) {
    const d = document.createElement('div');
    d.className = cls || '';
    d.textContent = texto;
    chat.appendChild(d);
    chat.scrollTop = chat.scrollHeight;
  }

  async function analizar() {
    const texto = input.value.trim();
    if (!texto) return;
    input.value = '';
    escribir('Tú: ' + texto, 'msg-user');

    const res  = await fetch('/analizar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({texto})
    });
    const data = await res.json();

    if (data.tokens.length > 0) {
      escribir('LigaBot:  Se reconocieron ' + data.tokens.length + ' token(s).', 'msg-ok');
      data.tokens.forEach(t => {
        escribir(`   [${t.fila}:${t.col}]  ${t.tipo.padEnd(18)} → "${t.lexema}"`, 'msg-dim');
      });
    }
    if (data.errores.length > 0) {
      escribir('LigaBot:  ' + data.errores.length + ' error(es) léxico(s):', 'msg-error');
      data.errores.forEach(e => {
        escribir(`   [${e.fila}:${e.col}]  ${e.descripcion}`, 'msg-error');
      });
    }

    document.getElementById('contador-t').textContent = 'Tokens:  ' + data.total_tokens;
    document.getElementById('contador-e').textContent = 'Errores: ' + data.total_errores;
    escribir('───────────────────────────────────────────────────', 'msg-sep');
  }

  async function limpiar(tipo) {
    const res  = await fetch('/limpiar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tipo})
    });
    const data = await res.json();
    document.getElementById('contador-t').textContent = 'Tokens:  ' + data.total_tokens;
    document.getElementById('contador-e').textContent = 'Errores: ' + data.total_errores;
    if (tipo === 'todo') {
      chat.innerHTML = '';
      escribir('LigaBot: Todo limpiado. Listo para analizar.', 'msg-bot');
      escribir('───────────────────────────────────────────────────', 'msg-sep');
    } else {
      escribir('LigaBot: ' + tipo + ' limpiados.', 'msg-dim');
    }
  }

  function abrirReporte(tipo) {
    window.open('/reporte/' + tipo, '_blank');
  }
</script>
</body>
</html>"""


#Manejador del HTTP

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass   # silenciar logs de consola

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/':
            self._responder(200, 'text/html', HTML_APP.encode())

        elif parsed.path == '/reporte/tokens':
            self._servir_archivo(RUTA_TOKENS)

        elif parsed.path == '/reporte/errores':
            self._servir_archivo(RUTA_ERRORES)

        else:
            self._responder(404, 'text/plain', b'Not found')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = json.loads(self.rfile.read(length))

        if self.path == '/analizar':
            texto  = body.get('texto', '')
            lex    = Lexer(texto)
            tokens, errores = lex.analizar()

            _sesion['tokens'].extend(tokens)
            _sesion['errores'].extend(errores)

            os.makedirs(CARPETA_SALIDA, exist_ok=True)
            generar_reporte_tokens(_sesion['tokens'], RUTA_TOKENS)
            generar_reporte_errores(_sesion['errores'], RUTA_ERRORES)

            payload = json.dumps({
                'tokens' : [{'tipo': t.tipo, 'lexema': t.lexema,
                              'fila': t.fila, 'col': t.columna} for t in tokens],
                'errores': [{'lexema': e.lexema, 'fila': e.fila,
                              'col': e.columna, 'descripcion': e.descripcion}
                             for e in errores],
                'total_tokens' : len(_sesion['tokens']),
                'total_errores': len(_sesion['errores']),
            }).encode()
            self._responder(200, 'application/json', payload)

        elif self.path == '/limpiar':
            tipo = body.get('tipo', 'todo')
            if tipo in ('tokens', 'todo'):
                _sesion['tokens'].clear()
                if os.path.exists(RUTA_TOKENS): os.remove(RUTA_TOKENS)
            if tipo in ('errores', 'todo'):
                _sesion['errores'].clear()
                if os.path.exists(RUTA_ERRORES): os.remove(RUTA_ERRORES)

            payload = json.dumps({
                'total_tokens' : len(_sesion['tokens']),
                'total_errores': len(_sesion['errores']),
            }).encode()
            self._responder(200, 'application/json', payload)

    def _responder(self, code, content_type, body):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _servir_archivo(self, ruta):
        if not os.path.exists(ruta):
            msg = b'<h2>Reporte no generado todavia, Analiza algun texto primero</h2>'
            self._responder(200, 'text/html', msg)
            return
        with open(ruta, 'rb') as f:
            contenido = f.read()
        self._responder(200, 'text/html', contenido)


#Punto de entrada
def iniciar(puerto: int = 8080):
    server = HTTPServer(('localhost', puerto), Handler)
    url    = f'http://localhost:{puerto}'
    print(f'[LigaBot] Servidor iniciado en {url}')
    print(f'[LigaBot] Abre tu navegador en: {url}')
    print(f'[LigaBot] Presiona Ctrl+C para detener.')
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[LigaBot] Servidor detenido.')


if __name__ == '__main__':
    iniciar()