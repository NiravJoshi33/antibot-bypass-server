from fastapi import FastAPI  # type: ignore[import-not-found]
from app.constants.app_data import AppData

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "message": {
            "app_name": AppData.app_name,
            "app_version": AppData.app_version,
            "doc_path": AppData.doc_path,
        }
    }
