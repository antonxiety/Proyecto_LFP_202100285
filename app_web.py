import json, os, sys, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))

from lexer          import Lexer
from parser         import Parser
from csv_reader     import LigaBotCSV
from reportes       import generar_reporte_tokens, generar_reporte_errores
from reportes_fase2 import (generar_reporte_errores_sintacticos,generar_reporte_jornada, generar_reporte_tabla,generar_reporte_partidos)

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')
RUTA_TOKENS    = os.path.join(CARPETA_SALIDA, 'Reporte_Token.html')
RUTA_ERRORES   = os.path.join(CARPETA_SALIDA, 'Reporte_Errores.html')
RUTA_ERR_SIN   = os.path.join(CARPETA_SALIDA, 'Reporte_Errores_S.html')
RUTA_CSV       = os.path.join(os.path.dirname(__file__), 'LaLigaBot-LFP.csv')

###
_db     = LigaBotCSV(RUTA_CSV)
_sesion = {'tokens': [], 'errores': [], 'err_sin': []}

HTML_APP = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LigaBot</title>
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',Arial,sans-serif; background:#1a1a2e; color:#eaeaea;
  height:100vh; display:flex; flex-direction:column; }
header { background:#16213e; padding:12px 20px; border-bottom:3px solid #e94560;
  display:flex; align-items:center; gap:12px; }
