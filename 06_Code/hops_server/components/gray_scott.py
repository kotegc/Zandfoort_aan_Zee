# hops_server/components/gray_scott.py
import json
import numpy as np
import ghhops_server as hs
from solvers.gray_scott.solver import solve_gray_scott


def register_gray_scott(hops: hs.Hops):
    @hops.component(
        "/gray_scott",
        name="GrayScott",
        description="Gray-Scott reaction diffusion (stable 9-point)",
        inputs=[
            hs.HopsBoolean("run",   "run",   "Run",              default=True),
            hs.HopsInteger("N",     "N",     "Grid resolution",  default=256),
            hs.HopsInteger("steps", "steps", "Iterations",       default=6000),
            hs.HopsNumber( "dt",    "dt",    "Time step",        default=0.5),
            hs.HopsNumber( "Du",    "Du",    "Diffusion U",      default=1.0),
            hs.HopsNumber( "Dv",    "Dv",    "Diffusion V",      default=0.5),
            hs.HopsNumber( "F",     "F",     "Feed",             default=0.0367),
            hs.HopsNumber( "K",     "K",     "Kill",             default=0.0649),
            hs.HopsInteger("seed",  "seed",  "Seed",             default=5),
            hs.HopsNumber( "noise", "noise", "Noise",            default=0.05),
            hs.HopsInteger("bc",    "bc",    "Boundary 0=wrap 1=reflect", default=0),
            hs.HopsBoolean("clamp", "clamp", "Clamp [0,1]",      default=False),
        ],
        outputs=[
            hs.HopsNumber("F",    "F", "Field", access=hs.HopsParamAccess.LIST),
            hs.HopsString("info", "info", "Info JSON"),
        ],
    )
    def gray_scott(run, N, steps, dt, Du, Dv, F, K, seed, noise, bc, clamp):
        if not run:
            return [], json.dumps({"ran": False})

        field = solve_gray_scott(
            N=int(N), steps=int(steps), dt=float(dt),
            Du=float(Du), Dv=float(Dv), F=float(F), K=float(K),
            seed=int(seed), noise=float(noise),
            bc_mode=int(bc), clamp=bool(clamp)
        )

        info = {
            "model": "gray_scott_9pt",
            "ran":   True,
            "min":   float(np.min(field)),
            "max":   float(np.max(field)),
            "mean":  float(np.mean(field)),
        }

        return field.reshape(-1).tolist(), json.dumps(info)