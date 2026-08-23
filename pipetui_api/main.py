from fastapi import FastAPI

from pipetui_api.routes import builds, pipelines, projects

app = FastAPI(title="PipeTUI API", version="0.1.0")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


app.include_router(projects.router)
app.include_router(pipelines.router)
app.include_router(builds.router)
