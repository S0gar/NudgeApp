import logging


# насройка логирования происходит до импортирования модулей 
# для корректной работы логов в процессе импортирования

# Получаем корневой логгер
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Настраиваем обработчик и форматер
logger_handler = logging.FileHandler("python.log", mode='w')
logger_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
logger_handler.setFormatter(logger_formatter)

# Прикрепляем обработчик к корневому логгеру
root_logger.addHandler(logger_handler)

# локальный логгер
_logger = logging.getLogger(__name__)


from backend.bot import core


def main():
    _logger.info("запуск бота")
    core.start_bot()

if __name__ == "__main__":
    _logger.info("начало работы программы")
    main()
