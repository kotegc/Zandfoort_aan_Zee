# hops_server/components/swift_hohenberg.py
import json
import numpy as np
import ghhops_server as hs
from solvers.swift_hohenberg.solver import solve_swift_hohenberg

_LAST = {"F": None, "info": None}


def register_swift_hohenberg(hops: hs.Hops):
    @hops.component(
        "/swift_hohenberg",
        name="SwiftHohenberg",
        description="Swift–Hohenberg (spectral, semi-implicit) height field",
        inputs=[
            hs.HopsBoolean("run",        "run",  "Compute when True; otherwise return cached result", default=False),
            hs.HopsInteger("N",          "N",    "Grid resolution (NxN)",                            default=256),
            hs.HopsNumber( "L",          "L",    "Domain size (same units as wavelength)",            default=40.0),
            hs.HopsInteger("steps",      "steps","Time steps",                                        default=2000),
            hs.HopsNumber( "dt",         "dt",   "Time step",                                         default=0.02),
            hs.HopsNumber( "wavelength", "wl",   "Preferred wavelength (same units as L)",            default=6.0),
            hs.HopsNumber( "r",          "r",    "Linear growth rate",                                default=0.35),
            hs.HopsNumber( "gamma",      "g",    "Cubic saturation",                                  default=1.0),
            hs.HopsInteger("seed",       "seed", "RNG seed",                                          default=0),
            hs.HopsNumber( "guard_clip", "clip", "Clip magnitude (0 disables). Notebook: 5.0",        default=5.0),
            hs.HopsBoolean("ridge",      "ridge","Apply ridge shaping",                               default=True),
            hs.HopsNumber( "a2",         "a2",   "Ridge harmonic a2",                                 default=0.22),
            hs.HopsNumber( "a3",         "a3",   "Ridge harmonic a3",                                 default=0.10),
            hs.HopsNumber( "gain",       "gain", "Vertical gain",                                     default=0.3),
        ],
        outputs=[
            hs.HopsNumber("F",    "F",    "Flattened field (row-major, length N*N)", access=hs.HopsParamAccess.LIST),
            hs.HopsString("info", "info", "Info JSON string"),
        ],
    )
    def swift_hohenberg(run, N, L, steps, dt, wavelength, r, gamma,
                        seed, guard_clip, ridge, a2, a3, gain):
        if not run:
            if _LAST["F"] is None:
                return [], json.dumps({"note": "run is False and no cached result yet"})
            return _LAST["F"], _LAST["info"]

        u = solve_swift_hohenberg(
            N=int(N), L=float(L), steps=int(steps), dt=float(dt),
            wavelength=float(wavelength), r=float(r), gamma=float(gamma),
            seed=int(seed), guard_clip=float(guard_clip),
            ridge=bool(ridge), a2=float(a2), a3=float(a3), gain=float(gain)
        )

        F    = u.ravel(order="C").tolist()
        info = json.dumps({
            "model":      "swift_hohenberg",
            "ran":        True,
            "N":          int(N),
            "L":          float(L),
            "wavelength": float(wavelength),
            "r":          float(r),
            "gamma":      float(gamma),
            "seed":       int(seed),
            "min":        float(np.min(u)),
            "max":        float(np.max(u)),
        })

        _LAST["F"]    = F
        _LAST["info"] = info
        return F, info