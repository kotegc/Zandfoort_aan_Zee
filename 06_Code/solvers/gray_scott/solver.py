# solvers/gray_scott/solver.py
import numpy as np


def lap9(field, bc_mode):
    if bc_mode == 0:  # wrap
        c = field
        n  = np.roll(c, -1, 0)
        s  = np.roll(c,  1, 0)
        e  = np.roll(c, -1, 1)
        w  = np.roll(c,  1, 1)
        ne = np.roll(n, -1, 1)
        nw = np.roll(n,  1, 1)
        se = np.roll(s, -1, 1)
        sw = np.roll(s,  1, 1)
    else:  # reflect
        p  = np.pad(field, 1, mode="reflect")
        c  = p[1:-1, 1:-1]
        n  = p[0:-2, 1:-1]
        s  = p[2:,   1:-1]
        e  = p[1:-1, 2:  ]
        w  = p[1:-1, 0:-2]
        ne = p[0:-2, 2:  ]
        nw = p[0:-2, 0:-2]
        se = p[2:,   2:  ]
        sw = p[2:,   0:-2]

    return (
        0.05 * (ne + nw + se + sw) +
        0.20 * (n + s + e + w) -
        1.00 * c
    )


def seed_fields(N, seed):
    rng = np.random.default_rng(seed)
    U = np.ones((N, N))
    V = np.zeros((N, N))
    mask = rng.random((N, N)) < 0.05
    U[mask] = 0.0
    V[mask] = 1.0
    return U, V


def solve_gray_scott(N=256, steps=6000, dt=0.5,
                     Du=1.0, Dv=0.5, F=0.0367, K=0.0649,
                     seed=5, noise=0.05, bc_mode=0, clamp=False):
    """
    Returns the V field as an NxN numpy array.
    All parameters have defaults matching the original Hops component.
    """
    N = int(N)
    U, V = seed_fields(N, seed)

    if noise > 0:
        eps = noise * (np.random.random((N, N)) - 0.5)
        V += eps
        U -= eps

    for _ in range(steps):
        Lu = lap9(U, bc_mode)
        Lv = lap9(V, bc_mode)
        UVV = U * V * V
        U = U + dt * (Du * Lu - UVV + F * (1 - U))
        V = V + dt * (Dv * Lv + UVV - (F + K) * V)
        if clamp:
            U = np.clip(U, 0, 1)
            V = np.clip(V, 0, 1)

    return V