from dataclasses import dataclass
from tokens import (
    TK_RESULTADO, TK_VS, TK_TEMPORADA, TK_JORNADA, TK_GOLES,
    TK_LOCAL, TK_VISITANTE, TK_TOTAL, TK_TABLA, TK_PARTIDOS,
    TK_TOP, TK_SUPERIOR, TK_INFERIOR, TK_ADIOS,
    TK_FLAG_F, TK_FLAG_N, TK_FLAG_JI, TK_FLAG_JF,
    TK_CADENA, TK_TEMPORADA_VAL, TK_NUMERO, TK_ID_ARCHIVO,
    TK_LT, TK_GT, TK_ERROR,
)


@dataclass
class ErrorSintactico:
    """Registra un error sintactico igual que ErrorLexico pero para la gramatica"""
    tipo: str
    descripcion: str
    linea: int
    columna: int
    token_recibido: str = ''
    token_esperado: str = ''


class Parser:
    """Analizador sintactico descendente recursivo para LigaBot"""

    def __init__(self, tokens: list):
        # Filtrar tokens de error antes de parsear
        self.tokens   = [t for t in tokens if t.tipo != TK_ERROR]
        self.posicion = 0
        self.errores  = []
        self.comando  = {}

#Utilidades

    def token_actual(self):
        """Devuelve el token actual sin consumirlo"""
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None

    def avanzar(self):
        """Avanza al siguiente token y devuelve el actual"""
        t = self.token_actual()
        if t:
            self.posicion += 1
        return t

    def consumir(self, tipo_esperado: str):
        """Verifica que el token actual sea del tipo esperado y lo consume"""
        actual = self.token_actual()

        if actual and actual.tipo == tipo_esperado:
            self.avanzar()
            return actual

        # Error: token inesperado
        recibido = actual.tipo    if actual else 'FIN DE ENTRADA'
        fila     = actual.fila   if actual else 0
        col      = actual.columna if actual else 0

        self.errores.append(ErrorSintactico(
            tipo           = 'Sintactico',
            descripcion    = f"Se esperaba '{tipo_esperado}' pero se recibio '{recibido}'",
            linea          = fila,
            columna        = col,
            token_recibido = recibido,
            token_esperado = tipo_esperado,
        ))
        return None

    def getLexema(self):
        """Devuelve el lexema del token actual"""
        t = self.token_actual()
        return t.lexema if t else ''

#Producciones aux

    def _leer_temporada(self):
        """Produccion: LT TEMPORADA_VAL GT:  devuelve el valor AAAA-AAAA"""
        self.consumir(TK_LT)
        t = self.consumir(TK_TEMPORADA_VAL)
        self.consumir(TK_GT)
        return t.lexema if t else None

    def _leer_cadena(self):
        """Produccion: TK_CADENA: devuelve el nombre del equipo"""
        t = self.consumir(TK_CADENA)
        return t.lexema if t else None

    def _leer_numero(self):
        """Produccion: TK_NUMERO: devuelve el numero como entero"""
        t = self.consumir(TK_NUMERO)
        return int(t.lexema) if t else None

    def _leer_id(self):
        """Produccion: TK_ID_ARCHIVO: devuelve el nombre de archivo"""
        t = self.consumir(TK_ID_ARCHIVO)
        return t.lexema if t else None

    def _leer_flag_f(self):
        """Produccion opcional: FLAG_F ID_ARCHIVO"""
        if self.token_actual() and self.token_actual().tipo == TK_FLAG_F:
            self.avanzar()
            return self._leer_id()
        return None

    def _leer_flag_n(self):
        """Produccion opcional: FLAG_N NUMERO"""
        if self.token_actual() and self.token_actual().tipo == TK_FLAG_N:
            self.avanzar()
            return self._leer_numero()
        return None

    def _leer_flag_ji(self):
        """Produccion opcional: FLAG_JI NUMERO"""
        if self.token_actual() and self.token_actual().tipo == TK_FLAG_JI:
            self.avanzar()
            return self._leer_numero()
        return None

    def _leer_flag_jf(self):
        """Produccion opcional: FLAG_JF NUMERO"""
        if self.token_actual() and self.token_actual().tipo == TK_FLAG_JF:
            self.avanzar()
            return self._leer_numero()
        return None

