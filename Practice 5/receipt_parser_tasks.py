import re
import json

def parse_receipt(text: str) -> dict:
    receipt = {}

    receipt["store"] = re.search(r"Филиал .+", text).group().strip()
    receipt["bin"] = re.search(r"БИН (\S+)", text).group(1)
    receipt["vat_series"] = re.search(r"НДС Серия (\S+)", text).group(1)
    receipt["receipt_number"] = re.search(r"№ (\d+)", text).group(1)
    receipt["cash_register"] = re.search(r"Касса (\S+)", text).group(1)
    receipt["shift"] = int(re.search(r"Смена (\d+)", text).group(1))
    receipt["sequential_number"] = int(re.search(r"Порядковый номер чека №(\d+)", text).group(1))
    receipt["check_number"] = re.search(r"Чек №(\d+)", text).group(1)
    receipt["cashier"] = re.search(r"Кассир (.+)", text).group(1).strip()
    receipt["operation_type"] = re.search(r"ПРОДАЖА|ВОЗВРАТ", text).group()

    dt_match = re.search(r"Время: (\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2})", text)
    receipt["date"] = dt_match.group(1)
    receipt["time"] = dt_match.group(2)

    location_match = re.search(r"г\..+?(?=\nОператор)", text, re.DOTALL)
    if location_match:
        receipt["location"] = " ".join(location_match.group().split())

    payment_match = re.search(r"(Банковская карта|Наличные):\s*([\d\s]+,\d{2})", text)
    if payment_match:
        receipt["payment_method"] = payment_match.group(1)
        receipt["payment_amount"] = float(payment_match.group(2).replace(" ", "").replace(",", "."))

    total_match = re.search(r"ИТОГО:\s*([\d\s]+,\d{2})", text)
    receipt["total"] = float(total_match.group(1).replace(" ", "").replace(",", ".")) if total_match else None

    vat_match = re.search(r"в т\.ч\. НДС \d+%:\s*([\d\s]+,\d{2})", text)
    receipt["vat_amount"] = float(vat_match.group(1).replace(" ", "").replace(",", ".")) if vat_match else 0.0

    items = []
    lines = text.split("\n")
    item_id_pattern = re.compile(r"^(\d+)\.$")
    qty_price_pattern = re.compile(r"^([\d\s]+,\d+)\s+x\s+([\d\s]+,\d{2})$")

    i = 0
    while i < len(lines):
        m = item_id_pattern.match(lines[i].strip())
        if m:
            item_id = int(m.group(1))
            i += 1
            name_lines = []
            while i < len(lines) and not qty_price_pattern.match(lines[i].strip()):
                name_lines.append(lines[i].strip())
                i += 1
            name_raw = " ".join(name_lines)
            is_rx = "[RX]" in name_raw
            name_clean = re.sub(r"\[RX\]-?", "", name_raw).strip()

            qp = qty_price_pattern.match(lines[i].strip())
            qty = float(qp.group(1).replace(" ", "").replace(",", "."))
            unit_price = float(qp.group(2).replace(" ", "").replace(",", "."))
            i += 1
            total_price = float(lines[i].strip().replace(" ", "").replace(",", "."))
            i += 1
            i += 1
            i += 1

            items.append({
                "id": item_id,
                "name": name_clean,
                "is_prescription": is_rx,
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": total_price,
            })
        else:
            i += 1

    receipt["items"] = items
    receipt["total_items"] = len(items)
    receipt["calculated_total"] = round(sum(item["total_price"] for item in items), 2)

    return receipt


def main():
    with open(r"C:\codes\raw.txt", "r", encoding="utf-8") as f:
        text = f.read()

    result = parse_receipt(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()