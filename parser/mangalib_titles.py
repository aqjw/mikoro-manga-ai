import requests
import sqlite3
from urllib.parse import urlencode

# SQLite database setup
DB_NAME = 'manga_data.db'

skip = [
  '7580--i-alone-level-up',
  '34466--jeonjijeog-dogja-sijeom_',
  '3754--sweet-home-kim-carnby-',
  '29916--ag-yeog-uiending-eunjug-eumppun',
  '7820--suddenly-became-a-princess-one-day-',
  '21955--white-blood_',
  '7771--contract-fiancee-of-the-duke',
  '44451--baegjagga-ui-mangnani-ga-doeeossda',
  '51952--true-education',
  '7072--eleceed-',
  '38359--ibeon-saeng-eun-gajuga-doegessseubnida',
  '32693--how-to-fight',
  '66256--namjuui-ib-yangttali-doeeossseubnida',
  '12668--dwaejiuri-',
  '55134--sssgeubjasalheonteo',
  '122897--jagjeonmyeong-sunjeong',
  '37931--olgami',
  '18151--remarried-empress',
  '12478--ranker-who-lives-a-second-time',
  '89759--nampyeon-eul-nae-pyeon-eulo-mandeuneun-bangbeob',
  '83360--naje-tteuneun-byol',
  '98877--nae-namphyeon-gwa-gyeolhon-haejwo',
  '89959--yeokdagp-yeongji-sulgyesa',
  '52347--ibhag-yongbyeong',
  '58022--agnyeo-leul-jug-yeojwo',
  '16443--medical-return',
  '28495--geu-agnyeoleul-josimhaseyo',
  '120437--gyeolhon-jangsa',
  '59278--hunting-rifle-boy-',
  '54835--tokkiwa-heugpyobeom-ui-gongsaeng-gwangye',
  '36842--agnyeoneun-malioneteu',
  '32686--legend-of-the-northern-blade',
  '7523--gwihwanjaui-mabeobeun-teugbyeolhaeya-habnida',
  '57771--agnyeolaseo-pyeonhago-joh-eundeyo',
  '14472--a-stepmothers-marchen',
  '20399--agnyeoui-namjunim',
  '94557--agdang-gwa-gyeyaggajog-i-doeeossda',
  '60127--a-surviving-romance-',
  '106580--eommaga-gyeyageolhon-haessda',
  '57751--hwasangwihwan-',
  '10770--jasal-ro-ss',
  '13282--law-of-insomnia-',
  '109096--kkum-eseo-jayulo',
  '16628--fff-level-of-interest',
  '44778--sangsulinamu-alae',
  '27353--god-of-blackfield',
  '78997--8keullaeseu-mabeobsaui-hoegwi',
  '12624--the-office-blind-date',
  '54257--gobge-kiwossdeoni-jmseung_',
  '65075--jangleuleul-bakkwobodolog-hagessseub-nida',
  '111095--hapiimyeon-kkamagwiga-doeeobeolyeossda',
  '61809--billeontukil',
  '83698--a-new-life-for-a-killer-of-the-gods',
  '48425--naneun-sindelellaleul-sojunghi-kiwossda',
  '104354--beolyeojin-naui-choeaeleul-wihayeo',
  '50668--heugmag-eul-beolineun-desilpaehaessda',
  '38782--cheongchun-beulla',
  '4867--queen-with-a-scalpel',
  '113982--bing-uijaleul-wihan-teughye',
  '86707--useon-namdongsaengbuteo-sumgija',
  '122925--goodbye-eri',
  '37712--agiga-saeng-gyeoss-eoyo',
  '26198--the_boxer',
  '57771--agnyeolaseo-pyeonhago-joh-eundeyo',
  '14472--a-stepmothers-marchen',
  '1357--vagabond',
  '20399--agnyeoui-namjunim',
  '94557--agdang-gwa-gyeyaggajog-i-doeeossda',
  '92695--dasi-han-beon-bich-sogeulo',
  '60127--a-surviving-romance-',
  '106580--eommaga-gyeyageolhon-haessda',
  '6435--kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen',
  '106336--naega-juggilo-gyeolsimhan-geos-eun',
  '57751--hwasangwihwan-',
  '3445--houseki-no-kuni',
  '10770--jasal-ro-ss',
  '195323--sokkubchingu-keompeullegseu',
  '86572--look-back',
  '2706--oemojisangjuui',
  '24394--wolf-and-dog',
  '13282--law-of-insomnia-',
  '4464--jujutsu-kaisen',
  '1288--yaoshenji',
  '109096--kkum-eseo-jayulo',
  '16628--fff-level-of-interest',
  '44778--sangsulinamu-alae',
  '27353--god-of-blackfield',
  '25--annarasumanara',
  '78997--8keullaeseu-mabeobsaui-hoegwi',
  '104639--my-family-is-obsessed-with-me',
  '701--horimiya',
  '2053--tensei-shitara-slime-datta-ken',
  '12624--the-office-blind-date',
  '54257--gobge-kiwossdeoni-jmseung_',
  '91067--amuteun-lopan-majseubnida',
  '65075--jangleuleul-bakkwobodolog-hagessseub-nida',
  '46835--nae-dongsaeng-geondeulmyeon-neohuineun-da-jug-eun-mogsum-ida',
  '60175--megane-tokidoki-yankee-kun',
  '106817--emo-shang-shang-qian',
  '111095--hapiimyeon-kkamagwiga-doeeobeolyeossda',
  '61809--billeontukil',
  '83698--a-new-life-for-a-killer-of-the-gods',
  '16260--cheating-men-must-die',
  '3940--jigoku-raku',
  '48425--naneun-sindelellaleul-sojunghi-kiwossda',
  '104354--beolyeojin-naui-choeaeleul-wihayeo',
  '50668--heugmag-eul-beolineun-desilpaehaessda',
  '34148--brutal-satsujin-kansatsukan-no-kokuhaku',
  '293--vinland-saga',
  '38782--cheongchun-beulla',
  '4867--queen-with-a-scalpel',
  '44143--geunyeowa-yasu',
  '41--kuroshitsuji',
  '1384--mushoku-tensei-isekai-ittara-honki-dasu',
  '3321--dorohedoro',
  '2990--ayeshahs-secret',
  '113982--bing-uijaleul-wihan-teughye',
  '86707--useon-namdongsaengbuteo-sumgija',
  '149396--jeo-geuleon-injae-anibnida',
  '10953--akuyaku-reijo-nano-de-last-boss-wo-kattemimashita',
  '17080--geumbal-ui-jeonglyeongsa',
  '57093--aisha',
  '69506--sikeulis-leidi',
  '27192--i-adopted-a-robber',
  '18621--return-to-survive-',
  '29759--oshi-no-ko',
  '2262--oyasumi-punpun',
  '285--tower-of-god',
  '36410--nanomasin',
  '46423--yeoghalem-geim-sog-eulo-tteol-eojin-moyang-ibnida',
  '46846--sasil-eun-naega-jinjja-yeossda',
  '2025--dr-stone',
  '657--toukyou-kushu-re',
]

