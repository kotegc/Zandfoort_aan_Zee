# solvers/swift_hohenberg/solver.py
import numpy as np


def _ridge_shape(phi, a2=0.22, a3=0.10):
    return np.sin(phi) + a2 * np.sin(2.0 * phi) + a3 * np.sin(3.0 * phi)


def solve_swift_hohenberg(N=256, L=40.0, steps=2000, dt=0.02,
                           wavelength=6.0, r=0.35, gamma=1.0,
                           seed=0, guard_clip=5.0,
                           ridge=True, a2=0.22, a3=0.10, gain=0.3):
    """
    Swift-Hohenberg (spectral, semi-implicit Euler):
        u_t = r*u - (k0² + ∇²)²u - gamma*u³

    Returns an NxN numpy array.
    All parameters have defaults matching the original Hops component.
    """
    N          = int(N)
    steps      = int(steps)
    L          = float(L)
    dt         = float(dt)
    wavelength = float(wavelength)
    r          = float(r)
    gamma      = float(gamma)
    seed       = int(seed)
    guard_clip = float(guard_clip)
    a2         = float(a2)
    a3         = float(a3)
    gain       = float(gain)

    dx = L / N
    k0 = 2.0 * np.pi / wavelength
    rng = np.random.default_rng(seed)

    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky)
    K2 = KX**2 + KY**2
    Lk = (k0**2 - K2)**2

    u = 0.01 * rng.standard_normal((N, N))

    for _ in range(steps):
        NL      = -gamma * (u**3)
        Uhat    = np.fft.fft2(u)
        rhs     = Uhat + dt * np.fft.fft2(r * u + NL)
        u       = np.fft.ifft2(rhs / (1.0 + dt * Lk)).real
        if guard_clip > 0.0:
            u = np.clip(u, -guard_clip, guard_clip)

    if ridge:
        u = _ridge_shape(u, a2=a2, a3=a3)

    return u * gain