"""Intérprete de instrucciones: ejecuta la secuencia de a un paso por frame."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.level import Level
    from core.robot import Robot


class Interpreter:
    """Ejecuta una lista de instrucciones paso a paso, sincronizado con el robot.

    Flujo de uso típico en game.py:
        interp = Interpreter(instructions)
        interp.start()                              # al pulsar ESPACIO
        ...
        if interp.running and not robot.moving:
            result = interp.step(robot, level)      # en update() cada frame
    """

    def __init__(self, instructions: list[str]) -> None:
        self.instructions: list[str] = instructions
        self._index: int = 0
        self.running: bool = False
        self.finished: bool = False

    @property
    def steps_used(self) -> int:
        return self._index

    # Control público

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

    # Ejecución

    def step(self, robot: "Robot", level: "Level") -> str | None:
        """Ejecuta la instrucción actual y avanza el índice.

        Debe llamarse sólo cuando ``robot.moving`` sea ``False``.

        Returns:
            "OK", "WALL", "FELL", "PLANTED", "COLLECTED", "NOTHING" …
            o ``None`` si ya no hay más instrucciones.
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

        # Marcar como terminado si se agotaron las instrucciones
        if self._index >= len(self.instructions):
            self.finished = True

        return result

    # Despacho de instrucciones
    def _execute(self, instruction: str, robot: "Robot", level: "Level") -> str:
        """Llama al método correcto del robot según la instrucción."""
        if instruction == "MOVE":
            return robot.move_forward(level)
        if instruction == "TURN_LEFT":
            return robot.turn_left()
        if instruction == "TURN_RIGHT":
            return robot.turn_right()
        if instruction == "ACTION":
            return robot.action(level)
        # Instrucción desconocida: se ignora
        return "OK"