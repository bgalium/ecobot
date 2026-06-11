"""Intérprete de instrucciones: ejecuta la secuencia de a un paso por frame."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.level import Level
    from core.robot import Robot

# Resultados posibles de una instrucción
RESULT_OK = "OK"
RESULT_WALL = "WALL"
RESULT_FELL = "FELL"
RESULT_PLANTED = "PLANTED"

# Deltas de movimiento para cada dirección
_DIRECTION_DELTA: dict[str, tuple[int, int]] = {
    "UP":    ( 0, -1),
    "DOWN":  ( 0,  1),
    "LEFT":  (-1,  0),
    "RIGHT": ( 1,  0),
}

# Giros a izquierda y derecha
_TURN_LEFT: dict[str, str] = {
    "UP": "LEFT", "LEFT": "DOWN", "DOWN": "RIGHT", "RIGHT": "UP",
}
_TURN_RIGHT: dict[str, str] = {
    "UP": "RIGHT", "RIGHT": "DOWN", "DOWN": "LEFT", "LEFT": "UP",
}


class Interpreter:
    """Ejecuta una lista de instrucciones paso a paso, sincronizado con el robot.

    Flujo de uso:
        interp = Interpreter(instructions)
        interp.start()                          # en handle_events al pulsar SPACE
        ...
        if interp.running and robot.is_idle():
            result = interp.step(robot, level)  # en update() cada frame
    """

    def __init__(self, instructions: list[str]) -> None:
        self.instructions: list[str] = instructions
        self._index: int = 0
        self.running: bool = False
        self.finished: bool = False

    # ------------------------------------------------------------------
    # Control público
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Inicia la ejecución desde la primera instrucción."""
        self._index = 0
        self.running = True
        self.finished = False

    def reset(self) -> None:
        """Vuelve al inicio sin borrar la lista de instrucciones."""
        self._index = 0
        self.running = False
        self.finished = False

    # ------------------------------------------------------------------
    # Ejecución
    # ------------------------------------------------------------------

    def step(self, robot: "Robot", level: "Level") -> str | None:
        """Ejecuta la instrucción actual y avanza el índice.

        Debe llamarse sólo cuando el robot haya terminado su animación
        (``robot.is_idle()`` es ``True``).

        Returns:
            El resultado de la instrucción ("OK", "WALL", "FELL",
            "PLANTED", …) o ``None`` si ya no hay más instrucciones.
        """
        if not self.running or self.finished:
            return None

        if self._index >= len(self.instructions):
            self.running = False
            self.finished = True
            return None

        instruction = self.instructions[self._index]
        self._index += 1

        result = self._execute(instruction, robot, level)

        # Si no quedan más instrucciones marcamos como terminado
        if self._index >= len(self.instructions):
            self.finished = True
            # No apagamos running aquí: game.py lo hará tras evaluar el resultado

        return result

    # ------------------------------------------------------------------
    # Implementación de instrucciones
    # ------------------------------------------------------------------

    def _execute(self, instruction: str, robot: "Robot", level: "Level") -> str:
        """Despacha la instrucción y devuelve su resultado."""
        if instruction == "MOVE":
            return self._move(robot, level)
        if instruction == "TURN_LEFT":
            robot.direction = _TURN_LEFT[robot.direction]
            return RESULT_OK
        if instruction == "TURN_RIGHT":
            robot.direction = _TURN_RIGHT[robot.direction]
            return RESULT_OK
        if instruction == "ACTION":
            return self._action(robot, level)
        # Instrucción desconocida: se ignora silenciosamente
        return RESULT_OK

    def _move(self, robot: "Robot", level: "Level") -> str:
        """Mueve el robot una celda hacia su dirección actual.

        Returns:
            "OK"   – movimiento completado.
            "WALL" – la celda destino es un muro o borde del mapa.
            "FELL" – la celda destino es un VOID (vacío / caída).
        """
        dcol, drow = _DIRECTION_DELTA[robot.direction]
        new_col = robot.col + dcol
        new_row = robot.row + drow

        # Fuera del mapa
        if not (0 <= new_col < level.cols and 0 <= new_row < level.rows):
            return RESULT_WALL

        target_tile = level.grid[new_row][new_col]

        if target_tile == "VOID":
            # El robot cae al vacío: actualiza posición para reflejar la caída
            robot.move_to(new_col, new_row)
            return RESULT_FELL

        if not level.is_walkable(new_col, new_row):
            return RESULT_WALL

        robot.move_to(new_col, new_row)
        return RESULT_OK

    def _action(self, robot: "Robot", level: "Level") -> str:
        """Ejecuta la acción ambiental del robot en su celda actual.

        Por ahora la única acción implementada es PLANT (plantar un árbol)
        cuando el robot se encuentra sobre una celda de tipo SOIL.
        """
        current_tile = level.grid[robot.row][robot.col]
        if current_tile == "SOIL":
            level.grid[robot.row][robot.col] = "TREE"
            return RESULT_PLANTED
        return RESULT_OK