from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import urllib.parse
import uvicorn

from services import SimulationCore, ExcavationService, ResearchService, SimulationError, MuseumService, GameConfig
from models import FossilState

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

core = SimulationCore()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, error: str = None, message: str = None):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "core": core,
        "fossil_states": FossilState,
        "error": error,
        "message": message
    })


@app.get("/excavate", response_class=HTMLResponse)
async def excavate_page(request: Request):
    return templates.TemplateResponse("excavate.html", {
        "request": request,
        "formations": core.formations
    })


@app.post("/excavate")
async def excavate_action(formation_id: int = Form(...)):
    try:
        formation = core.formations[formation_id]
        result_msg = ExcavationService.excavate(core.researcher, formation)
        safe_msg = urllib.parse.quote(result_msg)
        return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)
    except (SimulationError, IndexError) as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)


@app.post("/research/{fossil_idx}")
async def research_action(fossil_idx: int):
    try:
        fossil = core.researcher.inventory[fossil_idx]
        result_msg = ResearchService.analyze_fossil(core.researcher, fossil, core.period)
        safe_msg = urllib.parse.quote(result_msg)
        return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)


@app.post("/museum/create/{fossil_idx}")
async def create_model_action(fossil_idx: int):
    try:
        result_msg = MuseumService.create_model(core.museum, core.researcher, [fossil_idx], core.period)
        safe_msg = urllib.parse.quote(result_msg)
        return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)


@app.post("/exhibition")
async def exhibition_action():
    try:
        result_msg = MuseumService.run_exhibition(core.museum)
        safe_msg = urllib.parse.quote(result_msg)
        return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)
    except Exception as e:
        error_msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)


@app.post("/rest")
async def rest_action():
    core.researcher.rest()
    safe_msg = urllib.parse.quote("Энергия восстановлена до 100%.")
    return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)


@app.post("/save")
async def save_game():
    core.save()
    safe_msg = urllib.parse.quote("Прогресс успешно сохранен!")
    return RedirectResponse(url=f"/?message={safe_msg}", status_code=303)


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    climate_info = core.period.get_climate_info()
    return templates.TemplateResponse("help.html", {
        "request": request,
        "climate_info": climate_info,
        "core": core,
        "config": GameConfig
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)