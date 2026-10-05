import uvicorn
import logging
from tavi.web.api import app
from tavi.core.config import settings

# Setup basic logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    uvicorn.run("tavi.web.api:app", host="127.0.0.1", port=8000, reload=True)
