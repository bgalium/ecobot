"""Tests de core/transforms.py — traslación con coordenadas homogéneas."""
import numpy as np

from core.transforms import apply_translation, translation_matrix


def test_matriz_de_traslacion_es_3x3_homogenea():
    T = translation_matrix(2, -1)
    esperado = np.array([
        [1, 0, 2],
        [0, 1, -1],
        [0, 0, 1],
    ])
    assert T.shape == (3, 3)
    assert np.array_equal(T, esperado)


def test_aplicar_traslacion_mueve_el_punto():
    assert apply_translation(0, 3, 1, 0) == (1, 3)   # MOVE hacia RIGHT
    assert apply_translation(2, 2, 0, -1) == (2, 1)  # MOVE hacia UP


def test_traslacion_nula_es_identidad():
    assert apply_translation(4, 7, 0, 0) == (4, 7)
    assert np.array_equal(translation_matrix(0, 0), np.eye(3))


def test_composicion_de_traslaciones_suma_deltas():
    # T(1,2) @ T(3,4) == T(4,6) — concatenación de transformaciones
    compuesta = translation_matrix(1, 2) @ translation_matrix(3, 4)
    assert np.array_equal(compuesta, translation_matrix(4, 6))
