from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers import consumption, dashboard, history, members, products, reviews
from app.scheduler import start_scheduler

app = FastAPI(title="900 Care — Suivi conso & avis")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(members.router)
app.include_router(products.router)
app.include_router(consumption.router)
app.include_router(reviews.router)
app.include_router(history.router)


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()
