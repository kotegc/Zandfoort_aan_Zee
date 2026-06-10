# utils/normalize.py
import numpy as np


def normalize_field(F, hmin=-3.0, hmax=3.0, p_lo=5.0, p_hi=95.0, clamp=True):
    """
    Percentile normalize a field to [hmin, hmax].

    F       : array-like, 1D or NxN numpy array
    hmin    : target minimum (forced negative)
    hmax    : target maximum (forced positive)
    p_lo    : low percentile for robust scaling
    p_hi    : high percentile for robust scaling
    clamp   : clip output to [hmin, hmax]

    Returns a numpy array of the same shape as F.
    """
    F    = np.asarray(F, dtype=float)
    hmin = -abs(float(hmin))
    hmax =  abs(float(hmax))

    if hmin == 0.0 and hmax == 0.0:
        hmin, hmax = -5.0, 5.0

    v_lo = np.percentile(F, p_lo)
    v_hi = np.percentile(F, p_hi)

    # fall back to full range if percentile window is degenerate
    if abs(v_hi - v_lo) < 1e-12:
        v_lo = F.min()
        v_hi = F.max()

    # if still degenerate, return midpoint field
    if abs(v_hi - v_lo) < 1e-12:
        return np.full_like(F, 0.5 * (hmin + hmax))

    out = hmin + (F - v_lo) * (hmax - hmin) / (v_hi - v_lo)

    if clamp:
        out = np.clip(out, hmin, hmax)

    return out