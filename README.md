# Zandvoort aan Zee

Computational fabrication tools for PDE-driven surface textures and FDM/clay toolpath generation.

## Project Structure

    01_Docs/          — project documentation
    02_CAD_Working/   — Rhino/Grasshopper files
    03_CAD_Release/   — released CAD
    04_ID/            — visual assets and presentations
    05_Notes/         — research notes
    06_Code/          — all code (see below)

## 06_Code Structure

    hops_server/      — Grasshopper Hops server (Python 3.12)
    solvers/          — pure PDE solvers, numpy only
    utils/            — shared utilities
    notebooks/        — Jupyter notebooks for prototyping
    sketches/         — throwaway scripts

## Hops Server Setup

    cd 06_Code/hops_server
    py -3.12 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

Server runs on http://127.0.0.1:5000

## Solvers

- **Swift-Hohenberg** — spectral semi-implicit, stripe/labyrinth patterns
- **Kuramoto-Sivashinsky** — ETDRK4, turbulent pattern formation
- **Gray-Scott** — reaction-diffusion, spot and stripe patterns

## Status

Active development. Toolpath generation in progress.