import pytest
from unittest.mock import patch
from src.models import (
    Researcher, GeologicalFormation, Fossil, Museum,
    JurassicPeriod, FossilState, Difficulty
)
from src.services import (
    ExcavationService, ResearchService, MuseumService,
    PersistenceService, ResourceError, WorkflowError
)


# --- ФИКСТУРЫ (Подготовка данных) ---

@pytest.fixture
def setup_data():
    """
    Создает свежие тестовые данные перед каждым тестом.
    Это гарантирует, что тесты не влияют друг на друга.
    """
    researcher = Researcher(name="Грант", energy=100)
    period = JurassicPeriod(knowledge_level=0.0)
    museum = Museum(budget=1000.0)

    fossil = Fossil("Diplodocus", "Femur", FossilState.BURIED)
    formation = GeologicalFormation("Тест-Локация", Difficulty.EASY)
    formation.buried_fossils.append(fossil)

    return researcher, period, museum, fossil, formation


# --- ТЕСТЫ МОДЕЛЕЙ (Инкапсуляция) ---

def test_researcher_energy():
    researcher = Researcher(name="Тестер")

    researcher.spend_energy(30)
    assert researcher.energy == 70

    # Проверяем защиту от отрицательной энергии
    researcher.spend_energy(100)
    assert researcher.energy == 0


def test_fossil_integrity():
    fossil = Fossil("T-Rex", "Skull", integrity=1.0)
    fossil.reduce_integrity(0.3)
    assert fossil.integrity == 0.7


def test_geological_formation_extraction():
    formation = GeologicalFormation("Тест", Difficulty.EASY)
    fossil = Fossil("T-Rex", "Tooth")
    formation.buried_fossils.append(fossil)

    # Успешное извлечение
    extracted = formation.extract_fossil()
    assert extracted.species == "T-Rex"
    assert formation.is_empty()

    # Ошибка при попытке извлечь из пустой формации
    with pytest.raises(ValueError):
        formation.extract_fossil()


# --- ТЕСТЫ БИЗНЕС-ЛОГИКИ (Сервисы) ---

def test_excavation_no_energy(setup_data):
    researcher, _, _, _, formation = setup_data
    researcher.energy = 5  # Имитируем усталость

    with pytest.raises(ResourceError):
        ExcavationService.excavate(researcher, formation)


def test_excavation_empty_formation(setup_data):
    researcher, _, _, _, formation = setup_data
    formation.buried_fossils.clear()  # Опустошаем локацию

    with pytest.raises(WorkflowError):
        ExcavationService.excavate(researcher, formation)


def test_excavation_failure(setup_data):
    researcher, _, _, _, formation = setup_data
    # Искусственно заставляем генератор случайных чисел выдать 100 (гарантированный провал)
    with patch('random.randint', return_value=100):
        result = ExcavationService.excavate(researcher, formation)
        assert "неудачно" in result


def test_research_success(setup_data):
    researcher, period, _, fossil, _ = setup_data

    # Готовим кость (будто мы её уже выкопали)
    fossil.change_state(FossilState.EXCAVATED)
    researcher.inventory.append(fossil)

    result_message = ResearchService.analyze_fossil(researcher, fossil, period)

    assert fossil.state == FossilState.ANALYZED
    assert researcher.energy == 95
    assert period.knowledge_level > 0.0
    assert "Анализ завершен" in result_message


def test_research_wrong_state(setup_data):
    researcher, period, _, fossil, _ = setup_data
    # Пытаемся изучить кость со статусом BURIED (в земле)
    with pytest.raises(WorkflowError):
        ResearchService.analyze_fossil(researcher, fossil, period)


def test_museum_create_model_success(setup_data):
    researcher, period, museum, fossil, _ = setup_data

    # Готовим изученную кость
    fossil.change_state(FossilState.ANALYZED)
    researcher.inventory.append(fossil)

    MuseumService.create_model(museum, researcher, [0], period)

    # Проверяем экономику и логику
    assert museum.budget == 700.0  # 1000 - 300
    assert len(museum.exhibits) == 1
    assert museum.exhibits[0].species == "Diplodocus"
    assert fossil.state == FossilState.DISPLAYED  # Кость поменяла статус


def test_museum_no_budget(setup_data):
    researcher, period, museum, fossil, _ = setup_data

    museum.budget = 100.0  # Денег не хватает
    fossil.change_state(FossilState.ANALYZED)
    researcher.inventory.append(fossil)

    with pytest.raises(ResourceError):
        MuseumService.create_model(museum, researcher, [0], period)


def test_museum_run_exhibition_empty(setup_data):
    _, _, museum, _, _ = setup_data
    # Музей пустой, должна быть ошибка логики
    with pytest.raises(WorkflowError):
        MuseumService.run_exhibition(museum)


def test_persistence_save_and_load(tmp_path):
    # tmp_path - встроенная фикстура pytest для создания временных файлов
    PersistenceService.FILE_PATH = str(tmp_path / "test_state.json")

    test_data = {"test_key": "test_value"}
    PersistenceService.save_state(test_data)

    loaded_data = PersistenceService.load_state()
    assert loaded_data == test_data


def test_persistence_load_missing_file(tmp_path):
    # Проверяем, что вернется None, если файла сохранения еще нет
    PersistenceService.FILE_PATH = str(tmp_path / "missing.json")
    assert PersistenceService.load_state() is None