import sys

from src.services import (

    SimulationCore,
    ExcavationService,
    ResearchService,
    MuseumService,
    SimulationError,
    GameConfig
)
from src.models import FossilState


def print_status(core: SimulationCore):
    """Вывод сводной информации о состоянии симуляции."""
    print("\n" + "=" * 50)
    print(f"[{core.researcher.name}] | Энергия: {core.researcher.energy}/100 | Навык: {core.researcher.skill_level}")
    print("-" * 50)
    print(f"[МУЗЕЙ] Бюджет: {core.museum.budget:.2f} | Репутация: {core.museum.reputation}")
    print(f"Экспонатов на выставке: {len(core.museum.exhibits)}")
    print("-" * 50)
    print(f"[НАУКА] Изученность Юрского периода: {core.period.knowledge_level:.1f}%")
    print(f"Справка: {core.period.get_climate_info()}")
    print("-" * 50)

    print("[ИНВЕНТАРЬ]:")
    if not core.researcher.inventory:
        print("  Пусто.")
    else:
        for i, fossil in enumerate(core.researcher.inventory):
            print(
                f"  [{i}] {fossil.species} ({fossil.bone_type}) -> {fossil.state.value} (Целость: {fossil.integrity})")
    print("=" * 50 + "\n")


def print_menu():
    print("Доступные команды:")
    print("1. Статус системы")
    print("2. Экспедиция (Раскопки)")
    print("3. Лаборатория (Анализ)")
    print("4. Мастерская (Создать макет)")
    print("5. Зал (Провести выставку)")
    print("6. Отдых (Восстановить силы)")
    print("0. Сохранить и выйти")


def handle_excavation(core: SimulationCore):
    """Интерфейс для запуска полевых работ."""
    print("\nДоступные локации:")
    for i, form in enumerate(core.formations):
        print(f"  [{i}] {form.name} (Сложность: {form.difficulty.name} | Осталось костей: {len(form.buried_fossils)})")

    choice = input("Номер формации: ")
    if not choice.isdigit() or int(choice) >= len(core.formations):
        print("Ошибка ввода: неверная локация.")
        return

    formation = core.formations[int(choice)]
    result = ExcavationService.excavate(core.researcher, formation)
    print(f"\n[РЕЗУЛЬТАТ]: {result}")


def handle_research(core: SimulationCore):
    """Интерфейс для анализа находок."""
    # Собираем только те ископаемые, которые можно изучить
    unresearched = [
        f for f in core.researcher.inventory
        if f.state == FossilState.EXCAVATED
    ]

    if not unresearched:
        print("\nНет доступных находок для изучения. Сначала проведите раскопки.")
        return

    print("\nОжидают анализа:")
    # Выводим порядковые номера 0, 1, 2...
    for display_idx, fossil in enumerate(unresearched):
        print(f"  [{display_idx}] {fossil.species} ({fossil.bone_type})")

    choice = input("Номер находки: ")

    # Проверяем выбор пользователя относительно длины короткого списка
    if not choice.isdigit() or int(choice) >= len(unresearched):
        print("Ошибка ввода: неверный номер.")
        return

    # Берем кость и отправляем в сервис
    fossil = unresearched[int(choice)]
    result = ResearchService.analyze_fossil(core.researcher, fossil, core.period)
    print(f"\n[РЕЗУЛЬТАТ]: {result}")


def handle_museum_creation(core: SimulationCore):
    """Интерфейс для создания музейных экспонатов."""
    # Сохраняем пару: (оригинальный индекс в инвентаре, сама кость)
    analyzed = [
        (original_idx, f) for original_idx, f in enumerate(core.researcher.inventory)
        if f.state == FossilState.ANALYZED
    ]

    if not analyzed:
        print("\nНет изученных костей. Проведите анализ в лаборатории.")
        return

    print("\nДоступный материал:")
    # display_idx - это 0, 1, 2... для красивого вывода
    for display_idx, (original_idx, fossil) in enumerate(analyzed):
        print(f"  [{display_idx}] {fossil.species} ({fossil.bone_type})")

    choice = input("Выберите основу для макета (номер): ")

    if not choice.isdigit() or int(choice) >= len(analyzed):
        print("Ошибка ввода: неверный номер.")
        return

    # Достаем оригинальный индекс выбранного элемента
    selected_original_idx = analyzed[int(choice)][0]

    result = MuseumService.create_model(core.museum, core.researcher, [selected_original_idx], core.period)
    print(f"\n[РЕЗУЛЬТАТ]: {result}")


def print_help():
    print("\n" + "*" * 50)
    print(" ИНСТРУКЦИЯ ПОЛЬЗОВАТЕЛЯ ")
    print("*" * 50)
    print(f"- Раскопки: тратят {GameConfig.EXCAVATION_ENERGY_COST} энергии. Шанс зависит от навыка.")
    print(f"- Анализ: тратит {GameConfig.RESEARCH_ENERGY_COST} энергии. Повышает знания о периоде.")
    print(f"- Макеты: стоят {GameConfig.MODEL_CREATION_BUDGET_COST} монет. Требуют изученных костей.")
    print("- Выставки: приносят доход на основе качества макетов.")
    print("*" * 50 + "\n")


def main():
    print("Инициализация программы 'Модель Юрского Периода'...")
    core = SimulationCore()
    print_help()

    while True:
        print_menu()
        choice = input("\nВвод команды: ")

        try:
            if choice == '1':
                print_status(core)
            elif choice == '2':
                handle_excavation(core)
            elif choice == '3':
                handle_research(core)
            elif choice == '4':
                handle_museum_creation(core)
            elif choice == '5':
                result = MuseumService.run_exhibition(core.museum)
                print(f"\n[РЕЗУЛЬТАТ]: {result}")
            elif choice == '6':
                core.researcher.rest()
                print("\n[РЕЗУЛЬТАТ]: Энергия восстановлена до 100.")
            elif choice == '0':
                core.save()
                print("\nСостояние сохранено. Завершение работы.")
                sys.exit(0)
            else:
                print("\nКоманда не распознана.")

        except SimulationError as e:
            # Обработка ожидаемых бизнес-исключений (наше требование по лабе)
            print(f"\n[СИСТЕМНОЕ СООБЩЕНИЕ]: {e}")
        except Exception as e:
            # Обработка фатальных ошибок
            print(f"\n[КРИТИЧЕСКИЙ СБОЙ]: {e}")


if __name__ == "__main__":
    main()