#Producciones

    def _cmd_resultado(self):
        """RESULTADO "Local" VS "Visitante" TEMPORADA <AAAA-AAAA>"""
        local     = self._leer_cadena()
        self.consumir(TK_VS)
        visitante = self._leer_cadena()
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        self.comando = {
            'tipo': 'RESULTADO',
            'local': local,
            'visitante': visitante,
            'temporada': temporada,
        }

    def _cmd_jornada(self):
        """JORNADA N TEMPORADA <AAAA-AAAA> [-f nombre]"""
        numero    = self._leer_numero()
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        archivo   = self._leer_flag_f()
        self.comando = {
            'tipo': 'JORNADA',
            'jornada': numero,
            'temporada': temporada,
            'archivo': archivo,
        }

    def _cmd_goles(self):
        """GOLES (LOCAL|VISITANTE|TOTAL) "Equipo" TEMPORADA <AAAA-AAAA>"""
        t = self.token_actual()
        if not t or t.tipo not in (TK_LOCAL, TK_VISITANTE, TK_TOTAL):
            fila = t.fila   if t else 0
            col  = t.columna if t else 0
            self.errores.append(ErrorSintactico(
                tipo           = 'Sintactico',
                descripcion    = "Se esperaba LOCAL, VISITANTE o TOTAL despues de GOLES",
                linea          = fila,
                columna        = col,
                token_recibido = t.tipo if t else 'FIN',
                token_esperado = 'LOCAL | VISITANTE | TOTAL',
            ))
            return
        subtipo   = self.avanzar().tipo
        equipo    = self._leer_cadena()
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        self.comando = {
            'tipo': 'GOLES',
            'subtipo': subtipo,
            'equipo': equipo,
            'temporada': temporada,
        }

    def _cmd_tabla(self):
        """TABLA TEMPORADA <AAAA-AAAA> [-f nombre]"""
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        archivo   = self._leer_flag_f()
        self.comando = {
            'tipo': 'TABLA',
            'temporada': temporada,
            'archivo': archivo,
        }

    def _cmd_partidos(self):
        """PARTIDOS "Equipo" TEMPORADA <AAAA-AAAA> [-f nombre] [-ji N] [-jf N]"""
        equipo    = self._leer_cadena()
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        archivo = ji = jf = None
        # Las banderas opcionales pueden venir en cualquier orden
        while self.token_actual():
            tipo_act = self.token_actual().tipo
            if tipo_act == TK_FLAG_F:
                archivo = self._leer_flag_f()
            elif tipo_act == TK_FLAG_JI:
                ji = self._leer_flag_ji()
            elif tipo_act == TK_FLAG_JF:
                jf = self._leer_flag_jf()
            else:
                break
        self.comando = {
            'tipo': 'PARTIDOS',
            'equipo': equipo,
            'temporada': temporada,
            'archivo': archivo,
            'ji': ji,
            'jf': jf,
        }

    def _cmd_top(self):
        """TOP (SUPERIOR|INFERIOR) TEMPORADA <AAAA-AAAA> [-n N]"""
        t = self.token_actual()
        if not t or t.tipo not in (TK_SUPERIOR, TK_INFERIOR):
            fila = t.fila   if t else 0
            col  = t.columna if t else 0
            self.errores.append(ErrorSintactico(
                tipo           = 'Sintactico',
                descripcion    = "Se esperaba SUPERIOR o INFERIOR despues de TOP",
                linea          = fila,
                columna        = col,
                token_recibido = t.tipo if t else 'FIN',
                token_esperado = 'SUPERIOR | INFERIOR',
            ))
            return
        subtipo   = self.avanzar().tipo
        self.consumir(TK_TEMPORADA)
        temporada = self._leer_temporada()
        cantidad  = self._leer_flag_n()
        self.comando = {
            'tipo': 'TOP',
            'subtipo': subtipo,
            'temporada': temporada,
            'cantidad': cantidad or 5,   # default si no hay -n
        }

    def _cmd_adios(self):
        """ADIOS - sin parametros"""
        self.comando = {'tipo': 'ADIOS'}

