import os
from tokens import Token, ErrorLexico

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')


#Estilos compartido
_CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f4f6f9;
    color: #1a1a2e;
    padding: 32px 24px;
  }
  h1 { font-size: 22px; font-weight: 600; margin-bottom: 4px; }
  .subtitle { font-size: 13px; color: #666; margin-bottom: 24px; }
  table {
    width: 100%; border-collapse: collapse;
    background: #fff; border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,.08);
  }
  thead tr { background: #1a1a2e; color: #fff; }
  th { padding: 12px 16px; text-align: left; font-size: 12px;
      text-transform: uppercase; letter-spacing: .06em; font-weight: 500; }
  td { padding: 10px 16px; font-size: 13px;
      border-bottom: 1px solid #eef0f4; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f8f9ff; }
  .badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 999px; font-size: 11px; font-weight: 600;
  }
  .badge-reservada { background: #ede9fe; color: #4c1d95; }
  .badge-bandera   { background: #d1fae5; color: #065f46; }
  .badge-literal   { background: #fef3c7; color: #78350f; }
  .badge-simbolo   { background: #dbeafe; color: #1e3a8a; }
  .badge-especial  { background: #f1f5f9; color: #334155; }
  .badge-error     { background: #fee2e2; color: #7f1d1d; }
  .mono { font-family: 'Courier New', monospace; font-size: 13px; }
  .empty { text-align: center; color: #aaa; padding: 40px; font-size: 14px; }
  .count { font-size: 13px; color: #555; margin-top: 16px; }
"""

# Mapa de tipo como badge CSS
_BADGE = {
    'RESULTADO': 'reservada', 'VS': 'reservada', 'TEMPORADA': 'reservada',
    'JORNADA': 'reservada', 'GOLES': 'reservada', 'LOCAL': 'reservada',
    'VISITANTE': 'reservada', 'TOTAL': 'reservada', 'TABLA': 'reservada',
    'PARTIDOS': 'reservada', 'TOP': 'reservada', 'SUPERIOR': 'reservada',
    'INFERIOR': 'reservada', 'ADIOS': 'reservada',
    'FLAG_F': 'bandera', 'FLAG_N': 'bandera',
    'FLAG_JI': 'bandera', 'FLAG_JF': 'bandera',
    'CADENA': 'literal', 'TEMPORADA_VAL': 'literal',
    'NUMERO': 'literal', 'ID_ARCHIVO': 'literal',
    'LT': 'simbolo', 'GT': 'simbolo',
    'EOF': 'especial', 'ERROR': 'error',
}


def _clase_badge(tipo: str) -> str:
    return f"badge badge-{_BADGE.get(tipo, 'especial')}"

#  Reporte de tokens

def generar_reporte_tokens(tokens: list[Token],
                            ruta: str | None = None) -> str:
    #Genera Reporte_Token.html y devuelve la ruta del archivo

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = ruta or os.path.join(CARPETA_SALIDA, 'Reporte_Token.html')

    filas = ''
    for i, t in enumerate(tokens, 1):
        clase = _clase_badge(t.tipo)
        filas += (
            f'<tr>'
            f'<td>{i}</td>'
            f'<td class="mono">{_esc(t.lexema)}</td>'
            f'<td><span class="{clase}">{t.tipo}</span></td>'
            f'<td>{t.fila}</td>'
            f'<td>{t.columna}</td>'
            f'</tr>\n'
        )

    contenido_tabla = filas or f'<tr><td colspan="5" class="empty">No se encontraron tokens.</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>LigaBot — Reporte de Tokens</title>
  <style>{_CSS}</style>
</head>
<body>
  <h1> LigaBot — Reporte de Tokens</h1>
  <p class="subtitle">Analisis lexico | Tokens reconocidos</p>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Lexema</th>
        <th>Token</th>
        <th>Fila</th>
        <th>Columna</th>
      </tr>
    </thead>
    <tbody>
      {contenido_tabla}
    </tbody>
  </table>
  <p class="count">Total de tokens: <strong>{len(tokens)}</strong></p>
</body>
</html>"""

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)

    return ruta


#  Reporte de errores lexicos

def generar_reporte_errores(errores: list[ErrorLexico],
                            ruta: str | None = None) -> str:
    #Genera Reporte_Errores.html y devuelve la ruta del archivo

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = ruta or os.path.join(CARPETA_SALIDA, 'Reporte_Errores.html')

    filas = ''
    for i, e in enumerate(errores, 1):
        filas += (
            f'<tr>'
            f'<td>{i}</td>'
            f'<td class="mono">{_esc(e.lexema)}</td>'
            f'<td>{e.fila}</td>'
            f'<td>{e.columna}</td>'
            f'<td>{_esc(e.descripcion)}</td>'
            f'</tr>\n'
        )

    contenido_tabla = filas or (
        '<tr><td colspan="5" class="empty">'
        'No se encontraron errores lexicos.'
        '</td></tr>'
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>LigaBot — Reporte de Errores Lexicos</title>
  <style>{_CSS}</style>
</head>
<body>
  <h1> LigaBot — Reporte de Errores Lexicos</h1>
  <p class="subtitle">Analisis lexico | Caracteres o lexemas no reconocidos</p>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Lexema</th>
        <th>Fila</th>
        <th>Columna</th>
        <th>Descripción del error</th>
      </tr>
    </thead>
    <tbody>
      {contenido_tabla}
    </tbody>
  </table>
  <p class="count">Total de errores: <strong>{len(errores)}</strong></p>
</body>
</html>"""

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)

    return ruta


#Uttilidad interna
def _esc(texto: str) -> str:
    #Escapa caracteres especiales en el html
    return (texto
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

#  texto para rueba rapida
if __name__ == '__main__':
    from lexer import Lexer

    entrada = (
        'RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA <1979-1980>\n'
        'TOP SUPERIOR TEMPORADA <1979-1980> -n 3\n'
        'GOLES LOCAL "Real Madrid" TEMPORADA <1979-1980>\n'
        'JORNADA 1 TEMPORADA <1979-1980> -f jornada_1\n'
        'resultado @invalido "sin cerrar TEMPORADA <19791980>'
    )

    lex = Lexer(entrada)
    tokens, errores = lex.analizar()

    rt = generar_reporte_tokens(tokens)
    re = generar_reporte_errores(errores)

    print(f'Reporte de tokens  → {rt}')
    print(f'Reporte de errores → {re}')
    print(f'{len(tokens)} tokens, {len(errores)} errores')