header h1 { font-size:18px; font-weight:600; }
.csv-ok  { font-size:12px; color:#06d6a0; }
.csv-err { font-size:12px; color:#ff6b6b; }
.main { display:flex; flex:1; overflow:hidden; padding:12px; gap:12px; }
.chat-wrap { flex:1; display:flex; flex-direction:column; gap:8px; }
#chat { flex:1; background:#16213e; border-radius:10px; padding:16px;
  overflow-y:auto; font-size:13px; font-family:'Consolas',monospace; line-height:1.7; }
.msg-bot   { color:#00b4d8; font-weight:600; }
.msg-user  { color:#90e0ef; }
.msg-ok    { color:#06d6a0; }
.msg-error { color:#ff6b6b; }
.msg-dim   { color:#556677; }
.msg-sep   { color:#2a3a4a; }
.entrada { display:flex; gap:8px; background:#0f3460; border-radius:8px; padding:8px 12px; }
#input { flex:1; background:transparent; border:none; outline:none;
  color:#eaeaea; font-family:'Consolas',monospace; font-size:13px; }
#input::placeholder { color:#556677; }
button.primary { background:#e94560; color:#fff; border:none;
  padding:8px 18px; border-radius:6px; cursor:pointer; font-size:13px; font-weight:500; }
button.primary:hover { background:#c73652; }
.panel { width:185px; background:#16213e; border-radius:10px;
  padding:14px; display:flex; flex-direction:column; gap:5px; }
.panel-title { font-size:10px; font-weight:600; color:#8899aa;
  text-transform:uppercase; letter-spacing:.08em; margin:8px 0 4px; }
.panel-title:first-child { margin-top:0; }
button.sec { background:#0f3460; color:#eaeaea; border:none;
  padding:7px 10px; border-radius:6px; cursor:pointer;
  font-size:12px; text-align:left; width:100%; }
button.sec:hover { background:#1a4a80; }
.divider { border-top:1px solid #2a3a4a; margin:4px 0; }
#cnt-t { font-size:11px; color:#06d6a0; }
#cnt-e { font-size:11px; color:#ff6b6b; }
</style>
</head>
<body>
<header>
  <h1>LigaBot</h1>
  <span class="CSV_CLASS">CSV_STATUS</span>
</header>
<div class="main">
  <div class="chat-wrap">
    <div id="chat">
      <div class="msg-bot">LigaBot: Bienvenido. Ingrese un comando.</div>
      <div class="msg-dim">Ejemplo: RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA &lt;1979-1980&gt;</div>
      <div class="msg-sep">───────────────────────────────────────────────</div>
    </div>
    <div class="entrada">
      <input id="input" type="text" placeholder='Escriba un comando de LigaBot...' autocomplete="off"/>
      <button class="primary" onclick="enviar()">Enviar ▶</button>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">Reportes</div>
    <button class="sec" onclick="abrirReporte('tokens')">Tokens</button>
    <button class="sec" onclick="abrirReporte('errores')">Errores Lexicos</button>
    <button class="sec" onclick="abrirReporte('errores_s')">Errores Sintacticos</button>
    <div class="divider"></div>
    <div class="panel-title">Limpiar</div>
    <button class="sec" onclick="limpiar('tokens')">Tokens</button>
    <button class="sec" onclick="limpiar('errores')">Errores</button>
    <button class="sec" onclick="limpiar('todo')">Todo</button>
    <div class="divider"></div>
    <div id="cnt-t">Tokens:  0</div>
    <div id="cnt-e">Errores: 0</div>
  </div>
</div>
<script>
const chat  = document.getElementById('chat');
const input = document.getElementById('input');
input.addEventListener('keydown', e => { if(e.key==='Enter') enviar(); });

function msg(texto, cls) {
  const d = document.createElement('div');
  d.className = cls||''; d.textContent = texto;
  chat.appendChild(d); chat.scrollTop = chat.scrollHeight;
}

async function enviar() {
  const texto = input.value.trim();
  if(!texto) return;
  input.value = '';
  msg('Tú: '+texto, 'msg-user');

  const res  = await fetch('/analizar', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({texto})
  });
  const data = await res.json();

  // Errores lexicos
  data.err_lex.forEach(e => {
    msg(`   Error lexico [${e.fila}:${e.col}]: ${e.descripcion}`, 'msg-error');
  });

  // Errores sintacticos
  data.err_sin.forEach(e => {
    msg(`   Error sintactico [${e.fila}:${e.col}]: ${e.descripcion}`, 'msg-error');
  });

  // Respuesta del chatbot
  if(data.respuesta) {
    msg('LigaBot: '+data.respuesta, data.error ? 'msg-error' : 'msg-ok');
  }
  data.detalles && data.detalles.forEach(d => msg('   '+d, 'msg-dim'));

  if(data.reporte) {
    msg('Reporte generado: '+data.reporte, 'msg-dim');
    window.open('/reporte/archivo/'+data.reporte, '_blank');
  }

  document.getElementById('cnt-t').textContent = 'Tokens:  '+data.total_tokens;
  document.getElementById('cnt-e').textContent = 'Errores: '+data.total_errores;
  msg('───────────────────────────────────────────────', 'msg-sep');
}

async function limpiar(tipo) {
  const res  = await fetch('/limpiar', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({tipo})
  });
  const data = await res.json();
  document.getElementById('cnt-t').textContent = 'Tokens:  '+data.total_tokens;
  document.getElementById('cnt-e').textContent = 'Errores: '+data.total_errores;
  if(tipo==='todo') {
    chat.innerHTML='';
    msg('LigaBot: Todo limpiado. Listo para analizar.','msg-bot');
    msg('───────────────────────────────────────────────','msg-sep');
  } else {
    msg('LigaBot: '+tipo+' limpiados.','msg-dim');
  }
}

function abrirReporte(tipo) { window.open('/reporte/'+tipo,'_blank'); }
</script>
</body>
</html>"""


def _ejecutar_comando(cmd: dict) -> dict:
    """Ejecuta un comando y devuelve la respuesta para el chatbot"""
    tipo = cmd.get('tipo','')
    resp = {'respuesta':'', 'detalles':[], 'reporte':None, 'error':False}

    if tipo == 'ADIOS':
        resp['respuesta'] = 'ADIOS, '

    elif tipo == 'RESULTADO':
        r = _db.resultado(cmd['local'], cmd['visitante'], cmd['temporada'])
        if r['encontrado']:
            resp['respuesta'] = (f'El resultado fue: {r["local"]} {r["goles_local"]} - '
                                f'{r["goles_visitante"]} {r["visitante"]}')
        else:
            resp['respuesta'] = (f'No se encontro el partido {cmd["local"]} vs '
                                f'{cmd["visitante"]} en {cmd["temporada"]}')
            resp['error'] = True

    elif tipo == 'GOLES':
        sub = cmd['subtipo']
        if sub == 'LOCAL':
            r = _db.goles_local(cmd['equipo'], cmd['temporada'])
            resp['respuesta'] = (f'Los goles anotados por {cmd["equipo"]} en local '
                                f'en la temporada {cmd["temporada"]} fueron {r["total"]}')
        elif sub == 'VISITANTE':
            r = _db.goles_visitante(cmd['equipo'], cmd['temporada'])
            resp['respuesta'] = (f'Los goles anotados por {cmd["equipo"]} en visitante '
                                f'en la temporada {cmd["temporada"]} fueron {r["total"]}')
        else:
            r = _db.goles_total(cmd['equipo'], cmd['temporada'])
            resp['respuesta'] = (f'Los goles anotados por {cmd["equipo"]} en total '
                                f'en la temporada {cmd["temporada"]} fueron {r["total"]}')
        if not r['encontrado']:
            resp['respuesta'] = f'No se encontro al equipo "{cmd["equipo"]}" en {cmd["temporada"]}'
            resp['error'] = True

    elif tipo == 'TOP':
        superior = (cmd['subtipo'] == 'SUPERIOR')
        equipos  = _db.top(cmd['temporada'], cmd['cantidad'], superior)
        tipo_str = 'superior' if superior else 'inferior'
        if equipos:
            resp['respuesta'] = f'El top {tipo_str} de la temporada {cmd["temporada"]} fue:'
            for e in equipos:
                resp['detalles'].append(f'{e["posicion"]}. {e["equipo"]} ({e["puntos"]} pts)')
        else:
            resp['respuesta'] = f'No se encontro datos para {cmd["temporada"]}'
            resp['error'] = True

    elif tipo == 'JORNADA':
        partidos = _db.jornada(cmd['jornada'], cmd['temporada'])
        if partidos:
            ruta = generar_reporte_jornada(partidos, cmd['jornada'],
                                          cmd['temporada'], cmd.get('archivo'))
            resp['respuesta'] = (f'Generando reporte de jornada {cmd["jornada"]} '
                                f'temporada {cmd["temporada"]}.')
            resp['reporte'] = os.path.basename(ruta)
        else:
            resp['respuesta'] = f'No hay partidos para jornada {cmd["jornada"]} en {cmd["temporada"]}'
            resp['error'] = True

    elif tipo == 'TABLA':
        tabla = _db.tabla(cmd['temporada'])
        if tabla:
            ruta = generar_reporte_tabla(tabla, cmd['temporada'], cmd.get('archivo'))
            resp['respuesta'] = f'Generando tabla de clasificacion temporada {cmd["temporada"]}'
            resp['reporte'] = os.path.basename(ruta)
        else:
            resp['respuesta'] = f'No se encontraron datos para {cmd["temporada"]}'
            resp['error'] = True

    elif tipo == 'PARTIDOS':
        partidos = _db.partidos(cmd['equipo'], cmd['temporada'],
                                cmd.get('ji'), cmd.get('jf'))
        if partidos:
            ruta = generar_reporte_partidos(partidos, cmd['equipo'],
                                            cmd['temporada'], cmd.get('archivo'))
            resp['respuesta'] = f'Generando reporte de partidos de {cmd["equipo"]} en {cmd["temporada"]}'
            resp['reporte'] = os.path.basename(ruta)
        else:
            resp['respuesta'] = f'No se encontraron partidos para "{cmd["equipo"]}" en {cmd["temporada"]}'
            resp['error'] = True

    return resp


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args): pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        if path == '/':
            estado  = 'CSV cargado' if _db.cargado else 'CSV no encontrado'
            clase   = 'csv-ok' if _db.cargado else 'csv-err'
            html    = (HTML_APP
                      .replace('CSV_STATUS', estado)
                      .replace('CSV_CLASS', clase))
            self._resp(200, 'text/html', html.encode())

        elif path == '/reporte/tokens':
            self._servir(RUTA_TOKENS)
        elif path == '/reporte/errores':
            self._servir(RUTA_ERRORES)
        elif path == '/reporte/errores_s':
            self._servir(RUTA_ERR_SIN)
        elif path.startswith('/reporte/archivo/'):
            nombre = path.split('/reporte/archivo/')[-1]
            self._servir(os.path.join(CARPETA_SALIDA, nombre))
        else:
            self._resp(404, 'text/plain', b'Not found')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = json.loads(self.rfile.read(length))

        if self.path == '/analizar':
            texto = body.get('texto', '')

            # Lexico
            lex = Lexer(texto)
            tokens, err_lex = lex.analizar()
            _sesion['tokens'].extend(tokens)
            _sesion['errores'].extend(err_lex)

            # Sintactico
            p = Parser(tokens)
            cmd, err_sin = p.analizar()
            _sesion['err_sin'].extend(err_sin)

            # Ejecutar si es valido
            chat_resp = {}
            if cmd and not err_sin:
                chat_resp = _ejecutar_comando(cmd)

            # Regenerar reportes
            os.makedirs(CARPETA_SALIDA, exist_ok=True)
            generar_reporte_tokens(_sesion['tokens'], RUTA_TOKENS)
            generar_reporte_errores(_sesion['errores'], RUTA_ERRORES)
            generar_reporte_errores_sintacticos(_sesion['err_sin'], RUTA_ERR_SIN)

            payload = json.dumps({
                'err_lex'     : [{'descripcion': e.descripcion,
                                  'fila': e.fila, 'col': e.columna}
                                for e in err_lex],
                'err_sin'     : [{'descripcion': e.descripcion,
                                  'fila': e.linea, 'col': e.columna}
                                for e in err_sin],
                'respuesta'   : chat_resp.get('respuesta', ''),
                'detalles'    : chat_resp.get('detalles', []),
                'reporte'     : chat_resp.get('reporte'),
                'error'       : chat_resp.get('error', False),
                'total_tokens': len(_sesion['tokens']),
                'total_errores': len(_sesion['errores']) + len(_sesion['err_sin']),
            }).encode()
            self._resp(200, 'application/json', payload)

        elif self.path == '/limpiar':
            tipo = body.get('tipo', 'todo')
            if tipo in ('tokens', 'todo'):
                _sesion['tokens'].clear()
                if os.path.exists(RUTA_TOKENS): os.remove(RUTA_TOKENS)
            if tipo in ('errores', 'todo'):
                _sesion['errores'].clear()
                _sesion['err_sin'].clear()
                for r in [RUTA_ERRORES, RUTA_ERR_SIN]:
                    if os.path.exists(r): os.remove(r)
            payload = json.dumps({
                'total_tokens' : len(_sesion['tokens']),
                'total_errores': len(_sesion['errores']) + len(_sesion['err_sin']),
            }).encode()
            self._resp(200, 'application/json', payload)

    def _resp(self, code, ctype, body):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _servir(self, ruta):
        if not os.path.exists(ruta):
            self._resp(200, 'text/html',
                      b'<h2>Reporte no generado todavia, Analiza un comando primero</h2>')
            return
        with open(ruta, 'rb') as f:
            self._resp(200, 'text/html', f.read())


def iniciar(puerto: int = 8080):
    server = HTTPServer(('localhost', puerto), Handler)
    url    = f'http://localhost:{puerto}'
    print(f'LigaBot Iniciando en {url}')
    print(f'LigaBot Ctrl+C para detener.')
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[LigaBot] Servidor detenido')


if __name__ == '__main__':
    iniciar()
