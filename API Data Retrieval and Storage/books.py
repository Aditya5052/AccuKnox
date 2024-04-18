from loguru import logger
import traceback
from fastapi import FastAPI
from fastapi import HTTPException
import uvicorn

def booksfn():
    books = [
        {"title": "Storytelling with Data", "author": "Cole Nussbaumer Knaflic", "publication_year": 2014},
        {"title": "Introduction to Probability", "author": "J. Laurie Snell", "publication_year": 1988},
        {"title": "Data Science for Dummies", "author": "Lillian Pierson", "publication_year": 2015}
    ]
    return books

app = FastAPI()

@app.get('/health-check')
def health_check():
    return {'Status': "server up & running"}

@app.get("/books-api")
def read_item():
    try:
        response = booksfn()
        if (response is not None) :
            return response
        else:
            return "<h1> No Details found </h1>"
            
    except Exception as e:
        print(traceback.print_exc())
        logger.info(f"API Failed")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("books:app", host="127.0.0.1", port=8000, log_level="info")