from labyrinth_game import constants, utils


def show_help(commands):
    """
    Выводит список доступных команд.
    
    Args:
        commands (dict): Словарь команд с их описаниями.
    """
    print("Доступные команды:")
    for command, description in commands.items():
        print(f"  {command:<16} - {description}")

def show_inventory(game_state):
    """
    Выводит содержимое инвентаря игрока.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    inventory = game_state.get('player_inventory', [])
    if not inventory:
        print("Инвентарь пуст.")
    else:
        print("Инвентарь:", ", ".join(inventory))

def move_player(game_state, direction):
    """
    Перемещает игрока в указанном направлении.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
        direction (str): Направление движения (например, 'north').
    """

    
    current_room_key = game_state['current_room']
    current_room = constants.ROOMS.get(current_room_key, {})
    exits = current_room.get('exits', {})
    
    if direction in exits:
        next_room = exits[direction]
        
        # Проверка доступа к treasure_room
        if next_room == 'treasure_room':
            player_inventory = game_state.get('player_inventory', [])
            if 'rusty key' not in player_inventory:
                print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
                return
            else:
                print(
                "Вы используете найденный ключ, "
                "чтобы открыть путь в комнату сокровищ."
            )
        
        # Перемещение успешно
        game_state['current_room'] = next_room
        game_state['steps_taken'] += 1
        utils.describe_current_room(game_state)
        utils.random_event(game_state)
    else:
        print("Нельзя пойти в этом направлении.")


def take_item(game_state, item_name):
    """
    Берет предмет из текущей комнаты и добавляет его в инвентарь игрока.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
        item_name (str): Название предмета для взятия.
    """
    current_room_key = game_state['current_room']
    current_room = constants.ROOMS.get(current_room_key, {})
    room_items = current_room.get('items', [])
    
    if item_name in room_items:
        game_state['player_inventory'].append(item_name)
        room_items.remove(item_name)
        print(f"Вы подняли: {item_name}")
    else:
        print("Такого предмета здесь нет.")


def use_item(game_state, item_name):
    """
    Использует предмет из инвентаря игрока.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
        item_name (str): Название предмета для использования.
    """
    inventory = game_state.get('player_inventory', [])
    
    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return
    
    if item_name == 'torch':
        print("Вы зажгли факел. Стало светлее!")
    elif item_name == 'sword':
        print("Вы крепко сжимаете меч в руке. Чувствуете уверенность!")
    elif item_name == 'bronze box':
        print("Вы открыли бронзовую шкатулку.")
        if 'rusty key' not in inventory:
            game_state['player_inventory'].append('rusty key')
            print("Внутри вы нашли ржавый ключ!")
    else:
        print(f"Вы не знаете, как использовать {item_name}.")


def get_input(prompt="> "):
    """
    Получает ввод от игрока с обработкой исключений.
    
    Args:
        prompt (str): Строка приглашения для ввода.
        
    Returns:
        str: Введенная команда или 'quit' при прерывании.
    """
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"
