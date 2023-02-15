"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.utils import read_tree

ErrNoParent = 'Вы не указали родительскую категорию'
ErrInvalidParam = 'Неверный параметр'
ErrInvalidCmd = 'Неизвестная команда'

cat_repo = SqliteRepository[Category]("../../Python_23.db.sqbpro", Category)
exp_repo = SqliteRepository[Expense]("../../Python_23.db.sqbpro", Expense)

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

Category.create_from_tree(read_tree(cats), cat_repo)


def get_category(command: str) -> Category | None:
    parent = 0
    name = ''
    index = -1
    try:
        index = command.index(' ')
    except ValueError:
        pass
    if index >= 0:
        name = command[0:command.index(' ')]
        command = command[command.index(' ') + 1:]
        if len(command) == 0:
            print(ErrNoParent)
            return None
        if not command.isnumeric():
            print(ErrInvalidParam)
            return None
        parent = int(command)
    else:
        name = command
    category = Category(name, parent)
    return category


while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd.startswith('добавить категорию '):
        cmd = cmd[len('добавить категорию '):]
        obj = get_category(cmd)
        if obj is None:
            continue
        pk = cat_repo.add(obj)
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)
    else:
        print(ErrInvalidCmd)

