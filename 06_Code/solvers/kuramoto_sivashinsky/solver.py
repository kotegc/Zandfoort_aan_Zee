# solvers/kuramoto_sivashinsky/solver.py
import numpy as np


def _phi1(z):
    out = np.empty_like(z, dtype=np.complex128)
    small = np.abs(z) < 1e-8
    out[small] = 1.0 + z[small] / 2.0 + (z[small] ** 2) / 6.0
    out[~small] = np.expm1(z[~small]) / z[~small]
    return out


def _phi2(z):
    out = np.empty_like(z, dtype=np.complex128)
    small = np.abs(z) < 1e-6
    out[small] = 0.5 + z[small] / 6.0 + (z[small] ** 2) / 24.0
    out[~small] = (np.expm1(z[~small]) - z[~small]) / (z[~small] ** 2)
    return out


def _phi3(z):
    out = np.empty_like(z, dtype=np.complex128)
    small = np.abs(z) < 1e-4
    out[small] = (1.0 / 6.0) + z[small] / 24.0 + (z[small] ** 2) / 120.0
    out[~small] = (np.expm1(z[~small]) - z[~small] - 0.5 * z[~small] ** 2) / (z[~small] ** 3)
    return out


def solve_kuramoto_sivashinsky(N=256, L=200.0, dt=0.15, steps=1500,
                                seed=0, init_amp=0.1, dealias=True):
    """
    Kuramoto-Sivashinsky poster equation (ETDRK4, phi-functions):
        u_t + ∇²u + ∇⁴u + 1/2|∇u|² = 0

    Returns (u, status) where u is an NxN numpy array and
    status is "OK" or a blowup reason string.
    All parameters have defaults matching the original Hops component.
    """
    N = int(N)
    L = float(L)
    dt = float(dt)
    steps = int(steps)

    rng = np.random.default_rng(int(seed))

    dx = L / N
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, ky, indexing="xy")

    K2 = KX * KX + KY * KY
    K4 = K2 * K2
    Lk = K2 - K4

    E  = np.exp(dt * Lk)
    E2 = np.exp(0.5 * dt * Lk)

    mask = None
    if bool(dealias):
        kx_ind = np.fft.fftfreq(N) * N
        ky_ind = np.fft.fftfreq(N) * N
        KXi, KYi = np.meshgrid(kx_ind, ky_ind, indexing="xy")
        cutoff = N / 3.0
        mask = ((np.abs(KXi) <= cutoff) & (np.abs(KYi) <= cutoff)).astype(float)

    def Nhat(u_hat):
        ux = np.fft.ifft2(1j * KX * u_hat).real
        uy = np.fft.ifft2(1j * KY * u_hat).real
        n_hat = np.fft.fft2(-0.5 * (ux * ux + uy * uy))
        if mask is not None:
            n_hat *= mask
        return n_hat

    u = float(init_amp) * rng.standard_normal((N, N))
    u_hat = np.fft.fft2(u).astype(np.complex128)

    z  = dt * Lk
    z2 = 0.5 * z

    dtphi1z2 = dt * _phi1(z2)
    dtphi1z  = dt * _phi1(z)
    dt2phi2z = 2.0 * dt * _phi2(z)
    dtphi3z  = dt * _phi3(z)

    for i in range(steps):
        Nu = Nhat(u_hat)

        a  = E2 * u_hat + dtphi1z2 * Nu
        Na = Nhat(a)

        b  = E2 * u_hat + dtphi1z2 * Na
        Nb = Nhat(b)

        c  = E2 * a + dtphi1z2 * (2.0 * Nb - Nu)
        Nc = Nhat(c)

        u_hat = (E * u_hat) + (dtphi1z * Nu) + (dt2phi2z * (Na + Nb)) + (dtphi3z * Nc)
        u_hat[0, 0] = 0.0 + 0.0j

        if (i % 25) == 0:
            if not np.isfinite(u_hat).all():
                return np.zeros((N, N), dtype=float), f"BLOWUP: non-finite at step {i}"

    u = np.fft.ifft2(u_hat).real
    if not np.isfinite(u).all():
        return np.zeros((N, N), dtype=float), "BLOWUP: non-finite in ifft"

    return u, "OK"