from ui import GenerateUI
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    ui_generator = GenerateUI()
    ui_generator.launch_ui()
