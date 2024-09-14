import csv
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_orders() -> list[list[str]]:
    file_path = os.path.join(script_dir,"../orders.csv")
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        orders = [list(order.values()) for order in reader]
    return orders


def save_order(user_id: int, search_url: str, last_scraped_id: int) -> None:
    file_path = os.path.join(script_dir,"../orders.csv")
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        orders = list(reader)
        user_orders = [order for order in orders if order[0] == str(user_id)]
        if user_orders:
            user_order = user_orders[0]
            user_order[1] = search_url
            user_order[2] = last_scraped_id
        else:
            orders.append([user_id, search_url, last_scraped_id])

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(orders)


def remove_order(user_id: int) -> None:
    file_path = os.path.join(script_dir,"../orders.csv")
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        orders = list(reader)
        orders = [order for order in orders if order[0] != str(user_id)]

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(orders)

def save_only_new_realties(realties: list[dict], user_id: int) -> None:
    file_path = os.path.join(script_dir,f"../realties/{str(user_id)}.csv")

    file_exists = os.path.exists(file_path)
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_realties = list(reader)
            existing_ids = [int(realty["id"]) for realty in existing_realties if realty["user_id"] == str(user_id)]
    else:
        existing_ids = []
    new_realties = [realty for realty in realties if int(realty["id"]) not in existing_ids]
    for realty in new_realties:
        realty["read"] = "False"
        realty["user_id"] = str(user_id)
    if new_realties:
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=new_realties[0].keys(), quotechar='"', quoting=csv.QUOTE_ALL)
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_realties)

def update_realties_with_read(realties: list[dict], user_id:int) -> None:
    file_path = os.path.join(script_dir,f"../realties/{str(user_id)}.csv")
    realty_ids = [int(realty["id"]) for realty in realties]
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        realties = list(reader)
        for realty in realties:
            if int(realty["id"]) in realty_ids:
                realty["read"] = "True"
    if realties:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=realties[0].keys(), quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(realties)

def get_unread_realties(user_id:int) -> list[dict]:
    file_path = os.path.join(script_dir,f"../realties/{str(user_id)}.csv")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        realties = [realty for realty in reader if realty["read"] != "True"]
    return realties