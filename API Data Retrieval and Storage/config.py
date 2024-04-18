from loguru import logger
import traceback
from fastapi import FastAPI
from fastapi import HTTPException
import uvicorn
import requests
import json
import sqlite3