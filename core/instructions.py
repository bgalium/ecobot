"""Instrucciones que EcoBot puede ejecutar"""


class Instruction:
    """Clase base
      Cada instrucción sabe cómo ejecutarse sobre el robot y el nivel"""

    def execute(self, robot, level) -> str:
        raise NotImplementedError


class MoveForward(Instruction):
    def execute(self, robot, level) -> str:
        return robot.move_forward(level)


class TurnLeft(Instruction):
    def execute(self, robot, level) -> str:
        return robot.turn_left()


class TurnRight(Instruction):
    def execute(self, robot, level) -> str:
        return robot.turn_right()


class Action(Instruction):
    def execute(self, robot, level) -> str:
        return robot.action(level)


INSTRUCTION_MAP = {
    "MOVE":       MoveForward,
    "TURN_LEFT":  TurnLeft,
    "TURN_RIGHT": TurnRight,
    "ACTION":     Action,
}
