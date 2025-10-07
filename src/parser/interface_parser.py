from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class IParser(ABC):
    """Interface base para o parser usando ABC."""
    
    @abstractmethod
    def eat(self, expected_type: str, expected_value: Any = None) -> Any:
        """Verifica e consome o token atual se corresponder ao esperado."""
        pass

    @abstractmethod
    def parse(self):
        """Ponto de entrada principal do parser."""
        pass

    