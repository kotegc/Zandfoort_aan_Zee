# hops_server/components/kuramoto_sivashinsky.py
import json
import numpy as np
import ghhops_server as hs
from solvers.kuramoto_sivashinsky.solver import solve_kuramoto_sivashinsky


def register_kuramoto(hops: hs.Hops):
    @hops.component(
        "/kuramoto",
        name="Kuramoto–Sivashinsky (Poster Eq.)",
        description="u_t + ∇²u + ∇⁴u + 1/2|∇u|² = 0 (ETDRK4 stable phi-functions).",
        inputs=[
            hs.HopsInteger("N",       "N",    "Grid resolution (N×N).",          default=256),
            hs.HopsNumber( "L",       "L",    "Domain length.",                   default=200.0),
            hs.HopsNumber( "dt",      "dt",   "Time step (try 0.05–0.25).",       default=0.15),
            hs.HopsInteger("Steps",   "S",    "Number of steps.",                 default=1500),
            hs.HopsInteger("Seed",    "seed", "Random seed.",                     default=0),
            hs.HopsNumber( "InitAmp", "a0",   "Initial noise amplitude.",         default=0.1),
            hs.HopsBoolean("Dealias", "D",    "2/3 de-aliasing.",                 default=True),
        ],
        outputs=[
            hs.HopsNumber( "Field",  "F",  "Flattened field (length N*N).", access=hs.HopsParamAccess.LIST),
            hs.HopsInteger("N_out",  "No", "Output grid size N."),
            hs.HopsString( "Status", "S",  "OK or blowup reason."),
        ],
    )
    def kuramoto_component(N, L, dt, Steps, Seed, InitAmp, Dealias):
        u, status = solve_kuramoto_sivashinsky(
            N=int(N), L=float(L), dt=float(dt), steps=int(Steps),
            seed=int(Seed), init_amp=float(InitAmp), dealias=bool(Dealias)
        )
        return u.flatten().tolist(), int(N), status