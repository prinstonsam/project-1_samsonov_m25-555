import math

from labyrinth_game import constants

# Константы для случайных событий
EVENT_PROBABILITY_MODULO = 10  # Вероятность события 1 к 10 (10%)
DAMAGE_ROLL_MODULO = 10  # Диапазон для броска урона
FATAL_DAMAGE_THRESHOLD = 3  # Порог смертельного урона
EVENT_TYPES_COUNT = 3  # Количество типов случайных событий
EVENT_TYPE_FIND_COIN = 0  # Тип события: найти монету
EVENT_TYPE_HEAR_RUSTLE = 1  # Тип события: услышать шорох
EVENT_TYPE_TRIGGER_TRAP = 2  # Тип события: сработать ловушка


def pseudo_random(seed, modulo):
    """
    Генерирует псевдослучайное число в диапазоне [0, modulo) на основе seed.
    
    Использует математическую формулу на основе синуса для создания 
    предсказуемых случайных событий без использования модуля random.
    
    Args:
        seed (int): Целое число (например, количество шагов).
        modulo (int): Целое число для определения диапазона результата.
    
    Returns:
        int: Целое число в диапазоне [0, modulo).
    """
    x = math.sin(seed * 12.9898) * 43758.5453
    
    frac = x - math.floor(x)
    
    result = int(frac * modulo)
    
    return result


def trigger_trap(game_state):
    """
    Имитирует срабатывание ловушки с негативными последствиями для игрока.
    
    Если у игрока есть предметы, случайным образом удаляется один предмет.
    Если инвентарь пуст, игрок получает урон и может проиграть.
    
    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    print("Ловушка активирована! Пол стал дрожать...")
    
    player_inventory = game_state.get('player_inventory', [])
    steps_taken = game_state.get('steps_taken', 0)
    
    if player_inventory:
        item_count = len(player_inventory)
        random_index = pseudo_random(steps_taken, item_count)
        lost_item = player_inventory.pop(random_index)
        print(f"В суматохе вы потеряли: {lost_item}!")
    else:
        damage_roll = pseudo_random(steps_taken, DAMAGE_ROLL_MODULO)
        if damage_roll < FATAL_DAMAGE_THRESHOLD:
            print("Ловушка оказалась смертельной! Вы погибли...")
            game_state['game_over'] = True
        else:
            print("Вы едва успели увернуться! На этот раз вам повезло.")


def random_event(game_state):
    """
    Генерирует случайные события во время перемещения игрока.
    
    События происходят с низкой вероятностью и могут включать:
    - Находку предметов
    - Испуг от шороха
    - Срабатывание ловушки
    
    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    steps_taken = game_state.get('steps_taken', 0)
    
    event_trigger = pseudo_random(steps_taken, EVENT_PROBABILITY_MODULO)
    
    if event_trigger != 0:
        return
    
    event_type = pseudo_random(steps_taken + 1, EVENT_TYPES_COUNT)
    
    if event_type == EVENT_TYPE_FIND_COIN:
        print("Что-то блестит на полу... Вы нашли монетку!")
        current_room_key = game_state['current_room']
        room_data = constants.ROOMS.get(current_room_key, {})
        room_items = room_data.get('items', [])
        room_items.append('coin')
        
    elif event_type == EVENT_TYPE_HEAR_RUSTLE:
        print("Вы слышите подозрительный шорох в темноте...")
        player_inventory = game_state.get('player_inventory', [])
        if 'sword' in player_inventory:
            print("Вы достаете меч и отпугиваете существо!")
        
    elif event_type == EVENT_TYPE_TRIGGER_TRAP:
        current_room_key = game_state['current_room']
        player_inventory = game_state.get('player_inventory', [])
        
        if current_room_key == 'trap_room' and 'torch' not in player_inventory:
            print("Вы не видите в темноте и наступаете на нажимную плиту!")
            trigger_trap(game_state)


