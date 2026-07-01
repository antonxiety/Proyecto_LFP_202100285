import os

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), 'salidas')

# Estilos compartidos
_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9;
  color: #1a1a2e; padding: 32px 24px; }
h1 { font-size: 22px; font-weight: 600; margin-bottom: 4px; }
.subtitle { font-size: 13px; color: #666; margin-bottom: 24px; }
table { width: 100%; border-collapse: collapse; background: #fff;
  border-radius: 10px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.08); }
thead tr { background: #1a1a2e; color: #fff; }
th { padding: 12px 16px; text-align: left; font-size: 12px;
  text-transform: uppercase; letter-spacing: .06em; }
td { padding: 10px 16px; font-size: 13px;
  border-bottom: 1px solid #eef0f4; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8f9ff; }
.victoria { color: #065f46; font-weight: 600; }
.derrota  { color: #7f1d1d; font-weight: 600; }
.empate   { color: #78350f; font-weight: 600; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px;
  font-size:11px; font-weight:600; }
.badge-error { background:#fee2e2; color:#7f1d1d; }
.count { font-size:13px; color:#555; margin-top:16px; }
.pos { font-weight: 700; color: #1a1a2e; }
"""

def _esc(t: str) -> str:
    return (str(t).replace('&','&amp;').replace('<','&lt;')
            .replace('>','&gt;').replace('"','&quot;'))

def _html_base(titulo: str, subtitulo: str, tabla: str, total: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8">
<title>LigaBot — {titulo}</title>
<style>{_CSS}</style>
</head>
<body>
<h1>LigaBot — {titulo}</h1>
<p class="subtitle">{subtitulo}</p>
{tabla}
<p class="count">{total}</p>
</body>
</html>"""


#Reportes de errores sintacticos
def generar_reporte_errores_sintacticos(errores: list,
                                        ruta: str | None = None) -> str:
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = ruta or os.path.join(CARPETA_SALIDA, 'Reporte_Errores_S.html')

    filas = ''
    for i, e in enumerate(errores, 1):
        filas += (f'<tr><td>{i}</td>'
                  f'<td>{e.linea}</td><td>{e.columna}</td>'
                  f'<td><span class="badge badge-error">{_esc(e.token_recibido)}</span></td>'
                  f'<td>{_esc(e.token_esperado)}</td>'
                  f'<td>{_esc(e.descripcion)}</td></tr>\n')

    tabla = f"""<table>
<thead><tr><th>#</th><th>Fila</th><th>Col</th>
<th>Token recibido</th><th>Token esperado</th><th>Descripción</th></tr></thead>
<tbody>{filas or '<tr><td colspan="6" style="text-align:center;color:#aaa;padding:40px">No hay errores sintacticos</td></tr>'}</tbody>
</table>"""

    html = _html_base('Reporte de Errores Sintacticos',
                    'Fase 2 — Analisis sintactico',
                    tabla, f'Total de errores: <strong>{len(errores)}</strong>')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


#Reporte de jornada

def generar_reporte_jornada(partidos: list, jornada: int,
                            temporada: str, nombre: str | None = None) -> str:
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    nombre_archivo = (nombre or f'jornada_{jornada}') + '.html'
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)

    filas = ''
    for i, p in enumerate(partidos, 1):
        filas += (f'<tr><td>{i}</td>'
                f'<td>{_esc(p["local"])}</td>'
                f'<td>{_esc(p["visitante"])}</td>'
                f'<td style="text-align:center">{p["goles_local"]}</td>'
                f'<td style="text-align:center">{p["goles_visitante"]}</td></tr>\n')

    tabla = f"""<table>
<thead><tr><th>#</th><th>Equipo local</th><th>Equipo visitante</th>
<th>Goles local</th><th>Goles visitante</th></tr></thead>
<tbody>{filas or '<tr><td colspan="5" style="text-align:center;color:#aaa;padding:40px">No se encontraron partidos</td></tr>'}</tbody>
</table>"""

    html = _html_base(f'Jornada {jornada} — Temporada {temporada}',
                    f'Resultados de la jornada {jornada} · temporada {temporada}',
                    tabla, f'Total de partidos: <strong>{len(partidos)}</strong>')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


#Reporte de tabla de posiciones

def generar_reporte_tabla(tabla: list, temporada: str,
                        nombre: str | None = None) -> str:
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    nombre_archivo = (nombre or f'tabla_{temporada}') + '.html'
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)

    filas = ''
    for fila in tabla:
        pos = fila['posicion']
        medal = {1: '1', 2: '2', 3: '3'}.get(pos, str(pos))
        filas += (f'<tr>'
                f'<td class="pos">{medal}</td>'
                f'<td>{_esc(fila["equipo"])}</td>'
                f'<td style="text-align:center;font-weight:600">{fila["puntos"]}</td>'
                f'</tr>\n')

    tabla_html = f"""<table>
<thead><tr><th>Posición</th><th>Equipo</th><th>Puntos</th></tr></thead>
<tbody>{filas or '<tr><td colspan="3" style="text-align:center;color:#aaa;padding:40px">No se encontraron datos</td></tr>'}</tbody>
</table>"""

    html = _html_base(f'Tabla de Clasificación — {temporada}',
                    f'Temporada {temporada} - 3 pts victoria - 1 pt empate',
                    tabla_html,
                    f'Total de equipos: <strong>{len(tabla)}</strong>')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta


#Reporte de partidos por equipo

def generar_reporte_partidos(partidos: list, equipo: str,
                            temporada: str, nombre: str | None = None) -> str:
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    nombre_archivo = (nombre or f'partidos_{equipo.replace(" ","_")}') + '.html'
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)

    filas = ''
    for p in partidos:
        res = p['resultado_equipo']
        clase = {'Victoria': 'victoria', 'Derrota': 'derrota',
                'Empate': 'empate'}.get(res, '')
        filas += (f'<tr>'
                f'<td style="text-align:center">{p["jornada"]}</td>'
                f'<td>{_esc(p["local"])}</td>'
                f'<td>{_esc(p["visitante"])}</td>'
                f'<td style="text-align:center">{p["goles_local"]} - {p["goles_visitante"]}</td>'
                f'<td class="{clase}">{res}</td>'
                f'</tr>\n')

    tabla = f"""<table>
<thead><tr><th>Jornada</th><th>Local</th><th>Visitante</th>
<th>Marcador</th><th>Resultado para {_esc(equipo)}</th></tr></thead>
<tbody>{filas or '<tr><td colspan="5" style="text-align:center;color:#aaa;padding:40px">No se encontraron partidos.</td></tr>'}</tbody>
</table>"""

    html = _html_base(f'Partidos de {equipo} — {temporada}',
                    f'{equipo} · temporada {temporada}',
                    tabla,
                    f'Total de partidos: <strong>{len(partidos)}</strong>')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(html)
    return ruta
