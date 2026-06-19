from tokens import (
    Token, ErrorLexico,
    PALABRAS_RESERVADAS,
    TK_CADENA, TK_TEMPORADA_VAL, TK_NUMERO, TK_ID_ARCHIVO,
    TK_FLAG_F, TK_FLAG_N, TK_FLAG_JI, TK_FLAG_JF,
    TK_LT, TK_GT,
    TK_EOF, TK_ERROR,
)

class Lexer:
    #Analizador lexico para el lenguaje del proyectop
    
    def __init__(self, texto: str):
        self.texto    = texto          
        self.pos      = 0             
        self.fila     = 1              
        self.columna  = 1              
        self.tokens   = []             
        self.errores  = []  
        
    def _actual(self) -> str:
        #Devuelve el caracter en la posicion actual o '' si llego al fin
        return self.texto[self.pos] if self.pos < len(self.texto) else ''
    def _avanzar(self) -> str:
        #Consume el caracter actual y actualiza fila/columna y lo devuelve
        c = self.texto[self.pos]
        self.pos += 1
        if c == '\n':
            self.fila    += 1
            self.columna  = 1
        else:
            self.columna += 1
        return c
    def _peek(self, offset: int = 1) -> str:
        #Mira un caracter adelante sin consumirlo
        p = self.pos + offset
        return self.texto[p] if p < len(self.texto) else ''
    
    def analizar (self)-> tuple[list[Token], list[ErrorLexico]]:
        #Recorre todo el texto y devuelve tokens y errore
        while self.pos < len(self.texto):
            c = self._actual()

            if c in (' ', '\t', '\r', '\n'):
                self._avanzar()                    

            elif c == '"':
                self._leer_cadena()

            elif c == '-':
                self._leer_bandera()

            elif c == '<':
                fila, col = self.fila, self.columna
                self._avanzar()
                self.tokens.append(Token(TK_LT, '<', fila, col))

            elif c == '>':
                fila, col = self.fila, self.columna
                self._avanzar()
                self.tokens.append(Token(TK_GT, '>', fila, col))

            elif c.isdigit():
                self._leer_numero_o_temporada()

            elif c.isalpha() or c == '_':
                self._leer_palabra()

            else:
                # Caracter no reconocido es a un Error lexico
                fila, col = self.fila, self.columna
                self._avanzar()
                err = ErrorLexico(c, fila, col,
                                f"Caracter no reconocido: '{c}'")
                self.errores.append(err)
                self.tokens.append(Token(TK_ERROR, c, fila, col))

        return self.tokens, self.errores
    
    def _leer_cadena(self):
        #Lee una cadena entre comillas dobles
        
        fila, col = self.fila, self.columna
        self._avanzar()
        
        lexema = ''
        
        while self._actual() and self._actual() != '"':
            if self._actual() == '\n':
                # salto de linea por error
                err = ErrorLexico(
                    f'"{lexema}', fila, col,
                    f"Cadena no cerrada: falta \" al final de '\"{lexema}'"
                )
                self.errores.append(err)
                self.tokens.append(Token(TK_ERROR, lexema, fila, col))
                return
            lexema += self._avanzar()
 
        if self._actual() == '"':
            self._avanzar()   # consumir comilla de cierre "
            self.tokens.append(Token(TK_CADENA, lexema, fila, col))
        else:
            err = ErrorLexico(
                f'"{lexema}', fila, col,
                f"Cadena no cerrada: falta \" al final de '\"{lexema}'"
            )
            self.errores.append(err)
            self.tokens.append(Token(TK_ERROR, lexema, fila, col))
 
    def _leer_bandera(self):
        """Lee una bandera"""
        fila, col = self.fila, self.columna
        self._avanzar()   
        resto = ''

        # Leer hasta el primer espacio o fin de entrada
        while self._actual() and not self._actual().isspace():
            resto += self._avanzar()

        bandera = '-' + resto

        mapa = {
            '-f' : TK_FLAG_F,
            '-n' : TK_FLAG_N,
            '-ji': TK_FLAG_JI,
            '-jf': TK_FLAG_JF,
        }

        if bandera in mapa:
            self.tokens.append(Token(mapa[bandera], bandera, fila, col))
        else:
            err = ErrorLexico(bandera, fila, col,
                            f"Bandera no reconocida: '{bandera}'")
            self.errores.append(err)
            self.tokens.append(Token(TK_ERROR, bandera, fila, col))

    def _leer_numero_o_temporada(self):
        #Lee un numero de 1-2 digitos o una temporada AAAA-AAAA
        fila, col = self.fila, self.columna
        digitos = ''

        while self._actual().isdigit():
            digitos += self._avanzar()

        #Es inicio de temporada AAAA-AAAA?
        if (len(digitos) == 4
                and self._actual() == '-'
                and self._peek(0).isdigit() is False  # el '-' aun no fue consumido
                ):
            # verificar que tras el '-' vengan exactamente 4 digitos
            pos_guion = self.pos   
            guion = self._avanzar()  
            digitos2 = ''
            while self._actual().isdigit():
                digitos2 += self._avanzar()

            if len(digitos2) == 4:
                lexema = f"{digitos}-{digitos2}"
                self.tokens.append(Token(TK_TEMPORADA_VAL, lexema, fila, col))
            else:
                # No era temporada valida y reportar error
                lexema = f"{digitos}-{digitos2}"
                err = ErrorLexico(lexema, fila, col,
                                f"Formato de temporada invalido: '{lexema}' "
                                f"(se esperaba AAAA-AAAA)")
                self.errores.append(err)
                self.tokens.append(Token(TK_ERROR, lexema, fila, col))

        elif 1 <= len(digitos) <= 2:
            self.tokens.append(Token(TK_NUMERO, digitos, fila, col))

        else:
            # Numero con mas de 2 digitos y no es temporada
            err = ErrorLexico(digitos, fila, col,
                            f"Numero fuera de rango: '{digitos}' "
                            f"(se esperaba 1-2 digitos)")
            self.errores.append(err)
            self.tokens.append(Token(TK_ERROR, digitos, fila, col))

    def _leer_palabra(self):
        #Lee una secuencia de letras/digitos
        fila, col = self.fila, self.columna
        lexema = ''

        while self._actual() and (self._actual().isalnum() or self._actual() == '_'):
            lexema += self._avanzar()

        # Comparar en mayusculas para palabras reservadas
        tipo = PALABRAS_RESERVADAS.get(lexema.upper())

        if tipo:
            # Es palabra reservada 
            self.tokens.append(Token(tipo, lexema.upper(), fila, col))
        else:
            # No es reservada 
            self.tokens.append(Token(TK_ID_ARCHIVO, lexema, fila, col))

#  texto para prueba rapida
if __name__ == '__main__':
    pruebas = [
        'RESULTADO "Betis" VS "Rayo Vallecano" TEMPORADA <1979-1980>',
        'GOLES LOCAL "Real Madrid" TEMPORADA <1979-1980>',
        'TOP SUPERIOR TEMPORADA <1979-1980> -n 3',
        'JORNADA 1 TEMPORADA <1979-1980> -f jornada_1',
        'PARTIDOS "Betis" TEMPORADA <1979-1980> -ji 1 -jf 5 -f partidos_betis',
        'TABLA TEMPORADA <1979-1980> -f tabla_1979',
        'ADIOS',
        # en casos de ir con errores
        'RESULTADO "Betis VS @Rayo TEMPORADA <19791980>',
    ]

    for entrada in pruebas:
        print(f'\n{"─"*60}')
        print(f'Entrada: {entrada}')
        lex = Lexer(entrada)
        tokens, errores = lex.analizar()
        for t in tokens:
            print(f'  {t}')
        if errores:
            print('  ERRORES:')
            for e in errores:
                print(f'    {e}')