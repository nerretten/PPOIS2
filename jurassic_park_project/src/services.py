import json
import os
import random
from dataclasses import dataclass
from typing import List, Optional, Dict

from src.models import (
    Researcher,
    GeologicalFormation,
    Fossil,
    Museum,
    JurassicPeriod,
    DinosaurModel,
    FossilState,
    Difficulty
)


@dataclass(frozen=True)
class GameConfig:
    """Централизованное хранилище настроек баланса и стоимостей."""

    # --- Стоимость действий (Энергия/Бюджет) ---
    EXCAVATION_ENERGY_COST: int = 10
    RESEARCH_ENERGY_COST: int = 5
    MODEL_CREATION_BUDGET_COST: float = 300.0

    # --- Параметры раскопок (Шансы и урон) ---
    EXCAVATION_BASE_CHANCE: int = 60
    SKILL_BONUS_MULTIPLIER: int = 5
    DIFFICULTY_PENALTY_MULTIPLIER: int = 15
    MIN_SUCCESS_CHANCE: int = 10
    MAX_SUCCESS_CHANCE: int = 90
    MAX_DAMAGE_RATIO_HARD: float = 0.2  # Максимальный урон для сложных пород

    # --- Параметры исследования ---
    KNOWLEDGE_BASE_MULTIPLIER: float = 5.0
    SKILL_GAIN_PER_RESEARCH: int = 1

    # --- Параметры создания макета (Веса формулы) ---
    QUALITY_INTEGRITY_WEIGHT: float = 0.6
    QUALITY_KNOWLEDGE_WEIGHT: float = 0.4

    # --- Параметры выставки (Доход) ---
    REVENUE_PER_QUALITY_POINT: float = 5.0
    MIN_RANDOM_REVENUE: int = 50
    MAX_RANDOM_REVENUE: int = 150


# --- Исключения ---

class SimulationError(Exception):
    """Базовый класс пользовательских исключений."""
    pass


class ResourceError(SimulationError):
    """Исключение: нехватка энергии или бюджета."""
    pass


class WorkflowError(SimulationError):
    """Исключение: нарушение бизнес-логики."""
    pass


# --- Сервисы ---

