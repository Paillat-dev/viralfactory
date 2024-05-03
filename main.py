import logging
from ui import launch
from src.models import init_db
from dotenv import load_dotenv


def main():
    copyright()
    credits()
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    init_db()
    launch()


if __name__ == "__main__":
    main()
