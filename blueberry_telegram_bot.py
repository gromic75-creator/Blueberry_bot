"""
🫐 BlueberryBot v2.0 — Global Highbush Blueberry Market Intelligence
"""

import os
import logging
import json
import base64
from datetime import datetime
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

LANGUAGES = {
    "en": "🇬🇧 English",
    "pl": "🇵🇱 Polski",
    "de": "🇩🇪 Deutsch",
    "es": "🇪🇸 Español",
    "ru": "🇷🇺 Русский",
}

WELCOME = {
    "en": "🫐 *BlueberryBot v2.0* — Global Highbush Blueberry Market Intelligence\n\n📊 Data: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Tip:* Type your country name for variety advice!\n📸 *Send a photo* — variety ID + disease diagnosis!\n\nChoose a topic or ask me anything!",
    "pl": "🫐 *BlueberryBot v2.0* — Globalny Wywiad Rynku Borówki Amerykańskiej\n\n📊 Dane: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Wskazówka:* Napisz kraj aby dostać rekomendacje odmian!\n📸 *Wyślij zdjęcie* — rozpoznanie odmiany + diagnoza chorób!\n\nWybierz temat lub zadaj pytanie!",
    "de": "🫐 *BlueberryBot v2.0* — Globale Heidelbeer-Marktintelligenz\n\n📊 Daten: IBO · FreshPlaza · USDA · 2025/26\n\nThema wählen oder Frage stellen!",
    "es": "🫐 *BlueberryBot v2.0* — Inteligencia del Mercado Global de Arándanos\n\n📊 Datos: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n¡Elige un tema o pregunta lo que quieras!",
    "ru": "🫐 *BlueberryBot v2.0* — Глобальная аналитика рынка голубики\n\n📊 Данные: IBO · FreshPlaza · USDA · 2025/26\n\nВыберите тему или задайте вопрос!",
}

MENU_LABELS = {
    "en": {
        "market":       "📊 Global Market",
        "production":   "🌍 Production by Country",
        "export":       "🚢 Export Leaders",
        "destinations": "🎯 Key Markets",
        "prices":       "💰 Market Prices 2025/26",
        "varieties":    "🌱 New Varieties",
        "classics":     "📚 Classic Varieties",
        "nursery":      "🏭 Nursery & Plants",
        "news":         "📰 Breaking News",
        "photo":        "📸 Photo Analysis",
        "currency":     "💱 Currency & Prices",
        "health":       "🏥 Health Benefits",
        "search":       "🔍 Live Search",
        "lang":         "🌐 Language",
    },
    "pl": {
        "market":       "📊 Rynek globalny",
        "production":   "🌍 Produkcja wg kraju",
        "export":       "🚢 Liderzy eksportu",
        "destinations": "🎯 Kluczowe rynki",
        "prices":       "💰 Ceny rynkowe 2025/26",
        "varieties":    "🌱 Nowe odmiany",
        "classics":     "📚 Klasyczne odmiany",
        "nursery":      "🏭 Szkółki i sadzonki",
        "news":         "📰 Aktualności",
        "photo":        "📸 Analiza zdjęcia",
        "currency":     "💱 Waluty i ceny",
        "health":       "🏥 Właściwości zdrowotne",
        "search":       "🔍 Wyszukiwanie live",
        "lang":         "🌐 Język",
    },
    "de": {
        "market":       "📊 Globaler Markt",
        "production":   "🌍 Produktion nach Land",
        "export":       "🚢 Export-Führer",
        "destinations": "🎯 Schlüsselmärkte",
        "prices":       "💰 Marktpreise 2025/26",
        "varieties":    "🌱 Neue Sorten",
        "classics":     "📚 Klassische Sorten",
        "nursery":      "🏭 Baumschulen & Pflanzen",
        "news":         "📰 Aktuelle News",
        "photo":        "📸 Foto-Analyse",
        "currency":     "💱 Währung & Preise",
        "health":       "🏥 Gesundheitsvorteile",
        "search":       "🔍 Live-Suche",
        "lang":         "🌐 Sprache",
    },
    "es": {
        "market":       "📊 Mercado global",
        "production":   "🌍 Producción por país",
        "export":       "🚢 Líderes exportación",
        "destinations": "🎯 Mercados clave",
        "prices":       "💰 Precios mercado 2025/26",
        "varieties":    "🌱 Nuevas variedades",
        "classics":     "📚 Variedades clásicas",
        "nursery":      "🏭 Viveros y plantas",
        "news":         "📰 Noticias",
        "photo":        "📸 Análisis de foto",
        "currency":     "💱 Divisas y precios",
        "health":       "🏥 Beneficios salud",
        "search":       "🔍 Búsqueda en vivo",
        "lang":         "🌐 Idioma",
    },
    "ru": {
        "market":       "📊 Мировой рынок",
        "production":   "🌍 Производство по странам",
        "export":       "🚢 Лидеры экспорта",
        "destinations": "🎯 Ключевые рынки",
        "prices":       "💰 Рыночные цены 2025/26",
        "varieties":    "🌱 Новые сорта",
        "classics":     "📚 Классические сорта",
        "nursery":      "🏭 Питомники и саженцы",
        "news":         "📰 Новости",
        "photo":        "📸 Анализ фото",
        "currency":     "💱 Валюты и цены",
        "health":       "🏥 Польза для здоровья",
        "search":       "🔍 Поиск в реальном времени",
        "lang":         "🌐 Язык",
    },
}

