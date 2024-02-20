from ui import GenerateUI
from dotenv import load_dotenv
from src.models import init_db

load_dotenv()

if __name__ == "__main__":
    init_db()
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