class PersistenceService:
    """Сервис для сохранения и загрузки состояния системы."""
    FILE_PATH = "data/simulation_state.json"

    @staticmethod
    def save_state(data: Dict):
        os.makedirs("data", exist_ok=True)
        with open(PersistenceService.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_state() -> Optional[Dict]:
        if not os.path.exists(PersistenceService.FILE_PATH):
            return None
        try:
            with open(PersistenceService.FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None


class ExcavationService:
    """Логика проведения полевых раскопок."""

    @staticmethod
    def excavate(researcher: Researcher, formation: GeologicalFormation) -> str:
        cost = GameConfig.EXCAVATION_ENERGY_COST

        if researcher.energy < cost:
            raise ResourceError(f"Недостаточно энергии для экспедиции. Необходимо {cost} ед.")

        if formation.is_empty():
            raise WorkflowError("Данная формация полностью исследована.")

        researcher.spend_energy(cost)

        # Расчет шанса успеха
        base_chance = GameConfig.EXCAVATION_BASE_CHANCE
        skill_bonus = researcher.skill_level * GameConfig.SKILL_BONUS_MULTIPLIER
        difficulty_penalty = formation.difficulty.value * GameConfig.DIFFICULTY_PENALTY_MULTIPLIER

        success_chance = max(
            GameConfig.MIN_SUCCESS_CHANCE,
            min(GameConfig.MAX_SUCCESS_CHANCE, base_chance + skill_bonus - difficulty_penalty)
        )

        roll = random.randint(1, 100)

        if roll <= success_chance:
            fossil = formation.extract_fossil()
            fossil.change_state(FossilState.EXCAVATED)

            # Шанс повреждения только для сложных пород
            damage = 0.0
            if formation.difficulty != Difficulty.EASY:
                damage = random.uniform(0.0, GameConfig.MAX_DAMAGE_RATIO_HARD)

            fossil.reduce_integrity(damage)
            researcher.inventory.append(fossil)

            return f"Успех! Обнаружен образец: {fossil.species} ({fossil.bone_type}). Целостность: {fossil.integrity:.2f}"
        else:
            return "Раскопки прошли неудачно. Ископаемых на этом участке не обнаружено."


class ResearchService:
    """Логика проведения лабораторных исследований."""

    @staticmethod
    def analyze_fossil(researcher: Researcher, fossil: Fossil, period: JurassicPeriod) -> str:
        cost = GameConfig.RESEARCH_ENERGY_COST

        if researcher.energy < cost:
            raise ResourceError("Исследователь слишком утомлен для лабораторной работы.")

        if fossil.state != FossilState.EXCAVATED:
            raise WorkflowError("Для анализа требуется неочищенная находка из инвентаря.")

        researcher.spend_energy(cost)
        fossil.change_state(FossilState.ANALYZED)

        # Расчет знаний
        knowledge_gain = round(GameConfig.KNOWLEDGE_BASE_MULTIPLIER * fossil.integrity, 1)
        period.add_knowledge(knowledge_gain)
        researcher.add_skill(GameConfig.SKILL_GAIN_PER_RESEARCH)

        return f"Анализ завершен. Знания о периоде выросли на {knowledge_gain} ед."


class MuseumService:
    """Логика создания экспонатов и проведения выставок."""

    @staticmethod
    def create_model(museum: Museum, researcher: Researcher, indices: List[int], period: JurassicPeriod) -> str:
        cost = GameConfig.MODEL_CREATION_BUDGET_COST

        if museum.budget < cost:
            raise ResourceError(f"Бюджет музея недостаточен (нужно {cost} монет).")

        selected_fossils = []
        # Сортируем в обратном порядке, чтобы безопасно удалять по индексу
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(researcher.inventory):
                item = researcher.inventory[idx]
                if item.state == FossilState.ANALYZED:
                    selected_fossils.append(researcher.inventory.pop(idx))

        if not selected_fossils:
            raise WorkflowError("Не выбраны подходящие изученные находки для создания макета.")

        museum.spend_budget(cost)

        # Расчет качества макета
        avg_integrity = sum(f.integrity for f in selected_fossils) / len(selected_fossils)
        scientific_accuracy = min(1.0, period.knowledge_level / 100.0)  # Ограничиваем коэффициент 1.0

        final_quality = int(
            (avg_integrity * GameConfig.QUALITY_INTEGRITY_WEIGHT +
             scientific_accuracy * GameConfig.QUALITY_KNOWLEDGE_WEIGHT) * 100
        )

        species_name = selected_fossils[0].species

        model = DinosaurModel(
            name=f"Скелет {species_name}",
            species=species_name,
            quality=final_quality
        )
        museum.exhibits.append(model)

        for f in selected_fossils:
            f.change_state(FossilState.DISPLAYED)

        return f"Макет {species_name} успешно смонтирован. Качество реконструкции: {final_quality}/100."

    @staticmethod
    def run_exhibition(museum: Museum) -> str:
        if not museum.exhibits:
            raise WorkflowError("В музее нет готовых макетов для показа.")

        total_appeal = sum(model.quality for model in museum.exhibits)

        # Расчет прибыли
        base_revenue = total_appeal * GameConfig.REVENUE_PER_QUALITY_POINT
        random_bonus = random.randint(GameConfig.MIN_RANDOM_REVENUE, GameConfig.MAX_RANDOM_REVENUE)
        ticket_revenue = float(base_revenue + random_bonus)

        museum.add_revenue(ticket_revenue)
        museum.increase_reputation(len(museum.exhibits))

        return f"Выставка проведена! Продано билетов на сумму: {ticket_revenue:.2f} монет."


class SimulationCore:
    """Главный класс-контейнер симуляции."""

    def __init__(self):
        self.researcher: Optional[Researcher] = None
        self.museum: Optional[Museum] = None
        self.period: Optional[JurassicPeriod] = None
        self.formations: List[GeologicalFormation] = []

        data = PersistenceService.load_state()
        if data:
            self._restore_state(data)
        else:
            self._init_default_state()

    def _init_default_state(self):
        """Инициализация нового мира."""
        self.period = JurassicPeriod()
        self.museum = Museum()
        self.researcher = Researcher(name="Алан Грант")

        # Данные формаций (можно тоже вынести в конфиг, если их много)
        f1 = GeologicalFormation("Формация Моррисон", Difficulty.EASY)
        f1.buried_fossils = [
            Fossil("Diplodocus", "Femur"), Fossil("Stegosaurus", "Plate"),
            Fossil("Allosaurus", "Tooth"), Fossil("Brachiosaurus", "Rib"),
            Fossil("Apatosaurus", "Vertebra"), Fossil("Camarasaurus", "Skull"),
            Fossil("Ceratosaurus", "Horn")
        ]

        f2 = GeologicalFormation("Зольнхофен", Difficulty.MEDIUM)
        f2.buried_fossils = [
            Fossil("Archaeopteryx", "Feather"), Fossil("Compsognathus", "Femur"),
            Fossil("Pterodactylus", "Skull"), Fossil("Rhamphorhynchus", "Tail"),
            Fossil("Plesiosaurus", "Flipper"), Fossil("Ichthyosaurus", "Vertebra"),
            Fossil("Aegirosaurus", "Rib")
        ]

        f3 = GeologicalFormation("Формация Тяоцзишань", Difficulty.HARD)
        f3.buried_fossils = [
            Fossil("Darwinopterus", "Skull"), Fossil("Anchiornis", "Feather"),
            Fossil("Yi qi", "Wing membrane"), Fossil("Epidexipteryx", "Claw"),
            Fossil("Tianyulong", "Jaw"), Fossil("Castorocauda", "Tail bone"),
            Fossil("Juramaia", "Tooth")
        ]

        self.formations = [f1, f2, f3]

    def _restore_state(self, data: Dict):
        """Восстановление состояния из словаря."""
        self.researcher = Researcher.from_dict(data["researcher"])
        self.museum = Museum.from_dict(data["museum"])
        self.period = JurassicPeriod.from_dict(data["period"])
        self.formations = [GeologicalFormation.from_dict(f) for f in data["formations"]]

    def save(self):
        """Сохранение текущего состояния."""
        data = {
            "researcher": self.researcher.to_dict(),
            "museum": self.museum.to_dict(),
            "period": self.period.to_dict(),
            "formations": [f.to_dict() for f in self.formations]
        }
        PersistenceService.save_state(data)