BLUEBERRY_KNOWLEDGE = """
BLUEBERRY KNOWLEDGE BASE — VERIFIED 2025/26 DATA
Sources: IBO, FreshPlaza, USDA, Proarándanos, Blueberries Consulting

CRITICAL: This bot covers ONLY cultivated HIGHBUSH BLUEBERRY (Vaccinium corymbosum).
NOT wild bilberry (jagoda lesna / czarna jagoda). Completely different fruits!

SECTION 1: GLOBAL MARKET 2025/26
- Global production 2024: exceeded 2.0 million MT first time in history
- Global export 2024: 1,000,000 MT, value $6.73 billion (IBO)
- Cultivation area 2023: 267,000 ha (+7.2%)
- Latin America: 42% of world acreage
- IBO forecast: 2.5 billion kg fresh by 2029

SECTION 2: PRODUCTION BY COUNTRY
China #1 producer (domestic only!), Peru #1 EXPORTER.

1. China: 570,000-780,000 MT — Guizhou, Jilin, Yunnan — DOMESTIC ONLY
2. USA: 358,000 MT — Washington, Oregon, Georgia — value $1.15B farm gate
3. Peru: 320,000-412,000 MT — La Libertad 51%, Lambayeque 23% — #1 EXPORTER
4. Canada: 170,000 MT — British Columbia highbush
5. Chile: 150,000 MT — Biobio, Araucania
6. Morocco: 83,000 MT (record!) — rose from 7th to 4th exporter
7. Spain: 110,000 MT — Huelva (Andalusia) 90%
8. Poland: 75,000-80,000 MT — Mazovia, Lublin — largest EU producer
9. Mexico: 65,000-70,000 MT — Jalisco, Baja California
10. South Africa: 35,000 MT
11. Portugal: 25,000 MT
12. Ukraine: 25,000 MT
13. Australia: 20,000 MT
14. Argentina: 18,000 MT
15. Germany: 12,000 MT
16. Russia: 15,000 MT cultivated
17. Serbia: 6,000-7,000 MT (Duke 90%)
18. Georgia (country): 7,500 MT, 95% exported, May-June season
19. Romania: growing, Sekoya varieties planted 2021+
20. Zimbabwe: emerging

SECTION 3: EXPORT DATA 2024
Total: 1,000,000 MT, $6.73 billion
1. Peru: 31% (310,000 MT), $2.56B
2. Chile: 8% (80,000 MT)
3. Spain: 8% (80,000 MT)
4. Morocco: 8% (83,000 MT) — rose from 7th!
5. USA: 7% (70,000 MT)
6. Poland: 5% (50,000 MT)
7. Mexico: 2.3% (23,000 MT, +13%)
8. Canada: 3%

PERU 2025/26 FINAL: 380,260 MT (+21.5%), $2.56B
- USA: 150,673 MT (+3%), Europe: 91,926 MT (+36%), China: 43,935 MT (+153%!)

SECTION 4: KEY IMPORT MARKETS
USA: largest importer 200,000+ MT/year
China: fastest growing +25%/year, 80,000-100,000 MT, loves Sekoya Pop and Ventura
Europe: Netherlands hub, Morocco(Feb-Apr)→Spain(Apr-Jun)→Poland(Jul-Sep)→S.Hemisphere(Nov-Mar)
Russia: post-2022 mainly Belarus, Azerbaijan, China, Iran

SECTION 5: PRICES 2025/26 (VERIFIED)
Serbia farm gate June 2026: EUR 5-7/kg (DROPPING to 4-5 at peak)
Poland wholesale Bronisze June 2026: tunnel 20-45 PLN/kg, import 30-40 PLN/kg
Peru FOB: $4.19/kg (March 2026)
Netherlands wholesale: $4.06/kg (March 2026)
Belgium: $6.51/kg (Dec 2025)
China: $6.79/kg (Q1 2026 — highest globally)
USA: $4.41/kg (March 2026)
Retail: USA $8-16/kg, Germany EUR 12-24/kg, Poland 45-70 PLN/kg, China 80-200 CNY/kg
Frozen bulk EU: EUR 0.90-1.50/kg
TREND: Global downward pressure, oversupply warning from IBO

SECTION 6: VARIETIES — NEW (post-2020)
SEKOYA platform (Fall Creek): B2B, 15 members, 25 countries, 87,000 MT target
- LOW-CHILL (Peru, Mexico, Morocco, warm): Pop (China fav 24%), Beauty, Crunch, Grande
- HIGH-CHILL (Poland, Canada, cold): Nova FC15-173, ArabellaBlue FC14-062, LoretoBlue, Apex FCM14-057 (2026)
- Mechanical harvest: FC11-164 (trials Europe/US/Chile)

BLUE WORLD / DEMBA (Onubafruit/FV.BV Netherlands):
- Demba (FV1908) + Dana (FV1907) = Superior Taste Award winners
- Range: Demba, Dana, Aila, Lena, Selma, Selena
- EU protection until 2056, 25-30 t/ha, Huelva season Nov-June

PLANASA (Spain): Blue Manila, Malibu, Madeira, Maldiva, Marina, Masirah — zero chill
BerryWorld Orb: new northern highbush 2025
PeachyBlue: retail hit USA 2025

PERU TOP VARIETIES 2024/25: Ventura 26% (EU fav), Biloxi 16% (declining), Sekoya Pop 14% (China), Magica 19% (China)

CLASSIC VARIETIES (pre-2020):
Northern Highbush (high chill 800-1200h): Bluecrop, Duke, Draper, Aurora, Liberty, Chandler, Elliott, Patriot
Southern Highbush (low chill 200-500h): Biloxi, Ventura, O'Neal, Misty, Emerald, Jewel, Star
Half-High (extreme cold -35C): Northblue, Polaris, Chippewa

SECTION 7: NURSERIES TOP 5
1. Fall Creek USA: 40M+ plants/yr, 59 countries, SEKOYA platform, Peru (14M) + Spain (14M) hubs
2. Planasa Spain: 1B plants/yr total, 7000 staff, 27 countries, Blue Manila/Madeira/Maldiva
3. Onubafruit/FV.BV: Blue World varieties (Demba, Dana)
4. Oregon Blueberry USA: largest N.America wholesale
5. Lorsena Spain: EU specialist
Costs: plug $0.50-2.00, finished plant $2-5

SECTION 8: BREAKING NEWS JUNE 2026
Serbia: PEAK season, Duke 90%, prices EUR 6.50→4.00-5.00/kg (dropping fast), labor +12-15%
Romania: season starting June 15, first Sekoya volumes 450-500 MT
Poland: frost damage April-May 2026 (coldest May in 34 years), tunnel borówki 20-45 PLN, field July
Georgia (country): active May-June, 7,500 MT, 95% export to Germany/Poland/Russia/Dubai
Europe supply: Spain ending, Morocco done, Serbia PEAK, Romania starting, Poland/Germany July
Global IBO 5 trends: year-round quality, climate resilience, post-harvest innovation, mechanical harvesting, premium vs commodity segmentation

SECTION 9: HEALTH BENEFITS
ORAC: 9,621 umol TE/100g (highest common fruits)
Anthocyanins: malvidin, delphinidin, cyanidin, petunidin, peonidin
Brain: -26% cognitive decline (Harvard 2012, 16,000 women)
Heart: -32% heart attack risk, -4-6mmHg blood pressure
Diabetes: GI 53, improves insulin sensitivity
Cancer: anthocyanins inhibit tumor growth (colon, breast, liver)
Eyes: lutein, zeaxanthin protect macular degeneration
Gut: prebiotic fiber, polyphenols feed good bacteria
Sports: reduce muscle damage, faster recovery (300g before exercise)
Per 100g: 57 kcal, 14.5g carbs, 2.4g fiber, Vit C 9.7mg
Frozen retains 90%+ antioxidants
"""

