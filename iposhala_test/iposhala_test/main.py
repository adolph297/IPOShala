from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from iposhala_test.api.routes.company import router as company_router
# add more routers like:
from iposhala_test.api.routes.ipos import router as ipos_router
from iposhala_test.api.routes.docs import router as docs_router

app = FastAPI(title="Iposhala API")

# CORS (frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can lock later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(company_router)
app.include_router(ipos_router)
app.include_router(docs_router)


@app.get("/")
def root():
    return {"status": "ok"}