def setup_database():
    """Sets up the SQLite database and creates the manga table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manga (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_rus TEXT,
        slug_url TEXT,
        is_parsed INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    return conn, cursor


def build_url(base_url, params):
    """Builds a full URL with query parameters."""
    return f"{base_url}?{urlencode(params, doseq=True)}"


def fetch_and_save_manga(cursor, headers, base_url):
    """Fetches manga data from API and saves it to the database."""
    for page in range(1, 20):
        response = requests.get(f"{base_url}&page={page}", headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        json_data = response.json()
        data = json_data.get('data', [])
        for item in data:
            name = item.get('rus_name')
            slug = item.get('slug_url')
            parsed = 1 if slug in skip else 0
            # print('parsed', parsed, slug)
            cursor.execute('INSERT INTO manga (name_rus, slug_url, is_parsed) VALUES (?, ?, ?)', (name, slug, parsed))

        meta = json_data.get('meta', {})
        print(f"Saved {len(data)} records to the database. Page: {page}")


def main():
    # Database setup
    conn, cursor = setup_database()

    # API setup
    BASE_URL = 'https://api2.mangalib.me/api/manga'
    PARAMS = {
        'caution[]': [3, 2],
        'chap_count_min': 50,
        'fields[]': ['rate', 'rate_avg', 'userBookmark'],
        'format[]': [7],
        'scanlate_status[]': [1, 2, 3],
        'site_id[]': [1],
        'types[]': [5],
        'year_min': 2015
    }
    HEADERS = {
        'sec-ch-ua-platform': '"macOS"',
        'Referer': 'https://mangalib.me/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'Site-Id': '1',
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/131.0.0.0 Safari/537.36'
        ),
        'DNT': '1',
        'Content-Type': 'application/json',
    }

    # Fetch and save manga
    # full_url = build_url(BASE_URL, PARAMS)
    full_url = ('https://api2.mangalib.me/api/manga?caution[]=1&caution[]=2&caution[]=3&chap_count_min=50&fields['
                ']=rate&fields[]=rate_avg&fields[]=userBookmark&format[]=7&format[]=4&scanlate_status['
                ']=1&scanlate_status[]=2&scanlate_status[]=3&seed=49ff737a822e28b7a2937d54f039169a&site_id[]=1&types['
                ']=5&year_min=2015')
    fetch_and_save_manga(cursor, HEADERS, full_url)

    # Close database connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()


