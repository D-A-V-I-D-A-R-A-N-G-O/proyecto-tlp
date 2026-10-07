# compiler.py
# Compilador universal para BrickScript (Versión Final con Soporte de PowerUps)

import sys
import re
import json

def lexer(codigo_fuente):
    codigo_fuente = re.sub(r'#.*', '', codigo_fuente)
    token_regex = r'\b[A-F0-9]{6}\b|\b[A-Z][A-Z0-9_]*\b|\d+|[\[\](),:]'
    tokens = re.findall(token_regex, codigo_fuente)
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.ast = {
            "tipo_juego": None, 
            "config": {}, 
            "shapes": {}, 
            "events": {}, 
            "shapes_color": {}, 
            "shapes_chance": {}, 
            "power_up": {}
        }

    def parse(self):
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            if token_actual == 'GAME_TYPE':
                self.parsear_tipo_juego()
            elif token_actual == 'GAME_GRID':
                self.parsear_grid()
            elif token_actual == 'DEFINE':
                self.parsear_shape()
            elif token_actual == 'GAME_COLOR':
                self.parsear_color()
            elif token_actual == 'CHANCE':
                self.parsear_probabilidad_shape()
            elif token_actual == 'COLOR':
                self.parsear_color_shape()
            elif token_actual == 'POWERUP':
                self.parsear_powerup()
            elif token_actual == 'ON':
                self.parsear_evento()
            else:
                self.posicion += 1
        return self.ast

    def consumir(self, token_esperado=None):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            if token_esperado and token != token_esperado:
                raise Exception("Error de sintaxis: Se esperaba '" + token_esperado + "' pero se encontro '" + token + "'")
            self.posicion += 1
            return token
        if token_esperado:
            raise Exception("Error de sintaxis: Se esperaba '" + token_esperado + "' pero se llego al final del archivo.")
        return None

    def parsear_tipo_juego(self):
        self.consumir('GAME_TYPE')
        self.ast['tipo_juego'] = self.consumir()

    def parsear_grid(self):
        self.consumir('GAME_GRID')
        self.consumir('(')
        ancho = int(self.consumir())
        self.consumir(',')
        alto = int(self.consumir())
        self.consumir(')')
        self.ast['config']['grid_size'] = [ancho, alto]

    def parsear_color(self):
        self.consumir('GAME_COLOR')
        self.ast['config']['color'] = self.consumir()

    def parsear_color_shape(self):
        self.consumir('COLOR')
        nombre_shape_color = self.consumir()
        self.consumir(':')
        color_shape = self.consumir()
        self.ast['shapes_color'][nombre_shape_color] = color_shape

    def parsear_probabilidad_shape(self):
        self.consumir('CHANCE')
        nombre_shape_chance = self.consumir()
        self.consumir(':')
        probabilidad = int(self.consumir())
        self.ast['shapes_chance'][nombre_shape_chance] = probabilidad

    def parsear_powerup(self):
        self.consumir('POWERUP')
        nombre_powerup = self.consumir()
        self.consumir(':')
        valor = int(self.consumir())
        self.ast['power_up'][nombre_powerup] = valor

    def parsear_shape(self):
        self.consumir('DEFINE')
        self.consumir('SHAPE')
        nombre_shape = self.consumir()
        self.consumir(':')
        estados = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] == 'STATE':
            self.consumir('STATE')
            self.consumir()
            self.consumir(':')
            matriz = []
            while self.posicion < len(self.tokens) and self.tokens[self.posicion] == '[':
                fila = []
                self.consumir('[')
                while self.tokens[self.posicion] != ']':
                    fila.append(int(self.consumir()))
                    if self.tokens[self.posicion] == ',': self.consumir(',')
                self.consumir(']')
                matriz.append(fila)
            estados.append(matriz)
        self.consumir('END')
        self.ast['shapes'][nombre_shape] = estados
        
        # Asignación segura por defecto
        self.ast['shapes_color'].setdefault(nombre_shape, "FFFF00")
        self.ast['shapes_chance'].setdefault(nombre_shape, 1)

    def parsear_evento(self):
        self.consumir('ON')
        nombre_evento = 'ON_' + self.consumir()
        self.consumir(':')
        acciones = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion] != 'END':
            verbo = self.consumir()
            
            if verbo == 'GAME_OVER':
                acciones.append({'accion': verbo, 'objeto': None, 'params': []})
                continue
            
            objeto = self.consumir()
            params = []
            if self.posicion < len(self.tokens) and self.tokens[self.posicion] == 'AT':
                self.consumir('AT')
                if self.tokens[self.posicion] == 'RANDOM':
                    params.append(self.consumir())
                else:
                    self.consumir('(')
                    x = int(self.consumir())
                    self.consumir(',')
                    y = int(self.consumir())
                    self.consumir(')')
                    params.append([x, y])
            elif self.posicion < len(self.tokens) and self.tokens[self.posicion] not in ['END', 'ON', 'DEFINE', 'SPAWN', 'MOVE', 'ROTATE', 'INCREASE_SCORE', 'SET_DIRECTION', 'GROW', 'GAME_OVER']:
                params.append(self.consumir())
            acciones.append({'accion': verbo, 'objeto': objeto, 'params': params})
        self.consumir('END')
        self.ast['events'][nombre_evento] = acciones

def generar_codigo(ast, archivo_salida):
    with open(archivo_salida, 'w') as f:
        json.dump(ast, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 compiler.py <archivo_entrada.brick>")
        sys.exit(1)
    archivo_entrada = sys.argv[1]
    archivo_salida = archivo_entrada.replace('.brick', '.json')
    print("Compilando " + archivo_entrada + "...")
    try:
        with open(archivo_entrada, 'r') as f:
            codigo = f.read()
        tokens = lexer(codigo)
        parser = Parser(tokens)
        ast = parser.parse()
        generar_codigo(ast, archivo_salida)
        print("Compilacion exitosa! Archivo de juego creado en " + archivo_salida)
    except Exception as e:
        print("\n!!! ERROR DE COMPILACION !!!")
        print(str(e))
        sys.exit(1)