import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
import requests


SOURCE_PAGE = "List_of_heroes"
API_URL = "https://mobile-legends.fandom.com/api.php"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "list_of_heroes.json"
STATISTICS_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "hero_statistics.json"


def build_session() -> requests.Session:
	session = requests.Session()
	session.headers.update(
		{
			"User-Agent": (
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
				"AppleWebKit/537.36 (KHTML, like Gecko) "
				"Chrome/126.0.0.0 Safari/537.36"
			),
			"Accept": "application/json,text/plain,*/*",
			"Accept-Language": "en-US,en;q=0.9,id;q=0.8",
			"Cache-Control": "no-cache",
			"Pragma": "no-cache",
			"Referer": "https://mobile-legends.fandom.com/wiki/List_of_heroes",
			"Connection": "keep-alive",
		}
	)
	return session


def fetch_hero_table_html(session: requests.Session) -> str:
	response = session.get(
		API_URL,
		params={
			"action": "parse",
			"page": SOURCE_PAGE,
			"prop": "text|wikitext",
			"format": "json",
			"formatversion": 2,
		},
		timeout=30,
	)
	response.raise_for_status()
	payload = response.json()
	parse_data = payload.get("parse")
	if not parse_data:
		raise RuntimeError(f"API tidak mengembalikan data parse: {payload}")

	text_data = parse_data.get("text")
	if isinstance(text_data, dict):
		return text_data.get("*", "")
	if isinstance(text_data, str):
		return text_data
	raise RuntimeError("Format respons API tidak dikenali.")


def fetch_hero_page_html(session: requests.Session, page_title: str) -> str:
	response = session.get(
		API_URL,
		params={
			"action": "parse",
			"page": page_title,
			"prop": "text|wikitext",
			"format": "json",
			"formatversion": 2,
		},
		timeout=30,
	)
	response.raise_for_status()
	payload = response.json()
	parse_data = payload.get("parse")
	if not parse_data:
		raise RuntimeError(f"API tidak mengembalikan data parse untuk {page_title}: {payload}")

	text_data = parse_data.get("text")
	if isinstance(text_data, dict):
		return text_data.get("*", "")
	if isinstance(text_data, str):
		return text_data
	raise RuntimeError(f"Format respons API tidak dikenali untuk {page_title}.")


def normalize_text(value: str) -> str:
	return " ".join(value.split())


def normalize_page_title(hero_link: str | None) -> str | None:
	if not hero_link:
		return None
	path = urlparse(hero_link).path if hero_link.startswith("http") else hero_link
	if "/wiki/" not in path:
		return None
	return unquote(path.split("/wiki/", 1)[1]).strip("/")


def parse_stat_value(value: str) -> str | int | float | None:
	normalized = normalize_text(value)
	if not normalized:
		return None
	match = re.match(r"^([-+]?\d+(?:\.\d+)?)(%?)$", normalized)
	if match:
		number_text, percent_suffix = match.groups()
		if percent_suffix:
			return normalized
		if "." in number_text:
			return float(number_text)
		return int(number_text)

	leading_number = re.match(r"^([-+]?\d+(?:\.\d+)?)", normalized)
	if leading_number:
		number_text = leading_number.group(1)
		if "." in number_text:
			return float(number_text)
		return int(number_text)

	return normalized


def parse_prices(cell: BeautifulSoup) -> list[str]:
	prices: list[str] = []
	for item in cell.select("li"):
		image = item.find("img")
		if image and image.get("alt"):
			prices.append(normalize_text(image["alt"]))
			continue
		text = normalize_text(item.get_text(" ", strip=True))
		if text:
			prices.append(text)
	return prices


