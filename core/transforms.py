"""Transformaciones 2D con coordenadas homogéneas (NumPy) — Unidad 4 del curso.

Un punto de la grilla (col, row) se representa como vector homogéneo
[col, row, 1]ᵀ. Trasladarlo es multiplicarlo por la matriz T(dx, dy).
Componer movimientos es multiplicar matrices: T(a,b) @ T(c,d) == T(a+c, b+d).
"""
import numpy as np


def translation_matrix(dx: int, dy: int) -> np.ndarray:
    """Matriz de traslación homogénea 3×3 T(dx, dy)."""
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1],
    ])


def apply_translation(col: int, row: int, dx: int, dy: int) -> tuple[int, int]:
    """Traslada el punto (col, row): calcula T(dx, dy) @ [col, row, 1]ᵀ."""
    punto = np.array([col, row, 1])
    trasladado = translation_matrix(dx, dy) @ punto
    return int(trasladado[0]), int(trasladado[1])
