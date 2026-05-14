from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class FossilState(Enum):
    """Состояния жизненного цикла ископаемого."""
    BURIED = "В земле"
    EXCAVATED = "Выкопано"
    BROKEN = "Разрушено"
    ANALYZED = "Изучено"
    DISPLAYED = "На выставке"


class Difficulty(Enum):
    """Уровни сложности геологических формаций."""
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class JurassicPeriod:
    """Модель знаний о Юрском периоде."""
    knowledge_level: float = 0.0

    def add_knowledge(self, amount: float):
        """Увеличивает уровень знаний, но не больше 100%."""
        self.knowledge_level = min(100.0, self.knowledge_level + amount)

    def get_climate_info(self) -> str:
        """Возвращает информацию о климате в зависимости от уровня знаний."""
        if self.knowledge_level < 30:
            return "Данные о климате отсутствуют. Требуются дальнейшие исследования."
        elif self.knowledge_level < 70:
            return "Климат теплый и влажный, преобладают папоротниковые леса."
        else:
            return "Субтропический климат. Высокий уровень кислорода способствовал гигантизму."

    def to_dict(self) -> Dict[str, Any]:
        return {"knowledge_level": self.knowledge_level}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JurassicPeriod':
        return cls(knowledge_level=data.get("knowledge_level", 0.0))


@dataclass
class Fossil:
    """Модель ископаемой находки."""
    species: str
    bone_type: str
    state: FossilState = FossilState.BURIED
    integrity: float = 1.0

    def reduce_integrity(self, amount: float):
        """Уменьшает целостность находки (например, при неаккуратных раскопках)."""
        self.integrity = round(max(0.1, self.integrity - amount), 2)

    def change_state(self, new_state: FossilState):
        self.state = new_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "species": self.species,
            "bone_type": self.bone_type,
            "state": self.state.value,
            "integrity": self.integrity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fossil':
        return cls(
            species=data["species"],
            bone_type=data["bone_type"],
            state=FossilState(data["state"]),
            integrity=data["integrity"]
        )


@dataclass
class GeologicalFormation:
    """Локация для проведения полевых работ."""
    name: str
    difficulty: Difficulty
    buried_fossils: List[Fossil] = field(default_factory=list)

    def extract_fossil(self) -> Fossil:
        """Извлекает и возвращает первую доступную находку из слоя."""
        if not self.buried_fossils:
            raise ValueError("В данной формации не осталось ископаемых.")
        return self.buried_fossils.pop(0)

    def is_empty(self) -> bool:
        return len(self.buried_fossils) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "difficulty": self.difficulty.value,
            "buried_fossils": [f.to_dict() for f in self.buried_fossils]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeologicalFormation':
        return cls(
            name=data["name"],
            difficulty=Difficulty(data["difficulty"]),
            buried_fossils=[Fossil.from_dict(f) for f in data["buried_fossils"]]
        )


@dataclass
class Researcher:
    """Модель главного исследователя."""
    name: str
    energy: int = 100
    skill_level: int = 1
    inventory: List[Fossil] = field(default_factory=list)

    def spend_energy(self, amount: int):
        self.energy = max(0, self.energy - amount)

    def rest(self):
        self.energy = 100

    def add_skill(self, amount: int):
        self.skill_level += amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "energy": self.energy,
            "skill_level": self.skill_level,
            "inventory": [f.to_dict() for f in self.inventory]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Researcher':
        researcher = cls(
            name=data["name"],
            energy=data["energy"],
            skill_level=data["skill_level"]
        )
        researcher.inventory = [Fossil.from_dict(f) for f in data["inventory"]]
        return researcher


@dataclass
class DinosaurModel:
    """Музейный экспонат."""
    name: str
    species: str
    quality: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "species": self.species,
            "quality": self.quality
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DinosaurModel':
        return cls(
            name=data["name"],
            species=data["species"],
            quality=data["quality"]
        )


@dataclass
class Museum:
    """Модель управления музеем и финансами."""
    budget: float = 1000.0
    reputation: int = 0
    exhibits: List[DinosaurModel] = field(default_factory=list)

    def spend_budget(self, amount: float):
        self.budget -= amount

    def add_revenue(self, amount: float):
        self.budget += amount

    def increase_reputation(self, amount: int):
        self.reputation += amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "budget": self.budget,
            "reputation": self.reputation,
            "exhibits": [e.to_dict() for e in self.exhibits]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Museum':
        museum = cls(
            budget=data["budget"],
            reputation=data["reputation"]
        )
        museum.exhibits = [DinosaurModel.from_dict(e) for e in data["exhibits"]]
        return museum