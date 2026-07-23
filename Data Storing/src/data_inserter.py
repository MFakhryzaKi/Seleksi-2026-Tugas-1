import json
import re
import pymysql
from getpass import getpass
from pathlib import Path

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "data_inserter",
    "password": "",
    "database": "MobileLegends",
    "charset": "utf8mb4",
}

HEROES_JSON = Path(__file__).resolve().parent.parent.parent / "Data Scraping" / "data" / "list_of_heroes.json"
STATS_JSON =   Path(__file__).resolve().parent.parent.parent / "Data Scraping" / "data" / "hero_statistics.json"

def parsePrice(price):
    parts = price.strip().split(" ", 1)
    
    amount = int(parts[0]) if parts[0].isdigit() else parts[0]
    
    currency = parts[1] if len(parts) > 1 else ""
    
    return amount, currency

def turnToNumber (value) :
    if (isinstance(value, int) or isinstance(value, float)) :
        return value
    return None

def parsePercent(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.replace("%", "").strip()
    return value

def parse_date(value: str) :
    # Dictionary pemetaan nama bulan Indonesia ke angka
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "oktober": 10, "november": 11, "december": 12
    }
    
    elements = value.strip().split(" ")
    
    day = 1
    month = 1
    year = 1
    
    if len(elements) == 3:
        day = int(elements[0])
        # Ambil angka bulan dari dict (jika tidak ketemu, default ke 1)
        month = months.get(elements[1].lower(), 1)
        year = int(elements[2])
        
    elif len(elements) == 2:
        month = months.get(elements[0].lower(), 1)
        year = int(elements[1])
        
    elif len(elements) == 1:
        year = int(elements[0])
        
    return f"{year:04d}-{month:02d}-{day:02d}"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main () :
    heroes_data = load_json(HEROES_JSON)["heroes"]
    stats_data = load_json(STATS_JSON)["heroes"]

    while (True) :
        password = getpass("Masukkan Password MariaDB: ")
        DB_CONFIG["password"] = password
        try :
            conn = pymysql.connect(**DB_CONFIG)
            break
        except pymysql.err.OperationalError as e:
            if e.args and e.args[0] == 1045:
                print("Password salah, silakan ulangi!")
            else:
                print(f"Koneksi ke MariaDB gagal: {e}")
                raise
        except Exception as e:
            print(f"Koneksi ke MariaDB gagal: {e}")
            raise

    try :
        with conn.cursor() as cur:
            # Bersihin dulu semua tabel kalo ada isinya

            for statement in [
                "DELETE FROM Hero_Price",
                "DELETE FROM Hero_Lane_Recommendation",
                "DELETE FROM Hero_Specialty",
                "DELETE FROM Hero_Role",
                "DELETE FROM Statistics",
                "DELETE FROM Hero",
            ]:
                cur.execute(statement)

            # tabel hero
            hero_sql = """
                INSERT INTO Hero (hero_order, hero_name, hero_alias, region_of_origin, release_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            for h in heroes_data :
                cur.execute(hero_sql, (
                    h["hero_order"],
                    h.get("hero_name"),
                    h.get("hero_alias"),
                    h.get("region_of_origin"),
                    parse_date(h.get("release_date")),
                ))

            # tabel hero_role
            role_sql = """
                INSERT INTO Hero_Role (hero_order, role)
                VALUES (%s, %s)
            """

            for h in heroes_data : 
                for role in h.get("roles", []) or [] :
                    cur.execute (role_sql, (h["hero_order"], role))

            # tabel hero_specialty
            specialty_sql = """
                INSERT INTO Hero_Specialty (hero_order, specialty)
                VALUES (%s, %s)
            """

            for h in heroes_data : 
                for specialty in h.get("specialties", []) or [] :
                    cur.execute (specialty_sql, (h["hero_order"], specialty))

            # tabel hero_lane_recommendation
            lane_sql = """
                INSERT INTO Hero_Lane_Recommendation (hero_order, lane_recommendation)
                VALUES (%s, %s)
            """

            for h in heroes_data : 
                for lane in h.get("lane_recommendations", []) or [] :
                    cur.execute (lane_sql, (h["hero_order"], lane))

            # tabel hero_price
            price_sql = """
                INSERT INTO Hero_Price (hero_order, currency, amount)
                VALUES (%s, %s, %s)
            """

            for h in heroes_data : 
                for price in h.get("prices", []) or [] :
                    amount, currency = parsePrice (price)
                    # print (price)
                    # print (currency)
                    # print (amount)
                    cur.execute (price_sql, (h["hero_order"], currency, int(amount)))

            # tabel statistics
            stats_sql = """
                INSERT INTO Statistics (
                    hero_order, base_hp, hp_growth, base_mana, mana_growth,
                    base_mana_regen, mana_regen_growth,
                    base_physical_attack, physical_attack_growth,
                    base_magic_power, magic_power_growth,
                    base_physical_defense, physical_defense_growth,
                    base_magic_defense, magic_defense_growth,
                    base_attack_speed, attack_speed_growth,
                    attack_speed_ratio, critical_damage,
                    movement_speed, basic_attack_range
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for s in stats_data : 
                cur.execute(stats_sql, (
                    s["hero_order"],
                    turnToNumber(s.get("base_hp")),
                    turnToNumber(s.get("hp_growth")),
                    turnToNumber(s.get("base_mana")),
                    turnToNumber(s.get("mana_growth")),
                    turnToNumber(s.get("base_mana_regen")),
                    turnToNumber(s.get("mana_regen_growth")),
                    turnToNumber(s.get("base_physical_attack")),
                    turnToNumber(s.get("physical_attack_growth")),
                    turnToNumber(s.get("base_magic_power")),
                    turnToNumber(s.get("magic_power_growth")),
                    turnToNumber(s.get("base_physical_defense")),
                    turnToNumber(s.get("physical_defense_growth")),
                    turnToNumber(s.get("base_magic_defense")),
                    turnToNumber(s.get("magic_defense_growth")),
                    turnToNumber(s.get("base_attack_speed")),
                    turnToNumber(s.get("attack_speed_growth")),
                    turnToNumber(parsePercent(s.get("attack_speed_ratio"))),
                    turnToNumber(parsePercent(s.get("critical_damage"))),
                    turnToNumber(s.get("movement_speed")),
                    turnToNumber(s.get("basic_attack_range"))
                ))
                # print (parsePercent(s.get("attack_speed_ratio")))
                # print (parsePercent(s.get("critical_damage")))

        conn.commit()
        print("✅ Import selesai:")
        print(f"   - {len(heroes_data)} hero dimasukkan ke tabel Hero")
        print(f"   - {len(stats_data)} baris statistik dimasukkan ke tabel Statistics")

            
    except Exception as e:
        conn.rollback()
        print("❌ Terjadi error, transaksi di-rollback:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__" :
    main()