PHOTO_SYSTEM = """You are a world-class blueberry expert: plant pathologist, variety specialist, and quality control inspector.

Analyze the photo and respond with:

1. WHAT YOU SEE: berries / leaves / plant / combination

2. IF BERRIES VISIBLE — VARIETY ID:
Visual clues: size, color, bloom (waxy coat), crown/calyx, shape
- Large firm light blue heavy bloom small crown: likely Draper/Duke
- Very large light blue: Chandler/Aurora
- Large deep blue exceptional bloom very firm: Sekoya Pop/Crunch/Ventura
- Medium powder blue loose clusters: Biloxi
- Large dark blue excellent flavor: O'Neal/Liberty
- Pink/red: Pink Lemonade/PeachyBlue
State: MOST LIKELY: [variety] | CONFIDENCE: HIGH/MEDIUM/LOW + why

3. QUALITY CONTROL (if berries):
Size grade: Jumbo >22mm / Large 18-22mm / Medium 14-18mm / Small <14mm
Bloom: Heavy (premium) / Light / None (degraded)
Defects found: Category A (reject): Botrytis, mummies, cracks, bird damage, bruising
              Category B (downgrade): scarring, russeting, misshapen, sunburn
              Category C (minor): size variation, light marks
Brix estimate (visual ±2): deep blue heavy bloom firm = 12-15 Brix; medium blue = 10-12; light blue red = 8-10

4. IF PLANT/LEAVES — DISEASE DIAGNOSIS:
FUNGAL: Botrytis (gray mold), Mummyberry, Anthracnose, Powdery Mildew, Phytophthora root rot, Stem Blight, Rust
BACTERIAL: Crown Gall, Bacterial Canker
VIRAL: Shock Virus, Scorch Virus, Stunt, Red Ringspot
PESTS: Spotted Wing Drosophila (critical!), Blueberry Maggot, Spider Mites, Aphids, Thrips, Scale
NUTRIENTS: Fe (interveinal chlorosis young leaves, pH!), Mg (older leaves), N (pale), K (brown margins), Ca (tipburn), B (hollow berries), Zn (small leaves)
ABIOTIC: Frost, Hail, Drought, Herbicide drift

For each issue: Severity (mild/moderate/severe) + Treatment + Prevention

5. PROGNOSIS and next steps

Always respond in {lang_name} ONLY. Be specific and practical."""

def build_system_prompt(lang: str) -> str:
    lang_name = {"en": "English", "pl": "Polish", "de": "German", "es": "Spanish", "ru": "Russian"}.get(lang, "English")
    return f"""{BLUEBERRY_KNOWLEDGE}

RULES:
1. Always respond in {lang_name}. No exceptions.
2. Topic: HIGHBUSH BLUEBERRY only. NOT wild bilberry.
3. Distinguish PRODUCTION vs EXPORT. China #1 producer (domestic), Peru #1 exporter.
4. Use knowledge base above. Web search for missing/latest data.
5. Emojis, bold headers, tables for data.
6. Cite sources and season/year.
7. COUNTRY ADVISOR: country name → chill hours, best new + classic varieties, regions, profitability, avoid list.
8. NEW varieties = Sekoya/Demba/Blue World/Planasa Blue (post-2020). CLASSIC = pre-2020.
"""

# ── Analytics ──────────────────────────────────────────────────────────────
STATS_FILE = "/tmp/blueberry_stats.json"

def load_stats():
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except:
        return {"users": {}, "topics": {}, "questions": [], "total": 0, "countries": {}}

