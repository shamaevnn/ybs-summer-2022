get_nodes = """
Получить информацию об элементе по идентификатору.
 При получении информации о категории также предоставляется информация о её дочерних элементах.  # noqa
 """

delete_node = """
Удалить элемент по идентификатору.
При удалении категории удаляются все дочерние элементы.
Доступ к статистике (истории обновлений) удаленного элемента невозможен.
"""

imports = """
Импортирует новые товары и/или категории.
Товары/категории импортированные повторно обновляют текущие.
Изменение типа элемента с товара на категорию или с категории на товар не допускается.
"""
