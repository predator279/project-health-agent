from abc import ABC, abstractmethod
from src.schema import ProjectPlan

class BaseAdapter(ABC):
    @abstractmethod
    def parse(self, file_path: str, project_id: str) -> ProjectPlan:
        """Parses the input file and returns a canonical ProjectPlan."""
        pass
