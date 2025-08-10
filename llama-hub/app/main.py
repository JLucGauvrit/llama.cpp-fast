from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from models_catalog import CATALOG
from launcher import detect_capabilities, launch_llama, stop_llama

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    caps = detect_capabilities()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "caps": caps,
        "catalog": CATALOG
    })

@app.post("/launch")
async def launch(
    request: Request,
    repo_id: str = Form(...),
    filename: str = Form(...),
    mode: str = Form("cpu"),
    threads: int = Form(None),
    ctx_size: int = Form(None),
    n_gpu_layers: int = Form(None),
    batch_size: int = Form(None),
    ubatch_size: int = Form(None),
):
    use_gpu = (mode == "gpu")
    overrides = {}
    if threads: overrides["threads"] = threads
    if ctx_size: overrides["ctx_size"] = ctx_size
    if n_gpu_layers is not None: overrides["n_gpu_layers"] = n_gpu_layers
    if batch_size: overrides["batch_size"] = batch_size
    if ubatch_size: overrides["ubatch_size"] = ubatch_size

    hf_token = os.getenv("HF_TOKEN", None)
    info = launch_llama(repo_id, filename, use_gpu, overrides, hf_token)
    # retourne à la page d’accueil (affiche les infos)
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop")
def stop():
    info = stop_llama()
    return RedirectResponse(url="/", status_code=303)
