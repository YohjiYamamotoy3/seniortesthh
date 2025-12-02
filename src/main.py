from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import auth, organizations, contacts, deals, tasks, activities, analytics

app = FastAPI(title="mini-crm", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(organizations.router, prefix="/api/v1", tags=["organizations"])
app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])
app.include_router(deals.router, prefix="/api/v1", tags=["deals"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(activities.router, prefix="/api/v1", tags=["activities"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])


@app.get("/")
def root():
    return {"message": "mini-crm api"}

