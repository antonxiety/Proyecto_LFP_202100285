
import csv
import os


class LigaBotCSV:
    """Carga el CSV y responde todas las consultas del chatbot"""

    def __init__(self, ruta: str):
        self.ruta    = ruta
        self.datos   = []       # lista de dicts con todas las filas
        self.cargado = False
        self._cargar()

#Carga inicial del

    def _cargar(self):
        """Lee el CSV completo y lo guarda en memoria"""
        if not os.path.exists(self.ruta):
            self.cargado = False
            return
        try:
            with open(self.ruta, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for fila in reader:
                    # Convertir tipos numericos al cargar
                    self.datos.append({
                        'Fecha'     : fila['Fecha'],
                        'Temporada' : fila['Temporada'],
                        'Jornada'   : int(fila['Jornada']),
                        'Equipo1'   : fila['Equipo1'],    # local
                        'Equipo2'   : fila['Equipo2'],    # visitante
                        'Goles1'    : int(fila['Goles1']),
                        'Goles2'    : int(fila['Goles2']),
                    })
            self.cargado = True
        except Exception as e:
            self.cargado = False

# Utilidad interna

    def _normalizar(self, texto: str) -> str:
        """Normaliza texto para comparaciones: minusculas y sin espacios extra"""
        return texto.strip().lower()

    def _mismo_equipo(self, nombre_csv: str, nombre_buscar: str) -> bool:
        """Compara dos nombres de equipo de forma flexible"""
        return self._normalizar(nombre_csv) == self._normalizar(nombre_buscar)

    def _filtrar_temporada(self, temporada: str) -> list:
        """Devuelve solo los partidos de una temporada"""
        return [f for f in self.datos if f['Temporada'] == temporada]

#Consultas del chatbot

    def resultado(self, local: str, visitante: str, temporada: str) -> dict:
        """Busca el resultado exacto de un partido"""
        for f in self._filtrar_temporada(temporada):
            if (self._mismo_equipo(f['Equipo1'], local) and
                    self._mismo_equipo(f['Equipo2'], visitante)):
                return {
                    'encontrado'    : True,
                    'local'         : f['Equipo1'],
                    'visitante'     : f['Equipo2'],
                    'goles_local'   : f['Goles1'],
                    'goles_visitante': f['Goles2'],
                    'jornada'       : f['Jornada'],
                }
        return {'encontrado': False, 'local': local, 'visitante': visitante}

    def goles_local(self, equipo: str, temporada: str) -> dict:
        """Suma los goles anotados por el equipo jugando como local"""
        partidos = self._filtrar_temporada(temporada)
        total = sum(f['Goles1'] for f in partidos
                    if self._mismo_equipo(f['Equipo1'], equipo))
        encontrado = any(self._mismo_equipo(f['Equipo1'], equipo) for f in partidos)
        return {'total': total, 'encontrado': encontrado, 'equipo': equipo}

    def goles_visitante(self, equipo: str, temporada: str) -> dict:
        """Suma los goles anotados por el equipo jugando como visitante"""
        partidos = self._filtrar_temporada(temporada)
        total = sum(f['Goles2'] for f in partidos
                    if self._mismo_equipo(f['Equipo2'], equipo))
        encontrado = any(self._mismo_equipo(f['Equipo2'], equipo) for f in partidos)
        return {'total': total, 'encontrado': encontrado, 'equipo': equipo}

    def goles_total(self, equipo: str, temporada: str) -> dict:
        """Suma todos los goles del equipo (local + visitante)"""
        local     = self.goles_local(equipo, temporada)
        visitante = self.goles_visitante(equipo, temporada)
        return {
            'total'     : local['total'] + visitante['total'],
            'encontrado': local['encontrado'] or visitante['encontrado'],
            'equipo'    : equipo,
        }

    def jornada(self, numero: int, temporada: str) -> list:
        """Devuelve todos los partidos de una jornada especifica"""
        return [
            {
                'local':          f['Equipo1'],
                'visitante':      f['Equipo2'],
                'goles_local':    f['Goles1'],
                'goles_visitante':f['Goles2'],
                'jornada':        f['Jornada'],
            }
            for f in self._filtrar_temporada(temporada)
            if f['Jornada'] == numero
        ]

    def tabla(self, temporada: str) -> list:
        """Calcula la tabla de clasificación de una temporada"""
        puntos = {}   # equipo && puntos

        for f in self._filtrar_temporada(temporada):
            e1 = f['Equipo1']
            e2 = f['Equipo2']
            g1 = f['Goles1']
            g2 = f['Goles2']

#Inicializar
            puntos.setdefault(e1, 0)
            puntos.setdefault(e2, 0)

            if g1 > g2:      # Victoria local
                puntos[e1] += 3
            elif g2 > g1:    # Victoria visitante
                puntos[e2] += 3
            else:            # Empate
                puntos[e1] += 1
                puntos[e2] += 1

#Ordenar de mayor a menor puntos
        tabla = [{'equipo': eq, 'puntos': pts}
                for eq, pts in puntos.items()]
        tabla.sort(key=lambda x: x['puntos'], reverse=True)

#agregar posciion
        for i, fila in enumerate(tabla, 1):
            fila['posicion'] = i

        return tabla

    def partidos(self, equipo: str, temporada: str,
                ji: int | None = None, jf: int | None = None) -> list:
        """Devuelve los partidos de un equipo, con filtros opcionales"""
        resultado = []
        for f in self._filtrar_temporada(temporada):
            es_local     = self._mismo_equipo(f['Equipo1'], equipo)
            es_visitante = self._mismo_equipo(f['Equipo2'], equipo)

            if not es_local and not es_visitante:
                continue

#Filtro de jornadas
            if ji is not None and f['Jornada'] < ji:
                continue
            if jf is not None and f['Jornada'] > jf:
                continue

#Calcular resultado para el equipo
            g1, g2 = f['Goles1'], f['Goles2']
            if es_local:
                resultado_equipo = ('Victoria' if g1 > g2
                                    else 'Derrota' if g1 < g2
                                    else 'Empate')
            else:
                resultado_equipo = ('Victoria' if g2 > g1
                                    else 'Derrota' if g2 < g1
                                    else 'Empate')

            resultado.append({
                'jornada'         : f['Jornada'],
                'local'           : f['Equipo1'],
                'visitante'       : f['Equipo2'],
                'goles_local'     : g1,
                'goles_visitante' : g2,
                'resultado_equipo': resultado_equipo,
            })

        resultado.sort(key=lambda x: x['jornada'])
        return resultado

    def top(self, temporada: str, cantidad: int = 5,
            superior: bool = True) -> list:
        """Devuelve el top superior o inferior de la clasificacion"""
        t = self.tabla(temporada)
        if not t:
            return []
        if superior:
            return t[:cantidad]
        else:
            return t[-cantidad:][::-1]   # los ultimos de forma ascendente
