
from tokens import (
    Token, ErrorLexico, PALABRAS_RESERVADAS,
    TK_CADENA, TK_TEMPORADA_VAL, TK_NUMERO, TK_ID_ARCHIVO,
    TK_FLAG_F, TK_FLAG_N, TK_FLAG_JI, TK_FLAG_JF,
    TK_LT, TK_GT, TK_ERROR,
)

MAPA_BANDERAS = {'-f':TK_FLAG_F, '-n':TK_FLAG_N, '-ji':TK_FLAG_JI, '-jf':TK_FLAG_JF}


class Lexer:
    def __init__(self, texto: str):
        self.texto    = texto
        self.tokens   = []
        self.errores  = []
        self.estado   = 0
        self.buffer   = ""
        self.linea    = 1
        self.columna  = 1
        self.i        = 0
        self.col_inicio   = 1
        self.linea_inicio = 1

#Funcionaes aux

    def es_letra(self, c):              return c.isalpha()
    def es_digito(self, c):             return c.isdigit()
    def es_inicio_identificador(self, c): return self.es_letra(c) or c == '_'
    def es_parte_identificador(self, c):  return self.es_letra(c) or self.es_digito(c) or c == '_'

#Estados del autoamata

    def S0(self, c):
        """Estado inicial. Decide rama segun primer caracter"""
        if c in (' ', '\t', '\r', '\n'):
            return

        if self.es_inicio_identificador(c):
            self.estado = 1
            self.buffer = c
            self.col_inicio = self.columna
            self.linea_inicio = self.linea

        elif self.es_digito(c):
            self.estado = 2
            self.buffer = c
            self.col_inicio = self.columna
            self.linea_inicio = self.linea

        elif c == '"':
            self.estado = 3
            self.buffer = ""
            self.col_inicio = self.columna
            self.linea_inicio = self.linea

        elif c == '-':
            self.estado = 4
            self.buffer = c
            self.col_inicio = self.columna
            self.linea_inicio = self.linea

        elif c == '<':
            self.tokens.append(Token(TK_LT, '<', self.linea, self.columna))

        elif c == '>':
            self.tokens.append(Token(TK_GT, '>', self.linea, self.columna))

        else:
            self.errores.append(ErrorLexico(c, self.linea, self.columna,
                                            f"Caracter no reconocido: '{c}'"))
            self.tokens.append(Token(TK_ERROR, c, self.linea, self.columna))

    def S1(self, c):
        """Acumulando letras, digitos o guiones bajos: ID_ARCHIVO o palabra reservada"""
        if self.es_parte_identificador(c):
            self.buffer += c
        else:
            tipo = PALABRAS_RESERVADAS.get(self.buffer.upper())
            if tipo:
                self.tokens.append(Token(tipo, self.buffer.upper(),
                                        self.linea_inicio, self.col_inicio))
            else:
                self.tokens.append(Token(TK_ID_ARCHIVO, self.buffer,
                                        self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
            self.i -= 1  # Retrocedemos para reanalizar el caracter actual en S0

    def S2(self, c):
        """Acumulando d"""
        if self.es_digito(c) and len(self.buffer) < 4:
            self.buffer += c
        elif c == '-' and len(self.buffer) == 4:
            self.buffer += c
            self.estado = 8
        else:
            if 1 <= len(self.buffer) <= 2:
                self.tokens.append(Token(TK_NUMERO, self.buffer,
                                        self.linea_inicio, self.col_inicio))
            else:
                self.errores.append(ErrorLexico(
                    self.buffer, self.linea_inicio, self.col_inicio,
                    f"Número fuera de rango: '{self.buffer}'"))
                self.tokens.append(Token(TK_ERROR, self.buffer,
                                        self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
            self.i -= 1  # Retrocedemos para reanalizar el caracter actual en S0

    def S3(self, c):
        """Leyendo contenido de CADENA"""
        if c == '"':
            self.tokens.append(Token(TK_CADENA, self.buffer,
                                    self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
        elif c == '\n':
            self.errores.append(ErrorLexico(
                f'"{self.buffer}', self.linea_inicio, self.col_inicio,
                f"Cadena no cerrada: '\"{self.buffer}'"))
            self.tokens.append(Token(TK_ERROR, self.buffer,
                                    self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
        else:
            self.buffer += c

    def S4(self, c):
        """Leyendo bandera"""
        if self.es_letra(c) and len(self.buffer) < 3:
            self.buffer += c
        else:
            tipo = MAPA_BANDERAS.get(self.buffer)
            if tipo:
                self.tokens.append(Token(tipo, self.buffer,
                                        self.linea_inicio, self.col_inicio))
            else:
                self.errores.append(ErrorLexico(
                    self.buffer, self.linea_inicio, self.col_inicio,
                    f"Bandera no reconocida: '{self.buffer}'"))
                self.tokens.append(Token(TK_ERROR, self.buffer,
                                        self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
            self.i -= 1  # Retrocedemos para reanalizar el caracter actual en S0

    def S8(self, c):
        """Primer digito del segundo año de TEMPORADA"""
        if self.es_digito(c):
            self.buffer += c
            self.estado = 9
        else:
            self._error_temp()

    def S9(self, c):
        """2do digito del 2do año de TEMPORADA"""
        if self.es_digito(c):
            self.buffer += c
            self.estado = 10
        else:
            self._error_temp()

    def S10(self, c):
        """3er digito del 2do año de TEMPORADA"""
        if self.es_digito(c):
            self.buffer += c
            self.estado = 11
        else:
            self._error_temp()

    def S11(self, c):
        """4to digito del 2do año de TEMPORADA"""
        if self.es_digito(c):
            self.buffer += c
            self.tokens.append(Token(TK_TEMPORADA_VAL, self.buffer,
                                    self.linea_inicio, self.col_inicio))
            self.buffer = ""
            self.estado = 0
        else:
            self._error_temp()

    def _error_temp(self):
        self.errores.append(ErrorLexico(
            self.buffer, self.linea_inicio, self.col_inicio,
            f"Formato de temporada invalido: '{self.buffer}' (se esperaba AAAA-AAAA)"))
        self.tokens.append(Token(TK_ERROR, self.buffer,
                                self.linea_inicio, self.col_inicio))
        self.buffer = ""
        self.estado = 0

#Metodo principal

    def analizar(self, cadena=None):
        if cadena is not None:
            self.texto = cadena

        self.linea=1; self.columna=1; self.buffer=""
        self.estado=0; self.tokens=[]; self.errores=[]; self.i=0

        despachador = {
            0:self.S0, 1:self.S1, 2:self.S2, 3:self.S3, 4:self.S4,
            8:self.S8, 9:self.S9, 10:self.S10, 11:self.S11,
        }

        while self.i < len(self.texto):
            c = self.texto[self.i]
            despachador[self.estado](c)
            if c == '\n':
                self.linea += 1; self.columna = 1
            else:
                self.columna += 1
            self.i += 1

        # Si el texto termina dentro de un estado foraza la aceptacion
        if self.estado == 1: self.S1(' ')
        if self.estado == 2: self.S2(' ')
        if self.estado == 4: self.S4(' ')

        return self.tokens, self.errores


if __name__ == '__main__':
    pruebas = [
        'RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA <1979-1980>',
        'GOLES LOCAL "Real Madrid" TEMPORADA <1979-1980>',
        'TOP SUPERIOR TEMPORADA <1979-1980> -n 3',
        'JORNADA 1 TEMPORADA <1979-1980> -f jornada_1',
        'PARTIDOS "Betis" TEMPORADA <1979-1980> -ji 1 -jf 5 -f partidos_betis',
        'TABLA TEMPORADA <1979-1980> -f tabla_1979',
        'ADIOS',
        'RESULTADO @invalido "sin cerrar TEMPORADA <19791980>',
    ]
    for entrada in pruebas:
        print(f'\n{"─"*60}\nEntrada: {entrada}')
        lex = Lexer(entrada)
        tokens, errores = lex.analizar()
        for t in tokens:
            print(f'  [{t.fila}:{t.columna}] {t.tipo:<20} → "{t.lexema}"')
        for e in errores:
            print(f'  ERROR [{e.fila}:{e.columna}] {e.descripcion}')
