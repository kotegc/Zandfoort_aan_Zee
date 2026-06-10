# components/geom_mesh.py
import json
import rhino3dm as r3d
import ghhops_server as hs

def register_heightfield_mesh(hops: hs.Hops):
    @hops.component(
        "/heightfield_mesh",
        name="HeightfieldMesh",
        description="Build a quad mesh from heights H on an NxN grid",
        inputs=[
            hs.HopsNumber("H", "H", "Heights list (len must be N*N)", access=hs.HopsParamAccess.LIST),
            hs.HopsInteger("N", "N", "Grid resolution (NxN)", default=256),
            hs.HopsNumber("tile_mm", "L", "Tile size in mm", default=200.0),
            hs.HopsBoolean("center", "center", "Center tile at origin", default=True),
        ],
        outputs=[
            hs.HopsMesh("M", "M", "Mesh"),
            hs.HopsString("info", "info", "Info JSON"),
        ],
    )
    def heightfield_mesh(H, N, tile_mm, center):
        try:
            H_list = [float(x) for x in list(H)]
        except:
            return None, json.dumps({"ok": False, "reason": "H not iterable", "H_type": str(type(H))})

        N = int(N)
        tile_mm = float(tile_mm)
        center = bool(center)

        if N <= 1 or len(H_list) != N * N:
            return None, json.dumps({"ok": False, "reason": "len(H) != N*N", "N": N, "lenH": len(H_list)})

        step = tile_mm / float(N - 1)
        x0 = -0.5 * tile_mm if center else 0.0
        y0 = -0.5 * tile_mm if center else 0.0

        m = r3d.Mesh()

        # vertices
        for i in range(N):
            y = y0 + i * step
            base = i * N
            for j in range(N):
                x = x0 + j * step
                z = H_list[base + j]
                m.Vertices.Add(x, y, z)

        # quad faces
        for i in range(N - 1):
            row = i * N
            row_next = (i + 1) * N
            for j in range(N - 1):
                a = row + j
                b = row + j + 1
                c = row_next + j + 1
                d = row_next + j
                m.Faces.AddFace(a, b, c, d)

        m.Normals.ComputeNormals()

        info = {"ok": True, "N": N, "tile_mm": tile_mm, "step_mm": step}
        return m, json.dumps(info)
