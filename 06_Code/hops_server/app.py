# hops_server/app.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
import ghhops_server as hs

from components.swift_hohenberg       import register_swift_hohenberg
from components.kuramoto_sivashinsky  import register_kuramoto
from components.gray_scott            import register_gray_scott
from components.normalize             import register_field_normalize
from components.geom_mesh             import register_heightfield_mesh
from components.sand_analysis         import register_sand_analysis


def create_app():
    app  = Flask(__name__)
    hops = hs.Hops(app)

    register_swift_hohenberg(hops)
    register_kuramoto(hops)
    register_gray_scott(hops)
    register_field_normalize(hops)
    register_heightfield_mesh(hops)
    register_sand_analysis(hops)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)