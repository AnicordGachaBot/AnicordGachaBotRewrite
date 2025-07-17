import json
from os import getenv

from dotenv import load_dotenv

load_dotenv()

TOKEN: str = getenv('TOKEN')

WEBHOOK: str = getenv('WEBHOOK')

DATABASE_CRED: str = getenv('POSTGRES_URI')

OWNER_IDS: list[int] = json.loads(getenv('OWNER_IDS'))
