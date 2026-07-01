#PALABRAS RESERVADAS
TK_RESULTADO  = 'RESULTADO'
TK_VS         = 'VS'
TK_TEMPORADA  = 'TEMPORADA'
TK_JORNADA    = 'JORNADA'
TK_GOLES      = 'GOLES'
TK_LOCAL      = 'LOCAL'
TK_VISITANTE  = 'VISITANTE'
TK_TOTAL      = 'TOTAL'
TK_TABLA      = 'TABLA'
TK_PARTIDOS   = 'PARTIDOS'
TK_TOP        = 'TOP'
TK_SUPERIOR   = 'SUPERIOR'
TK_INFERIOR   = 'INFERIOR'
TK_ADIOS      = 'ADIOS'

#BANDERAS
TK_FLAG_F     = 'FLAG_F'
TK_FLAG_N     = 'FLAG_N'
TK_FLAG_JI    = 'FLAG_JI'
TK_FLAG_JF    = 'FLAG_JF'

#LITERALES
TK_CADENA         = 'CADENA'
TK_TEMPORADA_VAL  = 'TEMPORADA_VAL'
TK_NUMERO         = 'NUMERO'
TK_ID_ARCHIVO     = 'ID_ARCHIVO'

#DELIMITADORES
TK_LT   = 'LT'
TK_GT   = 'GT'

#ESPECIALES
TK_EOF   = 'EOF'
TK_ERROR = 'ERROR'

#PALABRAS RESERVADAS
PALABRAS_RESERVADAS = {
    'RESULTADO' : TK_RESULTADO,
    'VS'        : TK_VS,
    'TEMPORADA' : TK_TEMPORADA,
    'JORNADA'   : TK_JORNADA,
    'GOLES'     : TK_GOLES,
    'LOCAL'     : TK_LOCAL,
    'VISITANTE' : TK_VISITANTE,
    'TOTAL'     : TK_TOTAL,
    'TABLA'     : TK_TABLA,
    'PARTIDOS'  : TK_PARTIDOS,
    'TOP'       : TK_TOP,
    'SUPERIOR'  : TK_SUPERIOR,
    'INFERIOR'  : TK_INFERIOR,
    'ADIOS'     : TK_ADIOS,
}

class Token:
    #Representa un token que ha reconocido el analizador
    def __init__(self, tipo: str, lexema: str, fila: int, columna: int):
        self.tipo    = tipo
        self.lexema  = lexema
        self.fila    = fila
        self.columna = columna
    def __repr__(self) -> str:
        return (f"Token({self.tipo!r}, lexema={self.lexema!r}, "
                f"fila={self.fila}, col={self.columna})")
        
class ErrorLexico:
    #Registra un error lexico con su posicion y descripcion

    def __init__(self, lexema: str, fila: int, columna: int, descripcion: str):
        self.lexema      = lexema
        self.fila        = fila
        self.columna     = columna
        self.descripcion = descripcion

    def __repr__(self) -> str:
        return (f"ErrorLexico({self.lexema!r}, "
                f"fila={self.fila}, col={self.columna}: {self.descripcion})")