#Punto de la entrada principal

    def inicio(self):
        """Produccion raiz de la gramatica // decide que comando parsear"""
        if not self.tokens:
            self.errores.append(ErrorSintactico(
                tipo        = 'Sintactico',
                descripcion = 'Entrada vacia // no se encontraron tokens validos',
                linea=0, columna=0,
            ))
            return

        primero = self.token_actual()

        if primero.tipo == TK_RESULTADO:
            self.avanzar(); self._cmd_resultado()
        elif primero.tipo == TK_JORNADA:
            self.avanzar(); self._cmd_jornada()
        elif primero.tipo == TK_GOLES:
            self.avanzar(); self._cmd_goles()
        elif primero.tipo == TK_TABLA:
            self.avanzar(); self._cmd_tabla()
        elif primero.tipo == TK_PARTIDOS:
            self.avanzar(); self._cmd_partidos()
        elif primero.tipo == TK_TOP:
            self.avanzar(); self._cmd_top()
        elif primero.tipo == TK_ADIOS:
            self.avanzar(); self._cmd_adios()
        else:
            self.errores.append(ErrorSintactico(
                tipo           = 'Sintactico',
                descripcion    = f"Comando desconocido: '{primero.lexema}'",
                linea          = primero.fila,
                columna        = primero.columna,
                token_recibido = primero.tipo,
                token_esperado = 'RESULTADO|JORNADA|GOLES|TABLA|PARTIDOS|TOP|ADIOS',
            ))

# Verificar que no queden tokens sin consumir
        if self.token_actual() and not self.errores:
            t = self.token_actual()
            self.errores.append(ErrorSintactico(
                tipo           = 'Sintactico',
                descripcion    = f"Token inesperado al final: '{t.lexema}'",
                linea          = t.fila,
                columna        = t.columna,
                token_recibido = t.tipo,
                token_esperado = 'FIN DE COMANDO',
            ))

    def analizar(self):
        """Ejecuta el analisis sintactico completo"""
        self.inicio()
        return self.comando, self.errores

    def imprimir_errores(self):
        """Imprime los errores en consola (para pruebas)"""
        if not self.errores:
            print("No hay errores sintacticos.")
            return
        for e in self.errores:
            print(f"[{e.fila}:{e.columna}] {e.tipo}: {e.descripcion}")
            print(f"  Recibido: {e.token_recibido}  |  Esperado: {e.token_esperado}")


#prueba rapidoa
if __name__ == '__main__':
    from lexer import Lexer

    pruebas = [
        ('OK',  'RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA <1979-1980>'),
        ('OK',  'GOLES LOCAL "Betis" TEMPORADA <1979-1980>'),
        ('OK',  'TOP SUPERIOR TEMPORADA <1979-1980> -n 3'),
        ('OK',  'JORNADA 1 TEMPORADA <1979-1980> -f jornada_1'),
        ('OK',  'PARTIDOS "Betis" TEMPORADA <1979-1980> -ji 1 -jf 5 -f partidos_betis'),
        ('OK',  'TABLA TEMPORADA <1979-1980> -f tabla_1979'),
        ('OK',  'ADIOS'),
        ('ERR', 'RESULTADO "Betis" TEMPORADA <1979-1980>'),  # falta VS y visitante
        ('ERR', 'GOLES "Betis" TEMPORADA <1979-1980>'),      # falta LOCAL/VISITANTE/TOTAL
    ]

    for esperado, entrada in pruebas:
        print(f'\n{"─"*60}')
        print(f'Entrada: {entrada}')
        lex = Lexer(entrada)
        tokens, _ = lex.analizar()
        p = Parser(tokens)
        cmd, errores = p.analizar()
        if errores:
            print(f'Errores sintacticos:')
            for e in errores:
                print(f'     [{e.fila}:{e.columna}] {e.descripcion}')
        else:
            print(f'Comando reconocido: {cmd}')
