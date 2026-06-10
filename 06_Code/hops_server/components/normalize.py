# hops_server/components/normalize.py
import json
import numpy as np
import ghhops_server as hs
from utils.normalize import normalize_field


def register_field_normalize(hops: hs.Hops):
    @hops.component(
        "/field_normalize",
        name="FieldNormalize",
        description="Percentile normalize a flat field to [hmin, hmax]",
        inputs=[
            hs.HopsNumber( "F",     "F",    "Flattened field (row-major, length N*N)", access=hs.HopsParamAccess.LIST),
            hs.HopsNumber( "hmin",  "hmin", "Target min height (mm). Will be forced negative.", default=-3.0),
            hs.HopsNumber( "hmax",  "hmax", "Target max height (mm). Will be forced positive.", default=3.0),
            hs.HopsNumber( "p_lo",  "pLo",  "Low percentile",                                  default=5.0),
            hs.HopsNumber( "p_hi",  "pHi",  "High percentile",                                 default=95.0),
            hs.HopsBoolean("clamp", "clamp","Clamp output to [hmin, hmax]",                    default=True),
        ],
        outputs=[
            hs.HopsNumber("H",     "H",     "Normalized heights", access=hs.HopsParamAccess.LIST),
            hs.HopsString("stats", "stats", "Stats JSON"),
        ],
    )
    def field_normalize(F, hmin, hmax, p_lo, p_hi, clamp):
        try:
            F_arr = np.asarray(list(F), dtype=float)
        except Exception as e:
            return [], json.dumps({"ok": False, "reason": str(e)})

        if F_arr.size < 4:
            return [], json.dumps({"ok": False, "reason": "F empty or too small", "size": F_arr.size})

        out = normalize_field(
            F_arr,
            hmin=float(hmin), hmax=float(hmax),
            p_lo=float(p_lo), p_hi=float(p_hi),
            clamp=bool(clamp)
        )

        stats = json.dumps({
            "ok":   True,
            "size": F_arr.size,
            "in_min":  float(F_arr.min()),
            "in_max":  float(F_arr.max()),
            "out_min": float(out.min()),
            "out_max": float(out.max()),
            "p_lo": float(p_lo),
            "p_hi": float(p_hi),
        })

        return out.flatten().tolist(), stats