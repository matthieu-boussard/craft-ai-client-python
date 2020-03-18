import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
CRAFT_CFG = {"token": os.environ.get("CRAFT_TOKEN")}
