import pytest
from unittest.mock import patch
from src.main import (
    print_status, print_menu, print_help,
    handle_excavation, handle_research, handle_museum_creation, main
)
from src.services import SimulationCore
from src.models import Fossil, FossilState


@pytest.fixture
def core():
    """Создаем чистое ядро симуляции для тестов меню"""
    with patch('src.services.PersistenceService.load_state', return_value=None):
        return SimulationCore()


def test_print_functions(core, capsys):
    """Проверяем, что функции вывода не падают и выводят нужный текст"""
    print_status(core)
    print_menu()
    print_help()

    out, _ = capsys.readouterr()
    # ИСПРАВЛЕНО: ищем слова из нового интерфейса
    assert "Энергия:" in out
    assert "Доступные команды" in out
    assert "ИНСТРУКЦИЯ" in out


@patch('builtins.input', side_effect=['0'])
def test_handle_excavation_valid(mock_input, core, capsys):
    """Симулируем ввод '0' при выборе формации для раскопок"""
    handle_excavation(core)
    out, _ = capsys.readouterr()
    assert "РЕЗУЛЬТАТ" in out


@patch('builtins.input', side_effect=['99', 'abc'])
def test_handle_excavation_invalid(mock_input, core, capsys):
    """Симулируем ошибочный ввод при выборе формации"""
    handle_excavation(core)
    out, _ = capsys.readouterr()
    assert "Ошибка ввода" in out

    handle_excavation(core)
    out, _ = capsys.readouterr()
    assert "Ошибка ввода" in out


def test_handle_research_empty(core, capsys):
    """Пытаемся исследовать, когда инвентарь пуст"""
    handle_research(core)
    out, _ = capsys.readouterr()
    assert "Нет доступных находок" in out


@patch('builtins.input', side_effect=['0'])
def test_handle_research_valid(mock_input, core, capsys):
    """Добавляем выкопанную кость и успешно исследуем ее"""
    core.researcher.inventory.append(Fossil("Rex", "Bone", state=FossilState.EXCAVATED))
    handle_research(core)
    out, _ = capsys.readouterr()
    assert "РЕЗУЛЬТАТ" in out


def test_handle_museum_empty(core, capsys):
    """Пытаемся создать макет без костей"""
    handle_museum_creation(core)
    out, _ = capsys.readouterr()
    assert "Нет изученных костей" in out


@patch('builtins.input', side_effect=['0'])
def test_handle_museum_valid(mock_input, core, capsys):
    """Добавляем изученную кость и успешно создаем макет"""
    core.researcher.inventory.append(Fossil("Rex", "Bone", state=FossilState.ANALYZED))
    handle_museum_creation(core)
    out, _ = capsys.readouterr()
    assert "РЕЗУЛЬТАТ" in out


# ИСПРАВЛЕНО: Правильный перехват выхода из программы
@patch('builtins.input', side_effect=['0'])
def test_main_exit(mock_input):
    """Симулируем запуск игры и мгновенный выход (пользователь ввел '0')."""
    with patch('src.services.SimulationCore.save') as mock_save:
        # Ловим системное исключение выхода, чтобы разорвать цикл while True
        with pytest.raises(SystemExit) as exit_info:
            main()

        # Проверяем, что выход был успешным (код 0) и данные сохранились
        assert exit_info.value.code == 0
        mock_save.assert_called_once()