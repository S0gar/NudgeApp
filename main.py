from backend.bot import core
import logging


# получение пользовательского логгера и установка уровня логирования
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
logger_handler = logging.FileHandler(f"{__name__}.log", mode='w')
logger_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику 
logger_handler.setFormatter(logger_formatter)
# добавление обработчика к логгеру
_logger.addHandler(logger_handler)


def main():
    _logger.info("запуск бота")
    core.start_bot()

if __name__ == "__main__":
    _logger.info("начало работы программы")
    main()