def save_stats(s):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(s, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Stats save error: {e}")

LANG_TO_COUNTRY = {
    "pl": "🇵🇱 Poland", "de": "🇩🇪 Germany", "en": "🇬🇧 EN/US/AU",
    "ru": "🇷🇺 Russia", "uk": "🇺🇦 Ukraine", "es": "🇪🇸 Spain/LATAM",
    "fr": "🇫🇷 France", "it": "🇮🇹 Italy", "nl": "🇳🇱 Netherlands",
    "pt": "🇵🇹 Portugal/Brazil", "ro": "🇷🇴 Romania", "sr": "🇷🇸 Serbia",
    "tr": "🇹🇷 Turkey", "ar": "🇸🇦 Arabic", "zh": "🇨🇳 China",
    "ja": "🇯🇵 Japan", "ko": "🇰🇷 Korea", "cs": "🇨🇿 Czech",
    "sk": "🇸🇰 Slovakia", "hu": "🇭🇺 Hungary", "bg": "🇧🇬 Bulgaria",
    "hr": "🇭🇷 Croatia", "sl": "🇸🇮 Slovenia", "sv": "🇸🇪 Sweden",
    "no": "🇳🇴 Norway", "da": "🇩🇰 Denmark", "fi": "🇫🇮 Finland",
    "he": "🇮🇱 Israel", "fa": "🇮🇷 Iran", "be": "🇧🇾 Belarus",
    "ka": "🇬🇪 Georgia", "az": "🇦🇿 Azerbaijan", "kk": "🇰🇿 Kazakhstan",
}

def track(uid, uname, lang, etype, content="", tg_lang_code=None):
    s = load_stats()
    uid = str(uid)
    now = datetime.utcnow().isoformat()
    country = LANG_TO_COUNTRY.get(tg_lang_code, f"🌍 {tg_lang_code or 'unknown'}")
    if uid not in s["users"]:
        s["users"][uid] = {"name": uname, "lang": lang, "first": now, "count": 0, "country": country}
    s["users"][uid]["count"] += 1
    s["users"][uid]["last"] = now
    s["users"][uid]["lang"] = lang
    if tg_lang_code:
        s["users"][uid]["country"] = country
    if etype == "topic":
        s["topics"][content] = s["topics"].get(content, 0) + 1
    if etype == "question" and content:
        s["questions"].append({"q": content[:150], "lang": lang, "country": country, "t": now})
        s["questions"] = s["questions"][-500:]
    if "countries" not in s:
        s["countries"] = {}
    s["countries"][country] = s["countries"].get(country, 0) + 1
    s["total"] = s.get("total", 0) + 1
    save_stats(s)

# ── Claude API — ASYNC ─────────────────────────────────────────────────────
async def ask_claude(prompt: str, lang: str, use_search: bool = False) -> str:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    tools = [{"type": "web_search_20250305", "name": "web_search"}] if use_search else []
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "system": build_system_prompt(lang),
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools
    response = await client.messages.create(**kwargs)
    parts = [block.text for block in response.content if hasattr(block, 'text')]
    return "\n".join(parts) if parts else "⚠️ No response."

async def analyze_plant_photo(image_data: bytes, lang: str) -> str:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    lang_name = {"en": "English", "pl": "Polish", "de": "German", "es": "Spanish", "ru": "Russian"}.get(lang, "English")
    system = PHOTO_SYSTEM.replace("{lang_name}", lang_name)
    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": "Analyze this blueberry photo: identify variety if berries visible, diagnose diseases/pests/deficiencies, assess quality."}
            ],
        }]
    )
    parts = [block.text for block in response.content if hasattr(block, 'text')]
    return "\n".join(parts) if parts else "⚠️ Could not analyze image."

