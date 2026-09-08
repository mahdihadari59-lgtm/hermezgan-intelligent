import logging
import sys
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[
logging.StreamHandler(sys.stdout),
logging.FileHandler('logs/app.log', encoding='utf-8')
]
)

logger = logging.getLogger("hermezgan")
