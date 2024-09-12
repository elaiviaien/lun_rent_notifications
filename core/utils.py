import csv
import tempfile


def get_orders() -> list[list[str]]:
    with open("orders.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        orders = [list(order.values()) for order in reader]
    return orders


def save_order(user_id: int, search_url: str, last_scraped_id: int) -> None:
    with open("orders.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        orders = list(reader)
        user_orders = [order for order in orders if order[0] == str(user_id)]
        if user_orders:
            user_order = user_orders[0]
            user_order[1] = search_url
            user_order[2] = last_scraped_id
        else:
            orders.append([user_id, search_url, last_scraped_id])

    with open("orders.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(orders)


def remove_order(user_id: int) -> None:
    with open("orders.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        orders = list(reader)
        orders = [order for order in orders if order[0] != str(user_id)]

    with open("orders.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(orders)


def save_temp_page(content: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, prefix="debug_", suffix=".html"
    ) as _file:
        _file.write(content)
        temp_file_name = _file.name

    return temp_file_name
