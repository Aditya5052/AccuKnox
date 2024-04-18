from config import *

def scoresfn():
    scores = [{"student_id": i, "score": random.randint(50, 100)} for i in range(1, 16)]
    return scores

app = FastAPI()

@app.get('/health-check')
def health_check():
    return {'Status': "server up & running"}

@app.get("/scores-api")
def read_item():
    try:
        response = scoresfn()
        if (response is not None) :
            return response
        else:
            return "<h1> No Details found </h1>"
            
    except Exception as e:
        print(traceback.print_exc())
        logger.info(f"API Failed")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("scores:app", host="127.0.0.1", port=8000, log_level="info")