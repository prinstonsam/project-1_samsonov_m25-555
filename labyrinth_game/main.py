#!/usr/bin/env python3

from labyrinth_game import constants, player_actions, utils

game_state = {
    'player_inventory': [],  # Инвентарь игрока
    'current_room': 'entrance',  # Текущая комната
    'game_over': False,  # Значения окончания игры
    'steps_taken': 0  # Количество шагов
}

def process_command(game_state, command):
    """
    Обрабатывает команду пользователя.
    
    Args:
        game_state (dict): Словарь, содержащий текущее состояние игры.
        command (str): Введенная пользователем строка.
    """
    # Разделяем строку на части
    parts = command.strip().lower().split()
    if not parts:
        return
    
    cmd = parts[0]
    arg = ' '.join(parts[1:]) if len(parts) > 1 else None
    
    match cmd:
        case 'help' | 'h':
            player_actions.show_help(constants.COMMANDS)
        case 'look' | 'l':
            utils.describe_current_room(game_state)
        case 'go' | 'g':
            if arg:
                player_actions.move_player(game_state, arg)
            else:
                print("Куда идти? Укажите направление.")
        case 'take' | 't':
            if arg:
                player_actions.take_item(game_state, arg)
            else:
                print("Что взять? Укажите предмет.")
        case 'inventory' | 'i':
            player_actions.show_inventory(game_state)
        case 'use' | 'u':
            if arg:
                # Специальная обработка для сундука с сокровищами
                if arg == 'treasure_chest' or arg == 'treasure chest':
                    if game_state['current_room'] == 'treasure_room':
                        utils.attempt_open_treasure(game_state)
                    else:
                        print("Здесь нет сундука с сокровищами.")
                else:
                    player_actions.use_item(game_state, arg)
            else:
                print("Что использовать? Укажите предмет.")
        case 'solve' | 's':
            # Если игрок в treasure_room, вызываем attempt_open_treasure
            if game_state['current_room'] == 'treasure_room':
                utils.attempt_open_treasure(game_state)
            else:
                utils.solve_puzzle(game_state)
        case 'quit' | 'exit' | 'q':
            print("Спасибо за игру!")
            game_state['game_over'] = True
        case 'north' | 'south' | 'east' | 'west':
            # Односложные команды для движения
            player_actions.move_player(game_state, cmd)
        case _:
            print("Неизвестная команда. Введите 'help' для списка команд.")


def main():
    """
    Главная функция игры - точка входа.
    
    Запускает игровой цикл и обрабатывает команды игрока
    до окончания игры (победы или поражения).
    """
    print("Добро пожаловать в Лабиринт сокровищ!")
    utils.describe_current_room(game_state)

    while not game_state['game_over']:
        command = player_actions.get_input()
        process_command(game_state, command)


if __name__ == "__main__":
    main()
