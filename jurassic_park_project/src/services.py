import json
import os
import random
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


class SimulationError(Exception):
    """Базовый класс пользовательских исключений."""
    pass


class ResourceError(SimulationError):
    """Исключение: нехватка энергии или бюджета."""
    pass


class WorkflowError(SimulationError):
    """Исключение: нарушение бизнес-логики (например, раскопки в пустой формации)."""
    pass


class PersistenceService:
    """Сервис для сохранения и загрузки состояния системы (JSON сериализация)."""
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
        ENERGY_COST = 10

        if researcher.energy < ENERGY_COST:
            raise ResourceError("Недостаточно энергии для экспедиции. Необходим отдых.")

        if formation.is_empty():
            raise WorkflowError("Данная формация полностью исследована, ископаемых не осталось.")

        researcher.spend_energy(ENERGY_COST)

        # Вероятность успеха рассчитывается от базовой ставки, навыка и сложности породы
        base_chance = 60
        skill_bonus = researcher.skill_level * 5
        difficulty_penalty = formation.difficulty.value * 15

        success_chance = max(10, min(90, base_chance + skill_bonus - difficulty_penalty))
        roll = random.randint(1, 100)

        if roll <= success_chance:
            fossil = formation.extract_fossil()
            fossil.change_state(FossilState.EXCAVATED)

            # Небольшой шанс повредить находку при извлечении из твердых пород
            damage = random.uniform(0.0, 0.2) if formation.difficulty != Difficulty.EASY else 0.0
            fossil.reduce_integrity(damage)

            researcher.inventory.append(fossil)
            return f"Успех! Обнаружен образец: {fossil.species} ({fossil.bone_type}). Целостность: {fossil.integrity}"
        else:
            return "Раскопки прошли неудачно. Ископаемых на этом участке не обнаружено."


class ResearchService:
    """Логика проведения лабораторных исследований."""

    @staticmethod
    def analyze_fossil(researcher: Researcher, fossil: Fossil, period: JurassicPeriod) -> str:
        ENERGY_COST = 5

        if researcher.energy < ENERGY_COST:
            raise ResourceError("Исследователь слишком утомлен для лабораторной работы.")

        if fossil.state != FossilState.EXCAVATED:
            raise WorkflowError("Для анализа требуется неочищенная находка из инвентаря.")

        researcher.spend_energy(ENERGY_COST)
        fossil.change_state(FossilState.ANALYZED)

        # Очки знаний зависят от целостности находки
        knowledge_gain = round(5.0 * fossil.integrity, 1)
        period.add_knowledge(knowledge_gain)
        researcher.add_skill(1)

        return f"Анализ завершен. Знания о периоде выросли на {knowledge_gain} ед."


class MuseumService:
    """Логика создания экспонатов и проведения выставок."""

    @staticmethod
    def create_model(museum: Museum, researcher: Researcher, indices: List[int], period: JurassicPeriod) -> str:
        MODEL_COST = 300.0

        if museum.budget < MODEL_COST:
            raise ResourceError(f"Бюджет музея недостаточен (нужно {MODEL_COST} монет).")

        selected_fossils = []
        # Извлекаем кости из инвентаря (с конца, чтобы индексы не смещались)
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(researcher.inventory):
                if researcher.inventory[idx].state == FossilState.ANALYZED:
                    selected_fossils.append(researcher.inventory.pop(idx))

        if not selected_fossils:
            raise WorkflowError("Не выбраны подходящие изученные находки для создания макета.")

        museum.spend_budget(MODEL_COST)

        # Итоговое качество зависит от целостности кости и знаний о периоде
        avg_integrity = sum(f.integrity for f in selected_fossils) / len(selected_fossils)
        scientific_accuracy = period.knowledge_level / 100.0

        final_quality = int((avg_integrity * 0.6 + scientific_accuracy * 0.4) * 100)
        species_name = selected_fossils[0].species

        model = DinosaurModel(
            name=f"Скелет {species_name}",
            species=species_name,
            quality=final_quality
        )
        museum.exhibits.append(model)

        # Обновляем статус использованных костей
        for f in selected_fossils:
            f.change_state(FossilState.DISPLAYED)

        return f"Макет {species_name} успешно смонтирован. Качество реконструкции: {final_quality}/100."

    @staticmethod
    def run_exhibition(museum: Museum) -> str:
        if not museum.exhibits:
            raise WorkflowError("В музее нет готовых макетов для показа.")

        total_appeal = sum(model.quality for model in museum.exhibits)

        # Расчет прибыли от билетов на основе качества выставки
        ticket_revenue = float(total_appeal * 5 + random.randint(50, 150))
        museum.add_revenue(ticket_revenue)
        museum.increase_reputation(len(museum.exhibits))

        return f"Выставка проведена! Продано билетов на сумму: {ticket_revenue} монет."


