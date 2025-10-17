"""Общий хаб настроек. Здесь они подготавливаются и отсюда импортируются для использования в модулях."""

import yaml


class BaseConfig:
    def __init__(self, config_path=None):
        if config_path:
            self.process(config_path)

    def process(self, path):
        """Итерируемся по конфигу и хаваем параметры. Каждый словарь превращается в новую ноду."""

        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        self.devour(self, config_data)

    @staticmethod
    def devour(root, data):
        """Рекурсивно хаваем вложенные словари из конфига."""

        for node, value in data.items():
            if isinstance(value, dict):
                setattr(root, node, ConfigNode())

                child_node = getattr(root, node)
                child_node.devour(child_node, value)
            else:
                setattr(root, node, value)


class ConfigNode(BaseConfig):
    """Нода конфига, хранящая следующие ноды или значения в ней."""


qdrant_config = BaseConfig("configs/qdrant.yaml")