# ── Topic prompts ──────────────────────────────────────────────────────────
TOPIC_PROMPTS = {
    "market": {
        "en": "Global highbush blueberry market 2025/26: production, value, growth, regions. Distinguish production vs export. Concise with key numbers.",
        "pl": "Globalny rynek borówki 2025/26: produkcja, wartość, wzrost, regiony. Produkcja vs eksport. Kluczowe liczby.",
        "de": "Globaler Heidelbeermarkt 2025/26: Produktion, Wert, Wachstum. Produktion vs Export. Präzise.",
        "es": "Mercado global arándanos 2025/26: producción, valor, crecimiento. Distinguir producción de exportación.",
        "ru": "Мировой рынок голубики 2025/26: производство, стоимость, рост. Производство vs экспорт.",
    },
    "production": {
        "en": "Top 20 highbush blueberry producing countries 2024/25: MT volumes, regions, season. China #1 producer (domestic), Peru #1 exporter. Table format.",
        "pl": "Top 20 krajów borówki 2024/25: tony, regiony, sezon. Chiny nr1 producent (rynek wewn.), Peru nr1 eksporter. Tabela.",
        "de": "Top 20 Produzenten 2024/25: MT, Regionen, Saison. China #1 Inland, Peru #1 Export. Tabelle.",
        "es": "Top 20 productores 2024/25: TM, regiones, temporada. China #1 doméstico, Perú #1 exportador. Tabla.",
        "ru": "Топ-20 производителей 2024/25: тонны, регионы, сезон. Китай #1 внутренний, Перу #1 экспорт. Таблица.",
    },
    "export": {
        "en": "Global blueberry export 2024/25: 1M MT, $6.73B. Top 10 exporters MT and share. Peru 31% ($2.56B), Morocco rose 7→4th. Season windows.",
        "pl": "Globalny eksport 2024/25: 1mln MT, $6,73mld. Top10 eksporterów MT i %. Peru 31%, Maroko 7→4. Okna sezonowe.",
        "de": "Globaler Export 2024/25: 1 Mio MT, $6,73 Mrd. Top 10. Peru 31%, Marokko 7.→4. Saisonfenster.",
        "es": "Exportación global 2024/25: 1M TM, $6.73B. Top 10. Perú 31%, Marruecos 7°→4°. Ventanas.",
        "ru": "Мировой экспорт 2024/25: 1 млн тонн, $6,73 млрд. Топ-10. Перу 31%, Марокко 7→4. Сезоны.",
    },
    "destinations": {
        "en": "Key import markets 2025/26: USA 200k MT, China +153% from Peru (Chancay Port), Europe supply chain Morocco→Spain→Poland→S.Hemisphere, Russia post-2022. Prices per market.",
        "pl": "Rynki importu 2025/26: USA 200k MT, Chiny +153% z Peru (port Chancay), Europa Maroko→Hiszpania→Polska→PołHem, Rosja po 2022. Ceny.",
        "de": "Importmärkte 2025/26: USA 200k MT, China +153% aus Peru, Europa Lieferkette, Russland. Preise je Markt.",
        "es": "Mercados importación 2025/26: USA 200k TM, China +153% Perú, Europa cadena, Rusia. Precios.",
        "ru": "Рынки импорта 2025/26: США 200к тонн, Китай +153% из Перу, Европа цепочка, Россия. Цены.",
    },
    "prices": {
        "en": "Current prices June 2026: Serbia farm gate EUR 5-7/kg dropping. Poland Bronisze: tunnel 20-45 PLN, import 30-40 PLN. Peru FOB $4.19/kg. NL $4.06/kg. Belgium $6.51. China $6.79/kg (highest). USA $4.41. Retail USA $8-16/kg, Germany EUR 12-24, Poland 45-70 PLN. Frozen EUR 0.90-1.50/kg.",
        "pl": "Aktualne ceny czerwiec 2026: Serbia skup EUR 5-7/kg spada. Bronisze: tunelowe 20-45 PLN, import 30-40 PLN. Peru FOB $4,19/kg. Holandia $4,06. Belgia $6,51. Chiny $6,79 (najdrożej). USA $4,41. Detal USA $8-16/kg, Niemcy EUR 12-24, Polska 45-70 PLN. Mrożone EUR 0,90-1,50.",
        "de": "Aktuelle Preise Juni 2026: Serbien EUR 5-7/kg fallend. Polen Bronisze: Tunnel 20-45 PLN, Import 30-40 PLN. Peru FOB $4,19. NL $4,06. BE $6,51. China $6,79. USA $4,41. Einzelhandel USA, DE, PL. TK EUR 0,90-1,50.",
        "es": "Precios actuales junio 2026: Serbia EUR 5-7/kg bajando. Polonia Bronisze: túnel 20-45 PLN, importado 30-40 PLN. Perú FOB $4,19. NL $4,06. BE $6,51. China $6,79. USA $4,41. Retail. Congelado EUR 0,90-1,50.",
        "ru": "Цены июнь 2026: Сербия EUR 5-7/кг падает. Польша: тепличные 20-45 зл, импорт 30-40 зл. Перу FOB $4,19. Нидерланды $4,06. Бельгия $6,51. Китай $6,79. США $4,41. Розница. Замороженные EUR 0,90-1,50.",
    },
    "varieties": {
        "en": "NEW varieties 2020-2026: SEKOYA low-chill (Pop, Beauty, Crunch, Grande) + high-chill (Nova, ArabellaBlue, Apex 2026, FC11-164 mechanical). Blue World/Demba (Taste Award: Demba, Dana). Planasa (Blue Manila, Madeira, Maldiva). BerryWorld Orb, PeachyBlue. Climate for each.",
        "pl": "NOWE odmiany 2020-2026: SEKOYA low-chill (Pop, Beauty, Crunch, Grande) + high-chill (Nova, ArabellaBlue, Apex 2026). Blue World/Demba (nagroda: Demba, Dana). Planasa (Blue Manila, Madeira, Maldiva). BerryWorld Orb, PeachyBlue. Klimat.",
        "de": "NEUE Sorten 2020-2026: SEKOYA (Pop, Beauty, Crunch, Nova, ArabellaBlue, Apex) + Blue World/Demba (Taste Award) + Planasa Blue + BerryWorld Orb. Klima je Sorte.",
        "es": "NUEVAS variedades 2020-2026: SEKOYA + Blue World/Demba (Taste Award) + Planasa Blue + BerryWorld Orb. Clima por variedad.",
        "ru": "НОВЫЕ сорта 2020-2026: SEKOYA + Blue World/Demba (Taste Award) + Planasa Blue + BerryWorld Orb. Климат.",
    },
    "classics": {
        "en": "Classic varieties pre-2020: Northern Highbush high-chill (Bluecrop, Duke, Draper, Aurora, Liberty, Chandler, Patriot, Elliott). Southern Highbush low-chill (Biloxi, Ventura, O'Neal, Misty, Emerald, Jewel). Half-High extreme cold (Northblue, Polaris, Chippewa). Climate table.",
        "pl": "Klasyczne pre-2020: Północne high-chill (Bluecrop, Duke, Draper, Aurora, Liberty, Chandler, Patriot). Południowe low-chill (Biloxi, Ventura, O'Neal, Misty, Emerald). Półwysokopienne (Northblue, Polaris, Chippewa). Tabela klimatu.",
        "de": "Klassisch pre-2020: Nord-Highbush (Bluecrop, Duke, Draper, Aurora, Liberty) + Süd-Highbush (Biloxi, Ventura, O'Neal, Misty) + Half-High (Northblue, Polaris). Klimatabelle.",
        "es": "Clásicas pre-2020: Northern Highbush (Bluecrop, Duke, Draper, Aurora) + Southern Highbush (Biloxi, Ventura, O'Neal, Misty) + Half-High (Northblue, Polaris). Tabla climática.",
        "ru": "Классические до 2020: Северные (Bluecrop, Duke, Draper, Aurora) + Южные (Biloxi, Ventura, O'Neal, Misty) + Полувысокорослые (Northblue, Polaris). Таблица климата.",
    },
    "nursery": {
        "en": "Top 5 blueberry nurseries: 1) Fall Creek USA 40M+/yr, 59 countries, SEKOYA. 2) Planasa Spain 1B plants/yr, 7000 staff, Blue Manila/Madeira/Maldiva. 3) Onubafruit/FV.BV Blue World (Demba, Dana). 4) Oregon Blueberry USA largest N.America. 5) Lorsena Spain EU specialist. Costs $0.50-5.",
        "pl": "Top 5 szkółek: 1) Fall Creek USA 40mln/rok, 59 krajów, SEKOYA. 2) Planasa Hiszpania 1mld/rok, 7000 prac., Blue Manila/Madeira/Maldiva. 3) Onubafruit/FV.BV Blue World (Demba, Dana). 4) Oregon Blueberry USA. 5) Lorsena Hiszpania. Ceny $0,50-5.",
        "de": "Top 5: 1) Fall Creek USA 40M+/Jahr, 59 Länder. 2) Planasa Spanien 1Mrd/Jahr, 7000 MA. 3) Onubafruit Blue World. 4) Oregon Blueberry USA. 5) Lorsena Spanien. $0,50-5.",
        "es": "Top 5: 1) Fall Creek USA 40M+/año, 59 países. 2) Planasa España 1000M/año, 7000 emp. 3) Onubafruit Blue World. 4) Oregon Blueberry. 5) Lorsena. $0,50-5.",
        "ru": "Топ-5: 1) Fall Creek США 40М+/год, 59 стран. 2) Planasa Испания 1млрд/год, 7000 сотр. 3) Onubafruit Blue World. 4) Oregon Blueberry США. 5) Lorsena Испания. $0,50-5.",
    },
    "news": {
        "en": "Breaking news June 2026: Serbia prices EUR 6.50→4.00-5.00/kg at peak (Duke season), Poland frost damage (May coldest 34 years) tunnel 20-45 PLN field July, Romania starting June 15 first Sekoya volumes, Georgia (country) active May-June 7500 MT. Europe: Serbia peak, Romania starting, Poland/Germany July.",
        "pl": "Aktualności czerwiec 2026: Serbia ceny EUR 6,50→4,00-5,00/kg w szczycie (sezon Duke), Polska szkody przymrozkowe (maj najzimniejszy od 34 lat) tunelowe 20-45 PLN pole lipiec, Rumunia start 15 czerwca pierwsze wolumeny Sekoya, Gruzja aktywna maj-czerwiec 7500 MT. Europa: Serbia szczyt, Rumunia start, Polska/Niemcy lipiec.",
        "de": "News Juni 2026: Serbien EUR 6,50→4,00-5,00/kg Peak (Duke), Polen Frostschäden (kältester Mai 34 Jahre) Tunnel 20-45 PLN Feld Juli, Rumänien Start 15. Juni erste Sekoya, Georgien aktiv Mai-Juni 7500 MT.",
        "es": "Noticias junio 2026: Serbia EUR 6,50→4,00-5,00/kg pico (Duke), Polonia daños heladas (mayo más frío 34 años) túnel 20-45 PLN campo julio, Rumanía inicio 15 junio primeros Sekoya, Georgia activa mayo-junio 7500 MT.",
        "ru": "Новости июнь 2026: Сербия EUR 6,50→4,00-5,00/кг пик (Duke), Польша заморозки (май холоднейший 34 года) теплица 20-45 зл поле июль, Румыния старт 15 июня первые Sekoya, Грузия активна май-июнь 7500 MT.",
    },
    "photo": {
        "en": "📸 Photo Analysis ready! Send me a photo of your blueberry plant, berries, or leaves. I will identify the variety, diagnose diseases/pests/deficiencies, and assess fruit quality. Just send the photo!",
        "pl": "📸 Analiza zdjęcia gotowa! Wyślij mi zdjęcie borówki — owoców, liści lub krzewu. Rozpoznam odmianę, zdiagnozuję choroby/szkodniki/niedobory i ocenię jakość. Wyślij zdjęcie!",
        "de": "📸 Fotoanalyse bereit! Senden Sie ein Foto Ihrer Heidelbeerpflanze. Ich identifiziere die Sorte, diagnostiziere Krankheiten und beurteile die Qualität.",
        "es": "📸 Análisis de foto listo! Envíame una foto de tu planta de arándano. Identificaré la variedad, diagnosticaré enfermedades y evaluaré la calidad.",
        "ru": "📸 Анализ фото готов! Отправьте фото вашего растения голубики. Определю сорт, диагностирую болезни/вредителей, оценю качество.",
    },
    "currency": {
        "en": "Blueberry price converter June 2026. Key prices in EUR/USD/PLN/GBP/CNY/RUB/RSD/RON/MAD: Serbia EUR 5-7/kg, Peru FOB $4.19/kg, Poland wholesale 30-40 PLN/kg, Netherlands $4.06/kg, China $6.79/kg. Use approximate June 2026 rates: EUR/PLN 4.25, USD/PLN 3.90, EUR/USD 1.09. Show all key markets in all currencies.",
        "pl": "Przelicznik cen borówek czerwiec 2026. Ceny w EUR/USD/PLN/GBP/CNY/RUB/RSD/RON/MAD: Serbia EUR 5-7/kg, Peru FOB $4,19/kg, Polska hurt 30-40 PLN/kg, Holandia $4,06/kg, Chiny $6,79/kg. Kursy: EUR/PLN 4,25, USD/PLN 3,90, EUR/USD 1,09. Pokaż wszystkie rynki we wszystkich walutach.",
        "de": "Preisrechner Juni 2026. EUR/USD/PLN/GBP/CNY/RUB: Serbien EUR 5-7/kg, Peru FOB $4,19, Polen 30-40 PLN, NL $4,06, China $6,79. Kurse: EUR/PLN 4,25, USD/PLN 3,90.",
        "es": "Conversor precios junio 2026. EUR/USD/PLN/GBP/CNY/RUB: Serbia EUR 5-7/kg, Perú FOB $4,19, Polonia 30-40 PLN, NL $4,06, China $6,79. Tasas: EUR/PLN 4,25, USD/PLN 3,90.",
        "ru": "Конвертер цен июнь 2026. EUR/USD/PLN/GBP/CNY/RUB: Сербия EUR 5-7/кг, Перу FOB $4,19, Польша 30-40 зл, NL $4,06, Китай $6,79. Курсы: EUR/PLN 4,25, USD/PLN 3,90.",
    },
    "health": {
        "en": "Blueberry health benefits: ORAC 9,621 umol/100g. Brain: -26% cognitive decline (Harvard 2012). Heart: -32% heart attack risk, -4-6mmHg BP. Diabetes: GI 53. Cancer: anthocyanins inhibit tumors. Eyes: lutein/zeaxanthin. Gut: prebiotic. Sports: muscle recovery 300g. Per 100g: 57kcal, 14.5g carbs, 2.4g fiber, Vit C 9.7mg. Frozen = 90%+ antioxidants retained.",
        "pl": "Właściwości zdrowotne borówki: ORAC 9621 umol/100g. Mózg: -26% spadku poznawczego (Harvard 2012). Serce: -32% zawał, -4-6mmHg ciśnienie. Cukrzyca: IG 53. Rak: antocyjany hamują nowotwory. Oczy: luteina/zeaksantyna. Jelita: prebiotyk. Sport: regeneracja 300g. 100g: 57kcal, 14,5g węglowodany, 2,4g błonnik, Vit C 9,7mg. Mrożone = 90%+ antyoksydantów.",
        "de": "Gesundheitsvorteile: ORAC 9.621. Gehirn: -26% Harvard 2012. Herz: -32% Herzinfarkt. GI 53. Anthocyane hemmen Tumore. Lutein/Zeaxanthin Augen. 100g: 57kcal, Vit C 9,7mg. TK: 90%+ Antioxidantien.",
        "es": "Beneficios salud: ORAC 9.621. Cerebro: -26% Harvard 2012. Corazón: -32% infarto. GI 53. Antocianinas inhiben tumores. Luteína ojos. 100g: 57kcal, Vit C 9,7mg. Congelado: 90%+ antioxidantes.",
        "ru": "Польза для здоровья: ORAC 9621. Мозг: -26% Гарвард 2012. Сердце: -32% инфаркт. ГИ 53. Антоцианы подавляют опухоли. Лютеин глаза. 100г: 57ккал, Вит С 9,7мг. Замороженные: 90%+ антиоксидантов.",
    },
    "search": {
        "en": "Search FreshPlaza, IBO, Proarándanos for latest 2026 blueberry news: current prices, export data, new varieties, market trends. Combine with knowledge base.",
        "pl": "Szukaj FreshPlaza, IBO, Proarándanos najnowszych wiadomości borówkowych 2026: ceny, eksport, odmiany, trendy.",
        "de": "FreshPlaza, IBO suchen: aktuelle Heidelbeernews 2026. Preise, Export, Sorten.",
        "es": "Buscar FreshPlaza, IBO noticias arándanos 2026: precios, exportación, variedades.",
        "ru": "Поиск FreshPlaza, IBO новостей черники 2026: цены, экспорт, сорта.",
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────
def get_lang(context):
    return context.user_data.get("lang", "en")

def main_menu_keyboard(lang):
    labels = MENU_LABELS[lang]
    keyboard = [
        [InlineKeyboardButton(labels["market"],       callback_data="topic_market"),
         InlineKeyboardButton(labels["production"],   callback_data="topic_production")],
        [InlineKeyboardButton(labels["export"],       callback_data="topic_export"),
         InlineKeyboardButton(labels["destinations"], callback_data="topic_destinations")],
        [InlineKeyboardButton(labels["prices"],       callback_data="topic_prices"),
         InlineKeyboardButton(labels["varieties"],    callback_data="topic_varieties")],
        [InlineKeyboardButton(labels["classics"],     callback_data="topic_classics"),
         InlineKeyboardButton(labels["nursery"],      callback_data="topic_nursery")],
        [InlineKeyboardButton(labels["news"],         callback_data="topic_news"),
         InlineKeyboardButton(labels["photo"],        callback_data="topic_photo")],
        [InlineKeyboardButton(labels["currency"],     callback_data="topic_currency"),
         InlineKeyboardButton(labels["health"],       callback_data="topic_health")],
        [InlineKeyboardButton(labels["search"],       callback_data="topic_search"),
         InlineKeyboardButton(labels["lang"],         callback_data="choose_lang")],
    ]
    return InlineKeyboardMarkup(keyboard)

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
        for code, name in LANGUAGES.items()
    ])