class SimulationCore:
    """Главный класс-контейнер, хранящий текущее состояние всех объектов симуляции."""

    def __init__(self):
        self.researcher: Optional[Researcher] = None
        self.museum: Optional[Museum] = None
        self.period: Optional[JurassicPeriod] = None
        self.formations: List[GeologicalFormation] = []

        # Попытка восстановить предыдущий сеанс
        data = PersistenceService.load_state()
        if data:
            self._restore_state(data)
        else:
            self._init_default_state()

    def _init_default_state(self):
        """Создание дефолтных объектов при первом запуске."""
        self.period = JurassicPeriod()
        self.museum = Museum()
        self.researcher = Researcher(name="Алан Грант")

        # Наполнение локаций данными
        f1 = GeologicalFormation("Формация Моррисон", Difficulty.EASY)
        f1.buried_fossils = [
            Fossil("Diplodocus", "Femur"),
            Fossil("Stegosaurus", "Plate"),
            Fossil("Allosaurus", "Tooth"),
            Fossil("Brachiosaurus", "Rib"),
            Fossil("Apatosaurus", "Vertebra"),
            Fossil("Camarasaurus", "Skull"),
            Fossil("Ceratosaurus", "Horn")
        ]

        f2 = GeologicalFormation("Зольнхофен", Difficulty.MEDIUM)
        f2.buried_fossils = [
            Fossil("Archaeopteryx", "Feather"),
            Fossil("Compsognathus", "Femur"),
            Fossil("Pterodactylus", "Skull"),
            Fossil("Rhamphorhynchus", "Tail"),
            Fossil("Plesiosaurus", "Flipper"),
            Fossil("Ichthyosaurus", "Vertebra"),
            Fossil("Aegirosaurus", "Rib")
        ]

        f3 = GeologicalFormation("Формация Тяоцзишань", Difficulty.HARD)
        f3.buried_fossils = [
            Fossil("Darwinopterus", "Skull"),
            Fossil("Anchiornis", "Feather"),
            Fossil("Yi qi", "Wing membrane"),
            Fossil("Epidexipteryx", "Claw"),
            Fossil("Tianyulong", "Jaw"),
            Fossil("Castorocauda", "Tail bone"),
            Fossil("Juramaia", "Tooth")
        ]

        self.formations = [f1, f2, f3]

    def _restore_state(self, data: Dict):
        """Маппинг данных из словаря в объекты."""
        self.researcher = Researcher.from_dict(data["researcher"])
        self.museum = Museum.from_dict(data["museum"])
        self.period = JurassicPeriod.from_dict(data["period"])
        self.formations = [GeologicalFormation.from_dict(f) for f in data["formations"]]

    def save(self):
        """Передача текущего состояния в PersistenceService."""
        data = {
            "researcher": self.researcher.to_dict(),
            "museum": self.museum.to_dict(),
            "period": self.period.to_dict(),
            "formations": [f.to_dict() for f in self.formations]
        }
        PersistenceService.save_state(data)