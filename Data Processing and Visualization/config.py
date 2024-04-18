import requests
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from loguru import logger
import traceback
from fastapi import FastAPI
from fastapi import HTTPException
import uvicorn
import random