def attempt_open_treasure(game_state):
    """
    Реализует логику победы при попытке открыть сундук с сокровищами.
    
    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    current_room_key = game_state['current_room']
    room_data = constants.ROOMS.get(current_room_key, {})
    room_items = room_data.get('items', [])
    
    if 'treasure chest' not in room_items:
        print("Сундук уже открыт или отсутствует.")
        return
    
    player_inventory = game_state.get('player_inventory', [])
    
    has_treasure_key = 'treasure key' in player_inventory
    has_rusty_key = 'rusty key' in player_inventory
    
    if has_treasure_key or has_rusty_key:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        
        room_items.remove('treasure chest')
        
        print("В сундуке сокровище! Вы победили!")
        game_state['game_over'] = True
        return
    
    print("Сундук заперт. Вы можете попробовать ввести код.")
    answer = input("Ввести код? (да/нет): ").strip().lower()
    
    if answer == 'да' or answer == 'yes':
        user_code = input("Введите код: ").strip()
        
        puzzle = room_data.get('puzzle')
        if puzzle:
            correct_code = puzzle[1]
            
            if user_code.lower() == correct_code.lower():
                print("Код верный! Замок щёлкает, сундук открывается!")
                
                room_items.remove('treasure chest')
                
                print("В сундуке сокровище! Вы победили!")
                game_state['game_over'] = True
            else:
                print("Код неверный. Сундук остается заперт.")
        else:
            print("Не удается определить правильный код.")
    else:
        print("Вы отступаете от сундука.")


def solve_puzzle(game_state):
    """
    Решает загадку в текущей комнате.
    
    Поддерживает альтернативные варианты ответов.
    Награда зависит от комнаты.
    При неверном ответе в trap_room активируется ловушка.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    current_room_key = game_state['current_room']
    room_data = constants.ROOMS.get(current_room_key, {})
    
    puzzle = room_data.get('puzzle')
    if not puzzle:
        print("Загадок здесь нет.")
        return
    
    question, correct_answer = puzzle
    print(question)
    user_answer = input("Ваш ответ: ").strip()
    
    alternative_answers = {
        '10': ['10', 'десять'],
        'шаг шаг шаг': ['шаг шаг шаг'],
        'резонанс': ['резонанс', 'огонь', 'пламя']
    }
    
    default_answer = [correct_answer.lower()]
    accepted_answers = alternative_answers.get(
        correct_answer.lower(), default_answer
    )
    
    if user_answer.lower() in accepted_answers:
        print("Правильно! Загадка решена!")
        room_data['puzzle'] = None
        
        room_rewards = {
            'hall': ('gold coin', 'За решение загадки вы получили монету!'),
            'trap_room': (
                'treasure_key',
                'За решение загадки вы получили ключ от сокровищницы!'
            ),
            'library': (
                'ancient scroll',
                'За решение загадки вы получили древний свиток!'
            ),
            'treasure_room': (
                'gold coin',
                'За решение загадки вы получили монету!'
            )
        }
        
        default_reward = (
            'gold coin',
            'За решение загадки вы получили монету!'
        )
        reward_item, reward_message = room_rewards.get(
            current_room_key, default_reward
        )
        game_state['player_inventory'].append(reward_item)
        print(reward_message)
    else:
        print("Неверно. Попробуйте снова.")
        
        if current_room_key == 'trap_room':
            print("Неправильный ответ активировал защитный механизм!")
            trigger_trap(game_state)


def describe_current_room(game_state):
    """
    Выводит описание текущей комнаты, основываясь на состоянии игры.

    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
    """
    current_room_key = game_state['current_room']
    room_data = constants.ROOMS.get(current_room_key, {})
    print(f"== {current_room_key.upper()} ==")

    print(room_data.get('description', 'Пустая комната без описания.'))
    visible_items = room_data.get('items', [])
    if visible_items:
        print("Заметные предметы:", ", ".join(visible_items))

    exits = room_data.get('exits', {})
    if exits:
        print("Выходы:", ", ".join(exits.keys()))

    if room_data.get('puzzle'):
        print("Кажется, здесь есть загадка (используйте команду solve).")