async def safe_reply(edit_func, text, **kwargs):
    """Send message with Markdown, fallback to plain text."""
    try:
        await edit_func(text, parse_mode="Markdown", **kwargs)
    except Exception:
        try:
            await edit_func(text, **kwargs)
        except Exception as e:
            logger.error(f"Reply error: {e}")

# ── Handlers ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user = update.effective_user
    s = load_stats()
    is_new = str(user.id) not in s["users"]
    track(user.id, user.username or "anon", lang, "question", "/start", tg_lang_code=user.language_code)
    await update.message.reply_text(WELCOME[lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))
    if is_new:
        ad_texts = {
            "en": "🌱 *Sponsored · Partner of BlueberryBot*\n\nNanoGro Aqua Forest — biostimulant for professional blueberry cultivation.\nImproves root development, stress resistance and yield quality.\n\n👇 Learn more:",
            "pl": "🌱 *Sponsor · Partner BlueberryBot*\n\nNanoGro Aqua Forest — biostymulator dla profesjonalnych upraw borówki.\nPoprawia ukorzenianie, odporność na stres i jakość plonów.\n\n👇 Dowiedz się więcej:",
            "de": "🌱 *Gesponsert · Partner von BlueberryBot*\n\nNanoGro Aqua Forest — Biostimulans für professionellen Heidelbeeranbau.\n\n👇 Mehr erfahren:",
            "es": "🌱 *Patrocinado · Partner de BlueberryBot*\n\nNanoGro Aqua Forest — bioestimulante para cultivo profesional de arándanos.\n\n👇 Saber más:",
            "ru": "🌱 *Реклама · Партнёр BlueberryBot*\n\nNanoGro Aqua Forest — биостимулятор для профессионального выращивания голубики.\n\n👇 Узнать больше:",
        }
        ad_button = InlineKeyboardMarkup([[InlineKeyboardButton(
            "🌱 NanoGro Aqua Forest → agrarius.eu",
            url="https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/"
        )]])
        await update.message.reply_text(
            ad_texts.get(lang, ad_texts["en"]),
            parse_mode="Markdown",
            reply_markup=ad_button,
            disable_web_page_preview=True
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(WELCOME[lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user = update.effective_user
    question = " ".join(context.args) if context.args else ""
    if not question:
        hints = {
            "en": "💡 Usage: /ask <question>\n\nExamples:\n/ask best varieties for Poland\n/ask blueberry price China 2026\n/ask Peru export volume 2025",
            "pl": "💡 Użycie: /ask <pytanie>\n\nPrzykłady:\n/ask najlepsze odmiany do Polski\n/ask cena borówek Chiny 2026\n/ask eksport Peru 2025",
            "de": "💡 /ask <Frage>\n\nBeispiele:\n/ask beste Sorten für Polen\n/ask Heidelbeerpreis China 2026",
            "es": "💡 /ask <pregunta>\n\nEjemplos:\n/ask mejores variedades Polonia\n/ask precio arándanos China 2026",
            "ru": "💡 /ask <вопрос>\n\nПримеры:\n/ask лучшие сорта для Польши\n/ask цена черники Китай 2026",
        }
        await update.message.reply_text(hints.get(lang, hints["en"]))
        return
    track(user.id, user.username or "anon", lang, "question", question, tg_lang_code=user.language_code)
    thinking = {"en": "🫐 Analyzing...", "pl": "🫐 Analizuję...", "de": "🫐 Analysiere...", "es": "🫐 Analizando...", "ru": "🫐 Анализирую..."}
    msg = await update.message.reply_text(thinking.get(lang, "🫐 Thinking..."))
    try:
        response = await ask_claude(question, lang, use_search=True)
        if len(response) > 4000:
            response = response[:3990] + "\n\n_(truncated)_"
        await safe_reply(msg.edit_text, response)
        await update.message.reply_text("─" * 20, reply_markup=main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Ask error: {e}")
        await msg.edit_text(f"⚠️ Error: {str(e)[:200]}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin_id = int(os.getenv("ADMIN_ID", "0"))
    if user.id != admin_id:
        await update.message.reply_text("⛔ Access denied.")
        return
    s = load_stats()
    txt = f"📊 *BlueberryBot Stats*\n👥 Users: {len(s['users'])}\n📨 Total: {s.get('total',0)}\n\n"
    txt += "🔝 *Top topics:*\n"
    for t, cnt in sorted(s["topics"].items(), key=lambda x: -x[1])[:10]:
        txt += f"  {t}: {cnt}\n"
    txt += "\n🌍 *Countries:*\n"
    for c, cnt in sorted(s.get("countries", {}).items(), key=lambda x: -x[1])[:15]:
        txt += f"  {c}: {cnt}\n"
    txt += "\n💬 *Last questions:*\n"
    for q in s["questions"][-5:]:
        txt += f"  [{q.get('country','?')}] {q['q'][:60]}\n"
    await update.message.reply_text(txt[:4000], parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)
    if data == "choose_lang":
        await query.edit_message_text("🌐 Choose language / Wybierz język:", reply_markup=lang_keyboard())
        return
    if data.startswith("lang_"):
        new_lang = data.split("_", 1)[1]
        context.user_data["lang"] = new_lang
        await query.edit_message_text(WELCOME[new_lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(new_lang))
        return
    if data.startswith("topic_"):
        topic = data.split("_", 1)[1]
        loading = {"en": "⏳ Loading...", "pl": "⏳ Ładuję...", "de": "⏳ Laden...", "es": "⏳ Cargando...", "ru": "⏳ Загрузка..."}
        await query.edit_message_text(loading.get(lang, "⏳ Loading..."))
        user = query.from_user
        track(user.id, user.username or "anon", lang, "topic", topic, tg_lang_code=user.language_code)
        prompt = TOPIC_PROMPTS.get(topic, {}).get(lang) or TOPIC_PROMPTS.get(topic, {}).get("en", "Tell me about blueberries.")
        use_search = (topic == "search")
        try:
            response = await ask_claude(prompt, lang, use_search=use_search)
            if len(response) > 4000:
                response = response[:3990] + "\n\n_(truncated)_"
            await safe_reply(query.edit_message_text, response, reply_markup=main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Button error: {e}")
            await query.edit_message_text(f"⚠️ Error: {str(e)[:200]}", reply_markup=main_menu_keyboard(lang))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user_msg = update.message.text
    user = update.effective_user
    track(user.id, user.username or "anon", lang, "question", user_msg, tg_lang_code=user.language_code)
    thinking = {"en": "🫐 Analyzing...", "pl": "🫐 Analizuję...", "de": "🫐 Analysiere...", "es": "🫐 Analizando...", "ru": "🫐 Анализирую..."}
    msg = await update.message.reply_text(thinking.get(lang, "🫐 Thinking..."))
    try:
        response = await ask_claude(user_msg, lang, use_search=True)
        if len(response) > 4000:
            response = response[:3990] + "\n\n_(truncated)_"
        await safe_reply(msg.edit_text, response)
        await update.message.reply_text("─" * 20, reply_markup=main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Message error: {e}")
        await msg.edit_text(f"⚠️ Error: {str(e)[:200]}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user = update.effective_user
    thinking = {"en": "🔬 Analyzing photo...", "pl": "🔬 Analizuję zdjęcie...", "de": "🔬 Foto analysieren...", "es": "🔬 Analizando foto...", "ru": "🔬 Анализирую фото..."}
    msg = await update.message.reply_text(thinking.get(lang, "🔬 Analyzing..."))
    try:
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        result = await analyze_plant_photo(bytes(photo_bytes), lang)
        if len(result) > 4000:
            result = result[:3990] + "\n\n_(truncated)_"
        await safe_reply(msg.edit_text, result)
        track(user.id, user.username or "anon", lang, "topic", "photo", tg_lang_code=user.language_code)
        followup = {"en": "📸 Send another photo or choose:", "pl": "📸 Wyślij kolejne zdjęcie lub wybierz:", "de": "📸 Weiteres Foto oder Thema:", "es": "📸 Otra foto o elige tema:", "ru": "📸 Ещё фото или выберите тему:"}
        await update.message.reply_text(followup.get(lang, "📸"), reply_markup=main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Photo error: {e}")
        await msg.edit_text(f"⚠️ Photo error: {str(e)[:200]}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("🫐 BlueberryBot v2.0 starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
