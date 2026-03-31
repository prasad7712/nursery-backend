"""Application runner script"""
import uvicorn
from dotenv import load_dotenv
from src.utilities.config_manager import config

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.get('server.host', '0.0.0.0'),
        port=config.get('server.port', 8000),
        reload=config.debug,
        log_level="info"
    )
