import numpy as np
from PIL import Image

from scipy.ndimage import gaussian_filter
from numpy.fft import fft2, fftshift
from skimage.feature import structure_tensor
from skimage.morphology import skeletonize
from skimage.filters import threshold_otsu
from skimage.util import img_as_float

import ghhops_server as hs


def _load_grayscale(path: str) -> np.ndarray:
    im = Image.open(path).convert("L")
    return img_as_float(np.asarray(im))


def _measurement_image(img: np.ndarray, detrend_sigma=60.0, grad_smooth_sigma=1.2):
    mu = float(np.mean(img))
    sig = float(np.std(img)) + 1e-8
    z = (img - mu) / sig

    bg = gaussian_filter(z, sigma=detrend_sigma)
    z = z - bg

    gy, gx = np.gradient(z)
    g = np.sqrt(gx * gx + gy * gy)

    g = gaussian_filter(g, sigma=grad_smooth_sigma)
    return g


def _dominant_wavelength_px(meas: np.ndarray):
    H, W = meas.shape

    window = np.outer(np.hanning(H), np.hanning(W))
    m = meas * window

    F = fftshift(fft2(m))
    P = np.abs(F) ** 2

    cy, cx = H // 2, W // 2
    yy, xx = np.indices((H, W))
    rr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2).astype(np.int32)

    radial_sum = np.bincount(rr.ravel(), weights=P.ravel())
    radial_cnt = np.bincount(rr.ravel())
    radial = radial_sum / np.maximum(radial_cnt, 1)

    radial[:4] = 0.0

    r_peak = int(np.argmax(radial))
    if r_peak <= 0:
        return float("nan")

    size = float(min(H, W))
    return float(size / r_peak)


def _orientation_and_anisotropy(meas: np.ndarray, sigma=3.0):
    Axx, Axy, Ayy = structure_tensor(meas, sigma=sigma)

    theta = 0.5 * np.arctan2(2.0 * Axy, (Axx - Ayy))

    trace = Axx + Ayy
    det = np.sqrt((Axx - Ayy) ** 2 + 4.0 * Axy ** 2)
    lam1 = 0.5 * (trace + det)
    lam2 = 0.5 * (trace - det)

    aniso = (lam1 - lam2) / (lam1 + lam2 + 1e-8)
    w = np.clip(aniso, 0.0, 1.0)

    c = np.sum(w * np.cos(2.0 * theta))
    s = np.sum(w * np.sin(2.0 * theta))
    theta_mean = 0.5 * np.arctan2(s, c)

    deg = float(np.degrees(theta_mean))
    if deg < -90: deg += 180
    if deg > 90: deg -= 180

    return deg, float(np.mean(w))


def _defect_density(meas: np.ndarray):
    t = threshold_otsu(meas)
    bw = meas > t
    sk = skeletonize(bw).astype(np.uint8)

    nbr = (
        np.roll(sk,1,0)+np.roll(sk,-1,0)+
        np.roll(sk,1,1)+np.roll(sk,-1,1)+
        np.roll(np.roll(sk,1,0),1,1)+
        np.roll(np.roll(sk,1,0),-1,1)+
        np.roll(np.roll(sk,-1,0),1,1)+
        np.roll(np.roll(sk,-1,0),-1,1)
    )

    endpoints = np.sum((sk==1)&(nbr==1))
    branchpts = np.sum((sk==1)&(nbr>=3))

    area = float(sk.size)
    scale = 1e6/area

    return float(endpoints*scale), float(branchpts*scale)


def register_sand_analysis(hops: hs.Hops):

    @hops.component(
        "/sand_analysis",
        name="Sand Analysis",
        description="Analyze sand ripple wavelength/orientation",
        inputs=[
            hs.HopsString("ImagePath", "P", "Full image path"),
            hs.HopsBoolean("ComputeDefects", "D", "compute defect density", default=False),
        ],
        outputs=[
            hs.HopsNumber("Wavelength_px", "lam", "dominant wavelength"),
            hs.HopsNumber("Orientation_deg", "theta", "orientation"),
            hs.HopsNumber("Anisotropy", "A", "anisotropy"),
            hs.HopsNumber("Endpoints", "E", "endpoint density"),
            hs.HopsNumber("Branchpoints", "B", "branch density"),
            hs.HopsString("Status", "S", "ok or error"),
        ],
    )
    def sand_analysis(imagepath, computedefects):
        try:
            img = _load_grayscale(str(imagepath))
            meas = _measurement_image(img)

            wl = _dominant_wavelength_px(meas)
            ang, aniso = _orientation_and_anisotropy(meas)

            if computedefects:
                e, b = _defect_density(meas)
            else:
                e, b = float("nan"), float("nan")

            return wl, ang, aniso, e, b, "ok"

        except Exception as err:
            msg = f"{type(err).__name__}: {err}"
            return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), msg
