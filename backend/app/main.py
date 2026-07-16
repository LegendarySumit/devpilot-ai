from fastapi import FastAPI

from app.api import auth, build, debug, document, user

app = FastAPI(
    title="DevPilot AI API",
    version="0.1.0",
    description="Backend API for DevPilot AI: Build, Debug, Document.",
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(build.router, prefix="/api/build", tags=["Build"])
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])
app.include_router(document.router, prefix="/api/document", tags=["Document"])


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