def parse_hero_stat_rows(html: str) -> dict[str, str | int | float | None]:
	soup = BeautifulSoup(html, "html.parser")
	stat_table = None
	for table in soup.select("table.wikitable"):
		if "hero stats" in normalize_text(table.get_text(" ", strip=True)).lower():
			stat_table = table
			break

	if stat_table is None:
		raise RuntimeError("Tabel hero stats tidak ditemukan pada halaman hero.")

	stats: dict[str, str | int | float | None] = {}
	for row in stat_table.select("tbody tr"):
		cells = row.find_all("td")
		if not cells:
			continue

		label = normalize_text(cells[0].get_text(" ", strip=True)).split("(", 1)[0].strip()
		values = [normalize_text(cell.get_text(" ", strip=True)) for cell in cells[1:]]
		if not values:
			continue

		if label == "HP":
			stats["base_hp"] = parse_stat_value(values[0])
			stats["hp_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Mana":
			stats["base_mana"] = parse_stat_value(values[0])
			stats["mana_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Mana Regen":
			stats["base_mana_regen"] = parse_stat_value(values[0])
			stats["mana_regen_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Physical Attack":
			stats["base_physical_attack"] = parse_stat_value(values[0])
			stats["physical_attack_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Magic Power":
			stats["base_magic_power"] = parse_stat_value(values[0])
			stats["magic_power_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Physical Defense":
			stats["base_physical_defense"] = parse_stat_value(values[0])
			stats["physical_defense_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Magic Defense":
			stats["base_magic_defense"] = parse_stat_value(values[0])
			stats["magic_defense_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Attack Speed":
			stats["base_attack_speed"] = parse_stat_value(values[0])
			stats["attack_speed_growth"] = parse_stat_value(values[2]) if len(values) >= 3 else None
		elif label == "Attack Speed Ratio":
			stats["attack_speed_ratio"] = parse_stat_value(values[0])
		elif label == "Critical Damage":
			stats["critical_damage"] = parse_stat_value(values[0])
		elif label == "Movement Speed":
			stats["movement_speed"] = parse_stat_value(values[0])
		elif label == "Basic Attack range":
			stats["basic_attack_range"] = parse_stat_value(values[0])

	return stats


def parse_hero_rows(html: str) -> list[dict[str, object]]:
	soup = BeautifulSoup(html, "html.parser")
	table = soup.select_one("table.wikitable.sortable")
	if table is None:
		raise RuntimeError("Tabel hero tidak ditemukan pada hasil API.")

	heroes: list[dict[str, object]] = []
	for row in table.select("tbody tr"):
		cells = row.find_all("td")
		if len(cells) < 10:
			continue

		_, icon_cell, hero_cell, order_cell, role_cell, specialty_cell, lane_cell, region_cell, price_cell, release_cell = cells[:10]
		icon_link = icon_cell.find("a")
		icon_image = icon_cell.find("img")
		hero_link = hero_cell.find("a")
		hero_name = normalize_text(hero_cell.get_text(" ", strip=True))
		hero_page_title = normalize_text(hero_name.split(",", 1)[0])

		heroes.append(
			{
				"hero_order": int(normalize_text(order_cell.get_text(" ", strip=True))),
				"hero_name": hero_name,
				"hero_alias": normalize_text(hero_name.split(",", 1)[1]),
				# "hero_link": f"/wiki/{hero_page_title.replace(' ', '_')}",
				# "hero_icon": icon_image.get("alt") if icon_image else None,
				"roles": [normalize_text(part) for part in role_cell.get_text("/", strip=True).split("/") if normalize_text(part)],
				"specialties": [normalize_text(part) for part in specialty_cell.get_text("/", strip=True).split("/") if normalize_text(part)],
				"lane_recommendations": [normalize_text(part) for part in lane_cell.get_text("/", strip=True).split("/") if normalize_text(part)],
				"region_of_origin": normalize_text(region_cell.get_text(" ", strip=True)),
				"prices": parse_prices(price_cell),
				"release_date": normalize_text(release_cell.get_text(" ", strip=True)),
			}
		)

	return heroes


def main() -> None:
	print("scraping...")
	session = build_session()
	try:
		print("parsing heroes...")
		html = fetch_hero_table_html(session)
		heroes = parse_hero_rows(html)
	except Exception as exc:
		print(f"Gagal mengambil data hero lewat API: {exc}")
		return

	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	hero_statistics: list[dict[str, object]] = []
	payload = {
		"source_url": f"{API_URL}?action=parse&page={SOURCE_PAGE}&prop=text%7Cwikitext&format=json&formatversion=2",
		"scraped_from": "Fandom MediaWiki parse API",
		"hero_count": len(heroes),
		"heroes": heroes,
	}
	with OUTPUT_PATH.open("w", encoding="utf-8") as file:
		json.dump(payload, file, ensure_ascii=False, indent=2)

	print("parsing hero stats...")
	for hero in heroes:
		# page_title = normalize_page_title(hero.get("hero_link") if isinstance(hero.get("hero_link"), str) else None)
		link = f"/wiki/{normalize_text(hero.get("hero_name").split(",", 1)[0]).replace(' ', '_')}"
		page_title = normalize_page_title(link)
		if not page_title:
			continue

		try:
			hero_html = fetch_hero_page_html(session, page_title)
			stats = parse_hero_stat_rows(hero_html)
		except Exception as exc:
			print(f"Gagal mengambil statistik untuk {page_title}: {exc}")
			continue

		hero_statistics.append(
			{
				"hero_order": hero["hero_order"],
				**stats,
			}
		)

	with STATISTICS_OUTPUT_PATH.open("w", encoding="utf-8") as file:
		json.dump(
			{
				"source_url": f"{API_URL}?action=parse&page={SOURCE_PAGE}&prop=text%7Cwikitext&format=json&formatversion=2",
				"scraped_from": "Fandom MediaWiki parse API",
				"hero_count": len(hero_statistics),
				"heroes": hero_statistics,
			},
			file,
			ensure_ascii=False,
			indent=2,
		)

	print(f"Berhasil menyimpan {len(heroes)} hero ke {OUTPUT_PATH}")
	print(f"Berhasil menyimpan statistik {len(hero_statistics)} hero ke {STATISTICS_OUTPUT_PATH}")


if __name__ == "__main__":
	main()
