import logging


class Logger:
    def __init__(self, name = None, level = None, format = None, datefmt = None):
        # Define o nome do logger
        self.name = __name__ if name is None else name

        # Define o nível do logger
        self.level = logging.INFO if level is None else level

        # Define o formato do logger
        self.format = '[%(asctime)s] [%(levelname)s] %(message)s' if format is None else format

        # Define o formato da data do logger
        self.datefmt = '%Y-%m-%d %H:%M:%S' if datefmt is None else datefmt

        # Cria o logger
        self.logger = logging.getLogger(self.name)

        # Configura o logger
        self.logger.setLevel(self.level)

        # Cria o handler e formatter
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.format, self.datefmt)
        handler.setFormatter(formatter)

        # Remove handlers existentes para evitar duplicação
        self.logger.handlers = []
        
        # Adiciona o handler ao logger
        self.logger.addHandler(handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)

