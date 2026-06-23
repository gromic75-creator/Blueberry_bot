"""
🫐 BlueberryBot v2.0 — Global Highbush Blueberry Market Intelligence
Sources: IBO, FreshPlaza, Blueberries Consulting, USDA, Proarándanos
Data: 2024/2025 season (latest available)
Languages: EN, PL, DE, ES, RU
"""

import os
import logging
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
    "en": "🫐 *BlueberryBot v2.0* — Global Highbush Blueberry Market Intelligence\n\n📊 Data: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Tip:* Type your country name for variety advice!\n📸 *Send a photo* — variety identification + disease diagnosis!\n\nChoose a topic or ask me anything!",
    "pl": "🫐 *BlueberryBot v2.0* — Globalny Wywiad Rynku Borówki Amerykańskiej\n\n📊 Dane: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Wskazówka:* Napisz kraj aby dostać rekomendacje odmian!\n📸 *Wyślij zdjęcie* — rozpoznanie odmiany + diagnoza chorób!\n\nWybierz temat lub zadaj pytanie!",
    "de": "🫐 *BlueberryBot v2.0* — Globale Heidelbeer-Marktintelligenz\n\n📊 Daten: IBO · FreshPlaza · USDA · 2024/2025\n\nThema wählen oder Frage stellen!",
    "es": "🫐 *BlueberryBot v2.0* — Inteligencia del Mercado Global de Arándanos\n\n📊 Datos: IBO · FreshPlaza · USDA · Proarándanos · 2024/2025\n\n¡Elige un tema o pregunta lo que quieras!",
    "ru": "🫐 *BlueberryBot v2.0* — Глобальная аналитика рынка голубики\n\n📊 Данные: IBO · FreshPlaza · USDA · 2024/2025\n\nВыберите тему или задайте вопрос!",
}

MENU_LABELS = {
    "en": {
        "market":    "📊 Global Market",
        "production":"🌍 Production by Country",
        "export":    "🚢 Export Leaders",
        "destinations": "🎯 Key Markets",
        "prices":    "💰 Market Prices 2025/26",
        "varieties": "🌱 New Varieties",
        "classics":  "📚 Classic Varieties",
        "nursery":   "🏭 Nursery & Plants",
        "search":    "🔍 Live Search",
        "news":      "📰 Breaking News",
        "photo":     "📸 Photo Analysis",
        "roi":       "🧮 ROI Calculator",
        "currency":  "💱 Currency & Prices",
        "health":    "🏥 Health Benefits",
        "lang":      "🌐 Language",
    },
    "pl": {
        "market":    "📊 Rynek globalny",
        "production":"🌍 Produkcja wg kraju",
        "export":    "🚢 Liderzy eksportu",
        "destinations": "🎯 Kluczowe rynki",
        "prices":    "💰 Ceny rynkowe 2025/26",
        "varieties": "🌱 Nowe odmiany",
        "classics":  "📚 Klasyczne odmiany",
        "nursery":   "🏭 Szkółki i sadzonki",
        "search":    "🔍 Wyszukiwanie live",
        "news":      "📰 Aktualności",
        "photo":     "📸 Analiza zdjęcia",
        "roi":       "🧮 Kalkulator ROI",
        "currency":  "💱 Waluty i ceny",
        "health":    "🏥 Właściwości zdrowotne",
        "lang":      "🌐 Język",
    },
    "de": {
        "market":    "📊 Globaler Markt",
        "production":"🌍 Produktion nach Land",
        "export":    "🚢 Export-Führer",
        "destinations": "🎯 Schlüsselmärkte",
        "prices":    "💰 Marktpreise 2025/26",
        "varieties": "🌱 Neue Sorten",
        "classics":  "📚 Klassische Sorten",
        "nursery":   "🏭 Baumschulen & Pflanzen",
        "search":    "🔍 Live-Suche",
        "news":      "📰 Aktuelle News",
        "photo":     "📸 Foto-Analyse",
        "roi":       "🧮 ROI-Rechner",
        "currency":  "💱 Währung & Preise",
        "health":    "🏥 Gesundheitsvorteile",
        "lang":      "🌐 Sprache",
    },
    "es": {
        "market":    "📊 Mercado global",
        "production":"🌍 Producción por país",
        "export":    "🚢 Líderes exportación",
        "destinations": "🎯 Mercados clave",
        "prices":    "💰 Precios mercado 2025/26",
        "varieties": "🌱 Nuevas variedades",
        "classics":  "📚 Variedades clásicas",
        "nursery":   "🏭 Viveros y plantas",
        "search":    "🔍 Búsqueda en vivo",
        "news":      "📰 Noticias",
        "photo":     "📸 Análisis de foto",
        "roi":       "🧮 Calculadora ROI",
        "currency":  "💱 Divisas y precios",
        "health":    "🏥 Beneficios salud",
        "lang":      "🌐 Idioma",
    },
    "ru": {
        "market":    "📊 Мировой рынок",
        "production":"🌍 Производство по странам",
        "export":    "🚢 Лидеры экспорта",
        "destinations": "🎯 Ключевые рынки",
        "prices":    "💰 Рыночные цены 2025/26",
        "varieties": "🌱 Новые сорта",
        "classics":  "📚 Классические сорта",
        "nursery":   "🏭 Питомники и саженцы",
        "search":    "🔍 Поиск в реальном времени",
        "news":      "📰 Новости",
        "photo":     "📸 Анализ фото",
        "roi":       "🧮 ROI Калькулятор",
        "currency":  "💱 Валюты и цены",
        "health":    "🏥 Польза для здоровья",
        "lang":      "🌐 Язык",
    },
}

# ══════════════════════════════════════════════════════════════
# KNOWLEDGE BASE — VERIFIED DATA FROM IBO, FRESHPLAZA, USDA
# ══════════════════════════════════════════════════════════════
BLUEBERRY_KNOWLEDGE = """
╔══════════════════════════════════════════════════════════════════╗
║  BLUEBERRY KNOWLEDGE BASE — VERIFIED 2024/2025 DATA            ║
║  Sources: IBO, FreshPlaza, USDA, Proarándanos, Blueberries Consulting ║
╚══════════════════════════════════════════════════════════════════╝

⚠️ CRITICAL DISTINCTION:
- This bot covers ONLY cultivated HIGHBUSH BLUEBERRY (Vaccinium corymbosum)
  = Borówka Amerykańska / Arándano / Heidelbeere (Kulturheidelbeere)
- NOT wild bilberry / Vaccinium myrtillus (jagoda leśna / czarna jagoda)
- These are completely different fruits and markets!

══════════════════════════════════════════════════════════════════
SECTION 1: GLOBAL MARKET SIZE & VALUE
══════════════════════════════════════════════════════════════════

Global cultivated highbush blueberry production (IBO data):
- 2023: 1.78 million tonnes (global)
- 2024: exceeded 2.0 million tonnes for first time in history
- Global cultivation area 2023: 267,000 hectares (+7.2% vs 2022)
- Global export value 2024: $6.73 billion (1 million tonnes exported)
- Latin America: 42% of world acreage (Peru, Mexico, Chile)
- Growth rate: ~10% annually in exports (+60,000 tonnes/year since 2019)

IBO forecast: global fresh blueberry segment to reach 2.5 billion kg by 2029

══════════════════════════════════════════════════════════════════
SECTION 2: PRODUCTION BY COUNTRY — IMPORTANT CLARIFICATION
══════════════════════════════════════════════════════════════════

⚠️ PRODUCTION vs EXPORT — COMPLETELY DIFFERENT PICTURE:

PRODUCTION RANKING (total volume, 2023-2024):
China is #1 producer BY VOLUME but exports almost NOTHING — all domestic.
China overtook USA in 2021 as largest producer.

1. 🇨🇳 CHINA — ~570,000-780,000 MT (2024)
   - Provinces: Guizhou, Jilin, Yunnan, Shandong
   - ~32% of global production
   - DOMESTIC CONSUMPTION ONLY — minimal exports
   - Varieties: low-chill adapted (Misty, O'Neal, Sharpblue, Brightwell)
   - Rapidly expanding, mainly serving 1.4B domestic consumers
   - Also imports 80,000-100,000 MT/year — demand far exceeds domestic supply

2. 🇺🇸 USA — 358,000 MT cultivated highbush (2024, USDA data)
   + 90.8 million lbs wild lowbush (Maine) — separate market
   - Top states: Washington, Oregon, Georgia (= 65% of total)
   - Also: Michigan, California, North Carolina, New Jersey, Florida
   - 90% cultivated (highbush), 10% wild
   - Value: $1.15 billion farm gate (2024)
   - 55% fresh market, 45% processing/frozen

3. 🇵🇪 PERU — ~320,000-412,000 MT (2024/25 season)
   - WORLD'S #1 EXPORTER by volume AND value
   - 20,490 hectares certified for export (2024/25)
   - Regions: La Libertad (51%), Lambayeque (23%), Ica (11%)
   - Season: August–January (peak Sept–Nov)
   - Yields: 19 MT/hectare — highest in world
   - Export value 2025: ~$2.56 billion

4. 🇨🇦 CANADA — ~170,000 MT total
   - Highbush: British Columbia (94% of highbush)
   - Wild lowbush: Quebec (43,997 MT wild in 2024), Nova Scotia, New Brunswick
   - Fraser Valley dominant for cultivated

5. 🇨🇱 CHILE — ~150,000 MT
   - #2 exporter by volume
   - 2024/25: 90,000+ MT fresh exports (+5% vs previous season)
   - Regions: Biobío, La Araucanía, Bío Bío
   - New varieties driving 50% growth in premium segment

6. 🇪🇸 SPAIN — ~110,000 MT
   - Main region: Huelva (Andalusia) — 90%+ of production
   - Season: February–June (fills EU gap)
   - #3 exporter globally (8% world export share)
   - Key player: Onubafruit (20,000 MT, Blue World varieties)

7. 🇵🇱 POLAND — ~75,000-80,000 MT
   - Largest highbush producer in EU
   - Main regions: Mazovia, Lublin, Greater Poland
   - Season: July–September
   - Key varieties: Bluecrop, Duke, Patriot, Draper, Aurora
   - ~50,000 MT exported, mainly Germany/Netherlands/UK/Scandinavia

8. 🇲🇽 MEXICO — ~65,000-70,000 MT
   - Rapid growth: +13% exports 2025
   - Key regions: Jalisco, Baja California, Sinaloa
   - Season: Nov–April (fills North America off-season with Chile/Peru)
   - Growing role in US market (proximity advantage)

9. 🇲🇦 MOROCCO — ~83,000 MT (record 2024!)
   - Fastest rising exporter: climbed from 7th to 4th place globally in 2024
   - 8% of global export share (equal to Chile and Spain)
   - Season: February–April (earliest EU supply)
   - Main market: Europe (Netherlands, UK, France)
   - From 636 tonnes (2009) to 83,000 tonnes (2024) — extraordinary growth

10. 🇵🇹 PORTUGAL — ~25,000 MT
11. 🇿🇦 SOUTH AFRICA — ~35,000 MT (growing exporter)
12. 🇦🇷 ARGENTINA — ~18,000 MT
13. 🇦🇺 AUSTRALIA — ~20,000 MT
14. 🇩🇪 GERMANY — ~12,000 MT
15. 🇳🇱 NETHERLANDS — ~10,000 MT (mainly greenhouse)
16. 🇷🇺 RUSSIA — ~15,000 MT cultivated (+ large wild bilberry harvest)
17. 🇺🇦 UKRAINE — ~25,000 MT (before conflict was higher)
18. 🇷🇸 SERBIA — ~8,000 MT
19. 🇿🇼 ZIMBABWE — emerging, fast growing
20. 🇬🇪 GEORGIA (country) — emerging new exporter

══════════════════════════════════════════════════════════════════
SECTION 3: EXPORT DATA — WHO ACTUALLY SELLS TO THE WORLD
══════════════════════════════════════════════════════════════════

GLOBAL EXPORT 2024 (IBO / Blue Book data):
- Total: 1,000,000 MT (first time exceeding 1 million tonnes!)
- Total value: $6.73 billion

TOP EXPORTERS 2024 by share:
1. 🇵🇪 Peru — 31% (~310,000 MT) — WORLD LEADER
2. 🇨🇱 Chile — 8% (~80,000 MT)
3. 🇪🇸 Spain — 8% (~80,000 MT)
4. 🇲🇦 Morocco — 8% (~83,000 MT) ⬆️ NEW — rose from 7th to 4th!
5. 🇺🇸 USA — 7% (~70,000 MT)
6. 🇵🇱 Poland — ~5% (~50,000 MT)
7. 🇲🇽 Mexico — ~2.3% (~23,000 MT, +13%)
8. 🇨🇦 Canada — ~3%
9. 🇿🇦 South Africa — growing
10. 🇦🇺 Australia — growing

PERU EXPORTS 2025 (most detailed data):
- Total volume 2025: ~412,000 MT (record), value ~$2.56 billion
- USA: 150,673 MT (+3%) = #1 destination, value $1.19B
- Europe (Netherlands hub): 91,926 MT (+36%), value $508M
- China: 43,935 MT (+18%), value $231M (surged 153% in some reports)
- Other destinations: +122% growth (diversification)
- Average price: $6.20/kg (vs $6.43 in 2024 — slight decline)
- 66 destination countries (up from 52 in 2024)

CHILE EXPORTS 2024/25:
- Fresh exports: 90,000+ MT (+5% vs previous season)
- New varieties: 50% growth, now 21% of total exports
- Main varieties shifting from Biloxi to premium (Sekoya, Eureka)

══════════════════════════════════════════════════════════════════
SECTION 4: KEY IMPORT MARKETS
══════════════════════════════════════════════════════════════════

🇺🇸 USA:
- World's largest importer: ~200,000+ MT/year
- Counter-season supply: Chile, Peru, Mexico (Oct–May)
- Domestic season: April–September
- USA + Netherlands = 48% of world imports (2023)

🇨🇳 CHINA:
- Imports: 80,000-100,000 MT/year
- Fastest growing import market (+25%/year)
- Main suppliers: Peru (#1, +153% in 2025), Chile, Australia, NZ
- Key driver: Chancay Port (Peru) reduces logistics costs
- Preference: large, firm, sweet varieties (Sekoya Pop, Ventura)
- Domestic production growing but demand still far exceeds supply

🇪🇺 EUROPE (EU + UK):
- Netherlands: central redistribution hub
- ~200,000+ MT/year imports
- Seasonal supply chain:
  * November–January: Southern Hemisphere (Peru, Chile, Argentina)
  * February–April: Morocco (fastest growing!)
  * April–June: Spain (Huelva dominates)
  * July–September: Poland, Germany, Netherlands (domestic)
  * October: gap → Southern Hemisphere returns

🇷🇺 RUSSIA:
- Pre-2022: imported ~30,000 MT mainly from Serbia, Poland, Belarus
- Post-2022 sanctions: Western imports drastically reduced
- Current suppliers: Belarus, Azerbaijan, China, Iran, Serbia (via third countries)
- Domestic production growing: Leningrad region, Krasnodar, Siberia
- Wild bilberry/cowberry still main berry consumed (different product!)
- Retail prices: 400-800 RUB/250g punnet

══════════════════════════════════════════════════════════════════
SECTION 5: PRICES 2024/2025
══════════════════════════════════════════════════════════════════

EXPORT (FOB) PRICES:
- Peru average 2025: $6.20/kg (down from $6.43/kg in 2024, -3%)
- Peak season (Sept-Oct Peru): can fall sharply due to volume glut
- Off-season (Jan-May): $3.5-7.0/kg depending on origin
- Premium varieties (Sekoya): +20-40% premium over conventional

RETAIL PRICES (approximate):
- USA: $4-8/pint punnet (~$8-16/kg)
- Germany: €3-6/250g punnet (~€12-24/kg)
- UK: £2.50-5.00/150g (~£16-33/kg)
- Poland: 12-25 PLN/250g (~50-100 PLN/kg) in peak season
- Russia: 400-900 RUB/250g
- China: 80-200 CNY/kg (premium for large Sekoya-type berries)

FROZEN (bulk, EU import):
- Standard: €0.90-1.50/kg
- Premium/organic: €1.80-2.50/kg

PRICE TREND: Mild downward pressure globally due to oversupply.
IBO warns of "margin squeeze" as production outpaces demand growth.

══════════════════════════════════════════════════════════════════
SECTION 6: VARIETIES — THE NEW GENERATION 2022-2025
══════════════════════════════════════════════════════════════════

▶ SEKOYA PLATFORM (Fall Creek® breeding) — MOST IMPORTANT BRAND GLOBALLY
  The #1 premium variety platform worldwide, B2B model with 15 member companies.
  Present in 25 countries, 2,500 hectares, ~87,000 MT production target 2024.
  40% sold USA/Canada, 36% Europe, 24% Asia
  
  LOW/ZERO CHILL (warm climates — Peru, Mexico, S.USA):
  - Sekoya Pop™ 'FCM14-052' — most planted in Peru, preferred in China market
  - Sekoya Beauty™ 'FCM12-097' — early season, large berry
  - Sekoya Crunch™ 'FC13-083' — exceptional firmness, shelf life
  - Sekoya Grande™ 'FC13-122' — jumbo size

  HIGH CHILL (cold climates — Poland, Canada, N.USA, high Chile):
  - SEKOYA® Nova 'FC15-173' — newest high-chill, just launched
  - ArabellaBlue® 'FC14-062' — vigorous, early-fruiting (launched Dec 2025)
  - LoretoBlue™ 'FC11-118' — high performance
  - FC11-164 — mechanical harvest focused (commercial trials 2024, Europe/US/Chile)
  - Apex 'FCM14-057' — launched April 2026, for EMEA Jan-May window

▶ DEMBA & BLUE WORLD (Onubafruit / FV.BV Netherlands) — TOP EUROPEAN VARIETIES
  Developed by Dutch company FV.BV, exclusive licensee Onubafruit (Spain/Portugal/Morocco)
  Protected until December 31, 2056 in EU.
  Awards: International Taste Institute Superior Taste Award (Demba, Dana)
  Productivity: 25,000-30,000 kg/hectare, >80% size 18mm+
  Season: November to June (Huelva, Spain)
  
  - Demba (FV1908) ⭐ — AWARD WINNER. Precocity, size, firmness, exceptional flavor.
    One of world's best-rated blueberries by International Taste Institute.
  - Dana (FV1907) ⭐ — Award winner, excellent flavor and firmness
  - Selma (FV1901) — covers mid-season
  - Aila (FV1905) — early season
  - Lena (FV1904) — part of full-season portfolio
  - Selena (FV1905) — additional coverage
  - FV1902, FV1903 — in development, no commercial name yet
  Onubafruit Blue World target: 50% of 20,000 MT production, +10-15%/year growth

▶ PERU TOP VARIETIES (2024/25 season, Proarándanos data):
  ~65 varieties grown commercially in Peru!
  Top 9 = 80% of certified area:
  1. Ventura — 26% share (EU preference: 50% of shipments to Europe!)
  2. Biloxi — 16% (declining, being replaced)
  3. Sekoya Pop — 14% ⬆️ (growing fast, preferred in China: 24% of China shipments)
  4. Rocío — growing
  5. Mágica — growing (19% of China shipments in 2024/25!)
  6. Atlasblue — present
  7. Eureka / Eureka Sunrise — growing
  8. Scintilla — present
  9. Stella Blue / Kirra / Terrapin — other notable varieties
  
  Other: Emerald, Jupiterblue, Bella, Kestrel, Springhigh, Bonita,
         Snowchaser, Sekoya Beauty, Magnifica, First Blush, Salvador,
         Arana, Biancablue, Stellar, Jewel, among others

▶ NORTHERN HIGHBUSH (cold climates — Poland, Canada, NE USA, high Chile):
  Classic proven varieties still dominant in Poland/Eastern Europe:
  - Bluecrop — still most planted worldwide (reliable workhorse)
  - Duke — early season, cold tolerant, very popular Poland
  - Draper — premium, excellent flavor, good shelf life
  - Aurora — very late season, large berry
  - Liberty — late season, excellent flavor
  - Cargo — high yield, firmness
  - Calypso — disease resistant, patented

▶ HALF-HIGH (extreme cold — Scandinavia, Russia, Canada prairies):
  - Northblue — cold hardy to -35°C
  - Polaris — very aromatic, cold tolerant
  - Chippewa — reliable in harsh conditions

▶ NEW EMERGING VARIETIES (various breeders):
  - BerryWorld Orb® — new northern highbush, commercial volumes 2025
  - Eureka Sunrise, Eureka Sunset (Clear genetics)
  - Magnifica™, Bella™, Bonita™, Julieta™ (Clear genetics, Peru)
  - FC11-164 (Fall Creek) — mechanical harvest, trials in Europe/US/Chile
  - Stella Blue — growing presence Peru
  - Arana — appearing in Peru export data

══════════════════════════════════════════════════════════════════
SECTION 7: KEY INDUSTRY TRENDS 2025
══════════════════════════════════════════════════════════════════

1. OVERSUPPLY PRESSURE: Production growing faster than demand.
   IBO warns of "margin squeeze" — growers face lower prices.
   
2. VARIETAL REVOLUTION: Rapid replacement of old varieties (Biloxi→Sekoya/Ventura)
   for better quality, yield, shelf life.

3. MECHANICAL HARVESTING: Fall Creek FC11-164 leading development.
   Critical for labor cost reduction in Europe and USA.

4. CHINA MARKET BOOM: Imports surging. Peru exports to China +153% in 2025.
   Chancay Port dramatically reduces logistics costs Peru→China.

5. MOROCCO RISE: From 636 MT (2009) to 83,000 MT (2024).
   Now 4th largest exporter. Disrupting EU early-season supply.

6. SEGMENTATION: Premium (Sekoya, Demba) vs commodity (Biloxi, Bluecrop).
   "Blueberries are no longer a generic product" — Sekoya CEO.

7. YEAR-ROUND SUPPLY: 12-month availability now standard in EU and USA.

8. PRICE DECLINE: Average international price -3% in 2025 ($6.20/kg vs $6.43).
══════════════════════════════════════════════════════════════════
SECTION 9: BREAKING NEWS — JUNE 2026 (CURRENT SEASON)
Sources: Bronisze/sadyogrody.pl/jagodnik.pl/fresh-market.pl/hortidaily/IBO/Tridge/EastFruit
══════════════════════════════════════════════════════════════════

THIS IS THE MOST CURRENT DATA — June 21, 2026

SERBIA — June 2026 PEAK SEASON:
- Production: 6,000-7,000 MT/year, ~2,500 ha, 4,161 growers (2023)
- Duke variety = 90-95% of all Serbian blueberries — season June to mid-July
- Export markets: Netherlands, Germany, Poland, Czech Republic, UK
- PRICES June 2026: Started at EUR 6.50-7.00/kg early June → NOW DROPPING sharply
  as volumes spike. Mid-June trend: toward EUR 4.00-5.00/kg
- This Serbian surge is pulling down ALL European blueberry prices simultaneously
- 80%+ exported in retail packs (500g) directly to EU supermarket chains
- Labor costs: +12-15% vs 2024 — margins squeezed
- Quality 2026: GOOD — no major frost damage unlike Poland
- New investment: Serbia expanding facilities, targeting China market access (since 2023)

ROMANIA — June 2026 STARTING:
- Season: June 15 - August 31
- New varieties from 2021 onwards: Sekoya (Fall Creek/Agrovision)
- First commercial volumes new varieties 2026 (~450-500 MT)
- Large volumes expected from 2027 (100+ ha new plantings)
- Romania follows Serbia by ~3 weeks on the EU market
- Target: become largest premium blueberry producer in Europe

CROATIA: Not a significant commercial exporter — domestic market only.

POLAND — June 2026 VERIFIED DATA:
Weather: April-May 2026 frosts (coldest May in 34 years)
- April 26-30: frosts to -10C locally — flowers severely damaged at bloom stage
- May 3-14: Arctic air sweeping country every night for 12 days
- Government compensation: ARiMR payments for losses over 70%
- Final verdict: season similar to 2025 — NOT catastrophic, borówek nie zabraknie

PRICES Poland June 2026 (VERIFIED from Bronisze/sadyogrody.pl):
- Tunnel borówki (first Polish, under cover): 20-45 zł/kg depending on caliber/quality
- Field crop: NOT YET — starts first week of July
- Imported borówki (Serbia/Peru): 30-40 zł/kg wholesale
- Retail stores: 45-70 zł/kg in June (pre-season)
- March 2026 import price in Krakow: EUR 10.47-14.66/kg
- "Ceny importowanych borówek mocno w dół" — fresh-market.pl, May 20, 2026

WHY SERBIAN PRICE DROP MATTERS FOR POLAND:
Serbia farm gate EUR 5-7/kg + transport EUR 1.5-2/kg + margins = EUR 7-9/kg
= approx. 30-38 zł/kg wholesale Poland — so Serbian prices DO match Polish wholesale.
Any further Serbian price drop will directly pull Polish import prices down.

EUROPE SUPPLY CHAIN June 2026:
- Spain (Huelva): season ENDING — Germany main destination (June 16)
- Morocco: season COMPLETE
- Serbia: PEAK NOW — volumes causing price drops across EU
- Romania: STARTING (June 15+)
- Germany/Netherlands domestic: 2-3 weeks away (early July)
- Poland field crop: first week of July
- Georgia (country): Active May-June, supplying Germany/Poland/Russia/Dubai

GLOBAL PRICE REFERENCES Q4 2025 - Q1 2026 (Tridge/IMARC verified):
- USA: $4,405/MT = $4.41/kg (March 2026, downward trend)
- Netherlands wholesale: $4,062/MT = $4.06/kg (March 2026)
- Belgium: $6,507/MT = $6.51/kg (December 2025, premium market)
- China: $6,790/MT = $6.79/kg (Q1 2026 — highest price globally)
- Peru FOB: $4,193/MT = $4.19/kg (March 2026)
- Chile Nov 2025: $8.92/kg (Tridge transaction data)
- Netherlands Nov 2025: $13.50/kg (premium retail)


══════════════════════════════════════════════════════════════════
SECTION 8: SEASON 2025/26 — CURRENT DATA & FORECASTS
══════════════════════════════════════════════════════════════════

⚠️ NOTE ON DATA CURRENCY (as of June 2026):
- Season 2025/26 NOW COMPLETE for Peru/Chile (May–April cycle)
- Season 2025 complete for USA/Poland/Europe (April–September 2025)
- Morocco/Spain 2026 seasons complete (Feb–June 2026)
- Season 2026/27 for Peru/Chile begins August 2026

🇵🇪 PERU SEASON 2025/26 — FINAL RESULTS (FreshPlaza/Proarándanos, May 2026):
- Total exports: 380,260 MT (+21.5% vs 2024/25!)
- Slight miss vs forecast of 400,000 MT
- Peak: October (90,000+ MT), September (75,000+ MT), November (66,000+ MT)
- La Libertad: 189,700 MT (50%), Lambayeque: 89,500 MT, Ica: 50,000+ MT (+48%!)
- Outlook 2026/27: growth expected, El Niño risk factor

🇨🇱 CHILE SEASON 2025/26 — (Frutas de Chile, Oct 2025):
- Fresh exports: +1% vs 2024/25
- Protected/new varieties: +67% (now 35% of total, up from 21%!)
- Traditional varieties: -17% (phased out)
- Frozen: 161,000+ MT record (43% of all Chilean shipments — strategic channel!)

🇺🇸 USA SEASON 2025 (USDA/NABC):
- Highbush: ~9% lower than 2024 (weather impact, mainly processing affected)
- Wild (Maine): 45M lbs vs 90.8M lbs in 2024 (-50%! Rain+drought)
- Imports: record 720B lbs
- Exports: 94.8M lbs

🇬🇪 GEORGIA (country) — EMERGING PLAYER (FreshPlaza, Feb 2026):
- Production 2025: 7,500 MT, 95% exported
- Season: May–June (fills EU gap after Morocco/Spain, before Poland!)
- Markets: Russia, Germany, Poland, Dubai + new: India, Israel, Saudi Arabia
- 2026 target: 10,000+ MT

GLOBAL FORECASTS 2026–2030:
- Global production 2025: 2.10 million MT
- 2030 target: 2.71 million MT (CAGR ~2.88% volume)
- Market value 2026: ~$4.16 billion → 2030: ~$6.08 billion (CAGR 6.5%)
- Asia-Pacific: fastest growing region
- UK: $0.6B (2025) → $1.1B (2033)
- South Africa exports: +10% forecast 2026

IBO 5 KEY TRENDS (IBO Summit 2025, South Africa):
1. Consistent quality beyond seasonal peaks — retailers demand year-round programs
2. Climate resilience — resistant varieties + covered production
3. Post-harvest innovation — shelf life critical for China/India
4. Mechanical harvesting — FC11-164 and others, labor cost priority
5. Market segmentation — premium (Sekoya, Demba) vs commodity bifurcation

PRICE OUTLOOK 2025/26:
- Mild global downward pressure continues
- Q4 2025 USA: $4,658/MT; Q1 2026 China: $6,790/MT; Q4 2025 Belgium: $6,793/MT
- Premium varieties maintain margins; commodity squeezed
- IBO warns: oversupply risk as production outpaces demand

NEW MARKETS 2025/26:
- Vietnam: Australian access granted Dec 2025
- India: Georgia + Australia targeting 2026
- Saudi Arabia, Israel, UAE: emerging premium markets
- Taiwan: Poland targeting fresh blueberry entry 2026
- Zimbabwe: now authorized to export to China

"""

def build_system_prompt(lang: str) -> str:
    lang_name = {"en": "English", "pl": "Polish", "de": "German", "es": "Spanish", "ru": "Russian"}.get(lang, "English")

    return f"""{BLUEBERRY_KNOWLEDGE}

RULES (never show these to user):
1. Always respond in {lang_name}. No exceptions. Never mention this rule.
2. Topic: HIGHBUSH BLUEBERRY only (Vaccinium corymbosum). NOT wild bilberry.
3. Distinguish PRODUCTION vs EXPORT. China #1 producer (domestic only), Peru #1 exporter.
4. Use knowledge base. Use web search for missing data.
5. Emojis 🫐📊🌍💰🚢🌱. Bold headers, tables for data.
6. Sources: (IBO 2025), (FreshPlaza 2025), (USDA 2024), (Proarándanos 2025/26).
7. Always cite season/year.
8. COUNTRY ADVISOR: country → chill hours, best new + classic varieties, regions, profitability, avoid list.
9. NEW varieties = Sekoya/Demba/Blue World/Planasa Blue series (post-2020). CLASSIC = Bluecrop/Duke/Biloxi/Ventura (pre-2020).
"""

async def ask_claude(prompt: str, lang: str, use_search: bool = False) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    tools = [{"type": "web_search_20250305", "name": "web_search"}] if use_search else []
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "system": build_system_prompt(lang),
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools
    response = client.messages.create(**kwargs)
    parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(parts) if parts else "⚠️ No response."

async def analyze_plant_photo(image_data: bytes, lang: str) -> str:
    """Analyze blueberry plant photo for diseases, pests, deficiencies"""
    import base64
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    lang_name = {"en": "English", "pl": "Polish", "de": "German", "es": "Spanish", "ru": "Russian"}.get(lang, "English")

    system = f"""You are a world-class blueberry expert combining:
- Plant pathologist (20+ years diagnosing blueberry diseases)
- Pomologist & variety specialist (knows 60+ commercial varieties)
- Quality control inspector (knows USDA/EU grade standards and defects)
- Agronomist (nutrition, soil, growing conditions)

═══════════════════════════════════════════
STEP 1: IDENTIFY WHAT IS IN THE PHOTO
═══════════════════════════════════════════
A) FRUIT/BERRIES ONLY → Quality control + variety ID + Brix estimate
B) LEAVES/STEMS/PLANT → Disease/pest/deficiency diagnosis
C) FRUIT + PLANT → Full analysis (both A and B)
D) EARLY STAGE PLANT (young bush, no fruit) → Variety clues from leaf shape/color/growth habit + plant health

═══════════════════════════════════════════
STEP 2A: FRUIT QUALITY CONTROL ANALYSIS
═══════════════════════════════════════════
For each fruit visible, assess:

SIZE GRADING:
- Jumbo: >22mm diameter
- Large: 18-22mm  
- Medium: 14-18mm
- Small: <14mm
- Non-conforming: <12mm (usually rejected)

COLOR ASSESSMENT:
- Uniform deep blue/blue-black = mature, ideal
- Light blue with red areas = underripe
- Shriveled dark = overripe
- Uneven coloring = uneven maturity

BLOOM (waxy coating):
- Heavy bloom = premium quality, excellent shelf life
- Light bloom = reduced shelf life
- No bloom = overhandled, quality degraded

DEFECTS - identify any present:
CATEGORY A DEFECTS (reject):
  - Botrytis (gray mold) — gray fuzzy growth, mushy spots
  - Mummified berries — shriveled, dry, black
  - Cracking/splitting — visible skin breaks (water stress or hail)
  - Bird/insect damage — holes, cavities
  - Severe bruising — large dark soft areas
  - Stem punctures — holes from stem attachment
  
CATEGORY B DEFECTS (downgrade):
  - Scarring — healed skin damage from hail/rubbing
  - Russeting — rough brown skin patches
  - Misshapen — not round
  - Minor bruising — small soft spots
  - Stem damage — torn calyx
  - Rain cracking — fine surface cracks
  - Sunburn — bleached/tan patches

CATEGORY C DEFECTS (minor, acceptable):
  - Minor size variation
  - Light surface marks
  - Slight color variation

BRIX ESTIMATION (visual only, ±2°Brix accuracy):
- Deep blue-black, heavy bloom, firm = likely 12-15°Brix (premium)
- Medium blue, good bloom = likely 10-12°Brix (commercial standard)
- Light blue, some red = likely 8-10°Brix (underripe)
- Dark shriveled = likely 15-18°Brix but overripe (poor texture)
Note: Accurate Brix requires refractometer or NIR spectrometer (SCiO, F750).
Modern iPhone/Samsung NIR sensors are NOT accessible to apps for Brix measurement.

═══════════════════════════════════════════
STEP 2B: PLANT DISEASE/PEST/DEFICIENCY DIAGNOSIS
═══════════════════════════════════════════
FUNGAL DISEASES:
- Botrytis cinerea (Gray Mold) — gray fuzzy growth on berries/flowers/stems. Favors humid conditions. Treatment: iprodione, fenhexamid, cyprodinil/fludioxonil (Switch). Remove infected material.
- Mummyberry (Monilinia vaccinii-corymbosi) — mummified berries, witches' broom shoots in spring. Treatment: myclobutanil, propiconazole at bloom. Critical timing!
- Anthracnose (Colletotrichum acutatum) — salmon-orange spore masses on berries. Treatment: azoxystrobin, fludioxonil post-harvest.
- Powdery Mildew (Erysiphe vaccinii) — white powder on leaves. Treatment: sulfur, potassium bicarbonate, myclobutanil.
- Phytophthora Root Rot — wilting, red-brown roots, poor growth. Treatment: mefenoxam, phosphorous acid. Improve drainage CRITICAL.
- Stem Blight (Botryosphaeria) — brown wilting canes. Prune 30cm below symptoms.
- Fusicoccum Canker — elliptical cankers on stems. Prune and destroy.
- Leaf Spot (Septoria) — brown spots with purple border on leaves.
- Rust (Pucciniastrum vaccinii) — orange pustules under leaves. Treatment: azoxystrobin.
- Exobasidium leaf/fruit gall — pale green/pink swollen galls. Remove by hand.

BACTERIAL DISEASES:
- Crown Gall (Agrobacterium) — rough galls at crown/roots. No cure, remove plant.
- Bacterial Canker — angular water-soaked lesions. Copper sprays preventive.

VIRAL DISEASES:
- Blueberry Shock Virus — sudden blossom/leaf drop in spring, recovery next year.
- Blueberry Scorch Virus — scorched appearance, no recovery. Remove plant.
- Stunt (phytoplasma) — small yellowed leaves, stunted growth. No cure, remove.
- Necrotic Ring Blotch — ring patterns on leaves. No cure.
- Red Ringspot — red rings on berries. No cure.
- Tobacco Ringspot/Tomato Ringspot — necrotic patterns. Remove plant.

PESTS:
- Spotted Wing Drosophila (Drosophila suzukii) — small larvae inside ripe berries. CRITICAL pest. Treatment: spinosad, malathion. Monitor with traps.
- Blueberry Maggot (Rhagoletis mendax) — larvae in berries. Kaolin clay, spinosad.
- Mummyberry Moth — larvae in green berries. Monitor bloom stage.
- Japanese Beetle — skeletonized leaves. Treatment: carbaryl, neem.
- Blueberry Tip Borer — wilted shoot tips. Prune below damage.
- Scale insects — brown/white crusty bumps on stems. Horticultural oil dormant season.
- Spider Mites — fine webbing, stippled leaves. Miticide, high humidity helps.
- Aphids — curled leaves, sticky honeydew. Insecticidal soap, beneficial insects.
- Thrips — silvery scarring on berries/leaves. Spinosad.

NUTRIENT DEFICIENCIES:
- Iron (Fe) deficiency — interveinal chlorosis young leaves (yellow with green veins). pH too high! Lower to 4.5-5.2 with sulfur. Apply chelated iron.
- Magnesium (Mg) — interveinal chlorosis OLDER leaves, red edges. Apply MgSO4.
- Nitrogen (N) — pale/yellow whole plant, red leaves early. Apply ammonium sulfate (NOT nitrate!).
- Potassium (K) — brown leaf margins, poor fruit quality. Apply K2SO4.
- Calcium (Ca) — tipburn, blossom end rot on berries. Foliar CaCl2.
- Boron (B) — hollow berries, shoot dieback. Foliar borax solution.
- Zinc (Zn) — small leaves, stunted shoots. Chelated zinc spray.
- Manganese (Mn) — similar to Fe but less severe. pH related.
- Sulfur (S) — light green/yellow leaves. Apply elemental sulfur.
CRITICAL: Always check soil pH first! pH above 5.5 causes multiple deficiencies simultaneously.

ENVIRONMENTAL/ABIOTIC:
- Frost damage — brown/black flowers, wilted shoots after cold night. No treatment, assess extent.
- Hail damage — round indentations, scarring on berries/leaves. Assess severity.
- Drought stress — leaf curl, wilting, small berries. Irrigation urgently.
- Waterlogging — yellowing, root rot start. Improve drainage.
- Herbicide drift — unusual leaf shapes/colors. Document for insurance.
- Sunscald — bleached/tan patches on sun-exposed berries.

═══════════════════════════════════════════  
STEP 2C: VARIETY IDENTIFICATION
═══════════════════════════════════════════
NORTHERN HIGHBUSH clues:
- Bluecrop: medium-large, light blue, good bloom, flat crown, clusters
- Duke: medium, powder blue, very uniform, tight crown, firm
- Draper: large, light blue, heavy bloom, small crown, very firm
- Aurora: very large, light blue, waxy, late season, excellent flavor
- Liberty: medium-large, dark blue, excellent flavor, loose clusters
- Chandler: VERY large (sometimes >25mm), light blue, irregular shape
- Elliott: medium, firm, tart, very late, loose clusters
- Patriot: medium, dark blue, aromatic, cold hardy

SOUTHERN HIGHBUSH clues:
- Biloxi: medium, powder blue, very productive, loose clusters (declining variety)
- Ventura: large-very large, deep blue, excellent bloom, firm, tight crown (Peru #1)
- O'Neal: large, dark blue, excellent flavor, early season
- Misty: medium, light blue, open growth habit
- Emerald: large, light blue, very firm, excellent shelf life
- Jewel: large, deep blue, very sweet
- Star: large, light blue, excellent flavor
- Sekoya Pop: large-very large, deep blue, EXCEPTIONAL bloom, very firm (China favorite)
- Sekoya Crunch: very firm, excellent shelf life, premium appearance
- Farthing: large, light blue, early, warm climates

HALF-HIGH clues:
- Northblue: small-medium, dark blue, very dark flesh, intense flavor
- Polaris: medium, blue, aromatic
- Chippewa: medium, light blue, upright

PLANASA VARIETIES (Blue series):
- Blue Manila/Maldiva: large, light blue, zero-chill adapted, tropical climates

Always state: MOST LIKELY: [variety] | ALSO POSSIBLE: [variety] | CONFIDENCE: HIGH/MEDIUM/LOW
Explain visual clues used for identification.

═══════════════════════════════════════════
FINAL RESPONSE FORMAT:
═══════════════════════════════════════════
Use appropriate sections based on what photo shows.
Be SPECIFIC and ACTIONABLE — growers need practical advice.
State what you CAN and CANNOT determine from photo alone.
Always recommend consulting local extension service for confirmation.
Respond in {lang_name} ONLY. No other language."""

    image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64,
                    },
                },
                {
                    "type": "text",
                    "text": "Please analyze this blueberry photo. If berries are visible, identify the variety. Always check plant health and diagnose any diseases, pests or deficiencies."
                }
            ],
        }]
    )
    parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(parts) if parts else "⚠️ Could not analyze image."

TOPIC_PROMPTS = {
    "market": {
        "en": "Global highbush blueberry market 2025/26: production volume, market value, growth rate, top regions. Distinguish production vs export. Key numbers only, concise.",
        "pl": "Globalny rynek borówki amerykańskiej 2025/26: produkcja, wartość, wzrost, regiony. Rozróżnij produkcję od eksportu. Tylko kluczowe liczby.",
        "de": "Globaler Heidelbeermarkt 2025/26: Produktion, Wert, Wachstum, Regionen. Produktion vs. Export unterscheiden. Kurz und präzise.",
        "es": "Mercado global arándanos 2025/26: producción, valor, crecimiento, regiones. Distinguir producción de exportación. Solo cifras clave.",
        "ru": "Мировой рынок голубики 2025/26: производство, стоимость, рост, регионы. Отличить производство от экспорта. Только ключевые цифры.",
    },
    "production": {
        "en": "Top 20 highbush blueberry producing countries 2024/25 with MT volumes, key regions, season. Note: China #1 producer (domestic only), Peru #1 exporter. Table format.",
        "pl": "Top 20 krajów produkujących borówkę amerykańską 2024/25: wolumeny MT, regiony, sezon. Chiny nr 1 producent (rynek wewnętrzny), Peru nr 1 eksporter. Format tabeli.",
        "de": "Top 20 Highbush-Produzenten 2024/25: MT, Regionen, Saison. China #1 Produzent (Inland), Peru #1 Exporteur. Tabellenformat.",
        "es": "Top 20 productores highbush 2024/25: TM, regiones, temporada. China #1 productor (doméstico), Perú #1 exportador. Formato tabla.",
        "ru": "Топ-20 производителей высокорослой голубики 2024/25: тонны, регионы, сезон. Китай #1 производитель (внутренний), Перу #1 экспортёр. Таблица.",
    },
    "export": {
        "en": "Global blueberry export 2024/25: 1M MT, $6.73B. Top 10 exporters with MT and $ share. Peru 31% ($2.56B), Morocco rose 7th→4th. Season windows per country. Concise table.",
        "pl": "Globalny eksport borówek 2024/25: 1 mln MT, $6,73 mld. Top 10 eksporterów z MT i udziałem $. Peru 31% ($2,56 mld), Maroko wzrosło z 7 na 4 miejsce. Okna sezonowe. Tabela.",
        "de": "Globaler Export 2024/25: 1 Mio MT, $6,73 Mrd. Top 10 Exporteure mit MT und %. Peru 31%, Marokko 7.→4. Saisonfenster. Kompakte Tabelle.",
        "es": "Exportación global 2024/25: 1M TM, $6.73B. Top 10 exportadores con TM y %. Perú 31%, Marruecos subió 7°→4°. Ventanas temporada. Tabla.",
        "ru": "Мировой экспорт 2024/25: 1 млн тонн, $6,73 млрд. Топ-10 экспортёров с тоннами и долей. Перу 31%, Марокко с 7 на 4 место. Сезонные окна. Таблица.",
    },
    "destinations": {
        "en": "Key blueberry import markets 2025/26: USA (largest, 200k MT), China (fastest +153% from Peru, Chancay Port), Europe (Morocco→Spain→Poland→S.Hemisphere supply chain), Russia (post-2022 suppliers). Prices per market.",
        "pl": "Kluczowe rynki importu borówek 2025/26: USA (największy, 200k MT), Chiny (najszybszy +153% z Peru, port Chancay), Europa (Maroko→Hiszpania→Polska→PołHem), Rosja (dostawcy po 2022). Ceny per rynek.",
        "de": "Wichtigste Importmärkte 2025/26: USA (200k MT), China (+153% aus Peru, Chancay), Europa (Lieferkette), Russland (Post-2022). Preise je Markt.",
        "es": "Mercados importación clave 2025/26: USA (200k TM), China (+153% Perú, Chancay), Europa (cadena suministro), Rusia (post-2022). Precios por mercado.",
        "ru": "Ключевые рынки импорта 2025/26: США (200к тонн), Китай (+153% из Перу, Чанкай), Европа (цепочка поставок), Россия (после 2022). Цены по рынкам.",
    },
    "prices": {
        "en": "Current blueberry market & wholesale prices 2025/26: Serbia farm gate June 2026 EUR 5-7/kg (dropping fast at peak). Poland wholesale Bronisze June 2026: tunnel 20-45 zł/kg, Serbian import 30-40 zł/kg. Peru FOB $4.19/kg (March 2026, down). Netherlands wholesale $4.06/kg. Belgium $6.51/kg. China $6.79/kg (highest globally). USA $4.41/kg. Retail: USA $8-16/kg, Germany €12-24/kg, Poland 45-70 zł/kg pre-season. Frozen bulk €0.90-1.50/kg. Overall trend: downward pressure globally.",
        "pl": "Aktualne ceny rynkowe i hurtowe borówek 2025/26: Serbia skup czerwiec 2026 EUR 5-7/kg (gwałtownie spada przy szczycie). Polska hurt Bronisze czerwiec 2026: tunelowe 20-45 zł/kg, import serbski 30-40 zł/kg. Peru FOB $4,19/kg (marzec 2026). Holandia hurt $4,06/kg. Belgia $6,51/kg. Chiny $6,79/kg (najdrożej). USA $4,41/kg. Detal: USA $8-16/kg, Niemcy €12-24/kg, Polska 45-70 zł/kg. Mrożone €0,90-1,50/kg. Trend: globalna presja spadkowa.",
        "de": "Aktuelle Markt- und Großhandelspreise 2025/26: Serbien Erzeugerpreis Juni 2026 EUR 5-7/kg (fällt stark). Polen Großhandel Bronisze Juni: Tunnel 20-45 zł/kg, Import 30-40 zł/kg. Peru FOB $4,19/kg. NL $4,06/kg. BE $6,51/kg. China $6,79/kg. USA $4,41/kg. Einzelhandel: USA, DE, PL, CN. TK €0,90-1,50/kg. Trend: globaler Preisdruck.",
        "es": "Precios actuales mercado y mayorista 2025/26: Serbia productor junio 2026 EUR 5-7/kg (bajando rápido). Polonia mayorista Bronisze junio: túnel 20-45 zł/kg, importado 30-40 zł/kg. Perú FOB $4,19/kg. NL $4,06/kg. BE $6,51/kg. China $6,79/kg. USA $4,41/kg. Retail: USA, DE, PL, CN. Congelado €0,90-1,50/kg. Tendencia: presión bajista global.",
        "ru": "Актуальные рыночные и оптовые цены 2025/26: Сербия скупка июнь 2026 EUR 5-7/кг (резко падает на пике). Польша опт Брониши июнь: тепличные 20-45 зл/кг, импорт 30-40 зл/кг. Перу FOB $4,19/кг. Нидерланды $4,06/кг. Бельгия $6,51/кг. Китай $6,79/кг. США $4,41/кг. Розница: США, Германия, Польша, Китай. Замороженные €0,90-1,50/кг. Тренд: глобальное снижение.",
    },
    "varieties": {
        "en": "NEW blueberry varieties 2020-2026: SEKOYA low-chill (Pop-China fav, Beauty, Crunch, Grande) + high-chill (Nova, ArabellaBlue, Apex 2026). Demba/Blue World (Taste Award: Demba, Dana). Planasa (Blue Manila, Madeira, Maldiva-zero chill). BerryWorld Orb, PeachyBlue. Best climate for each.",
        "pl": "NOWE odmiany 2020-2026: SEKOYA low-chill (Pop-Chiny, Beauty, Crunch, Grande) + high-chill (Nova, ArabellaBlue, Apex 2026). Demba/Blue World (nagroda: Demba, Dana). Planasa (Blue Manila, Madeira, Maldiva-zero chill). BerryWorld Orb, PeachyBlue. Klimat dla każdej.",
        "de": "NEUE Sorten 2020-2026: SEKOYA (Pop, Beauty, Crunch, Nova, ArabellaBlue, Apex) + Demba/Blue World (Taste Award) + Planasa (Blue Manila, Madeira, Maldiva) + BerryWorld Orb. Klima je Sorte.",
        "es": "NUEVAS variedades 2020-2026: SEKOYA (Pop, Beauty, Crunch, Nova, ArabellaBlue, Apex) + Demba/Blue World (Taste Award) + Planasa (Blue Manila, Madeira, Maldiva) + BerryWorld Orb. Clima por variedad.",
        "ru": "НОВЫЕ сорта 2020-2026: SEKOYA (Pop, Beauty, Crunch, Nova, ArabellaBlue, Apex) + Demba/Blue World (Taste Award) + Planasa (Blue Manila, Madeira, Maldiva) + BerryWorld Orb. Климат для каждого.",
    },
    "classics": {
        "en": "Classic blueberry varieties pre-2020: Northern Highbush high-chill (Bluecrop, Duke, Draper, Aurora, Liberty, Chandler, Patriot, Elliott). Southern Highbush low-chill (Biloxi, Ventura, O'Neal, Misty, Emerald, Jewel). Half-High extreme cold (Northblue, Polaris, Chippewa). Climate requirements table.",
        "pl": "Klasyczne odmiany pre-2020: Północne high-chill (Bluecrop, Duke, Draper, Aurora, Liberty, Chandler, Patriot). Południowe low-chill (Biloxi, Ventura, O'Neal, Misty, Emerald). Półwysokopienne (Northblue, Polaris, Chippewa). Tabela wymagań klimatycznych.",
        "de": "Klassische Sorten pre-2020: Nord-Highbush (Bluecrop, Duke, Draper, Aurora, Liberty) + Süd-Highbush (Biloxi, Ventura, O'Neal, Misty) + Half-High (Northblue, Polaris). Klimatabelle.",
        "es": "Variedades clásicas pre-2020: Northern Highbush (Bluecrop, Duke, Draper, Aurora, Liberty) + Southern Highbush (Biloxi, Ventura, O'Neal, Misty) + Half-High (Northblue, Polaris). Tabla climática.",
        "ru": "Классические сорта до 2020: Северные (Bluecrop, Duke, Draper, Aurora, Liberty) + Южные (Biloxi, Ventura, O'Neal, Misty) + Полувысокорослые (Northblue, Polaris). Таблица климата.",
    },
    "nursery": {
        "en": "Top 5 global blueberry nurseries: 1) Fall Creek® USA - 40M+ plants/yr, 59 countries, SEKOYA platform. 2) Planasa Spain - 1B plants/yr total, 7000 staff, Blue Manila/Madeira/Maldiva. 3) Onubafruit/FV.BV - Blue World (Demba, Dana). 4) Oregon Blueberry USA - largest N.America wholesale. 5) Lorsena Spain - EU specialist. Plant costs: $0.50-5.00.",
        "pl": "Top 5 szkółek borówki: 1) Fall Creek® USA - 40 mln szt/rok, 59 krajów, SEKOYA. 2) Planasa Hiszpania - 1 mld szt/rok łącznie, 7000 prac., Blue Manila/Madeira/Maldiva. 3) Onubafruit/FV.BV - Blue World (Demba, Dana). 4) Oregon Blueberry USA - największa hurt. Ameryka Pn. 5) Lorsena Hiszpania - specjalista EU. Ceny: $0,50-5,00.",
        "de": "Top 5 Baumschulen: 1) Fall Creek® USA 40M+/Jahr, 59 Länder. 2) Planasa Spanien 1Mrd/Jahr, 7000 MA. 3) Onubafruit/FV.BV Blue World. 4) Oregon Blueberry USA. 5) Lorsena Spanien. Preise $0,50-5.",
        "es": "Top 5 viveros: 1) Fall Creek® USA 40M+/año, 59 países. 2) Planasa España 1000M/año, 7000 emp. 3) Onubafruit/FV.BV Blue World. 4) Oregon Blueberry USA. 5) Lorsena España. Precios $0,50-5.",
        "ru": "Топ-5 питомников: 1) Fall Creek® США 40М+/год, 59 стран. 2) Planasa Испания 1 млрд/год, 7000 сотр. 3) Onubafruit/FV.BV Blue World. 4) Oregon Blueberry США. 5) Lorsena Испания. Цены $0,50-5.",
    },
    "news": {
        "en": "Report the CURRENT situation in June 2026 blueberry markets using Section 9: Serbia price crash details, Poland frost damage update, Romania start, European wholesale prices now. Be specific with numbers.",
        "pl": "Podaj AKTUALNĄ sytuację na rynku borówek czerwiec 2026 z Sekcji 9: szczegóły spadku cen w Serbii, szkody przymrozkowe w Polsce, start Rumunii, europejskie ceny hurtowe teraz. Podaj konkretne liczby.",
        "de": "Aktuelle Situation Juni 2026 aus Abschnitt 9: Serbien Preiseinbruch, Polen Frostschäden, Rumänien Saisonstart, europäische Großhandelspreise. Konkrete Zahlen.",
        "es": "Situación ACTUAL junio 2026 de Sección 9: caída precios Serbia, daños heladas Polonia, inicio Rumanía, precios mayoristas europeos ahora. Números específicos.",
        "ru": "ТЕКУЩАЯ ситуация июнь 2026 из Раздела 9: обвал цен в Сербии, ущерб от заморозков в Польше, старт Румынии, европейские оптовые цены. Конкретные цифры.",
    },
    "photo": {
        "en": "You clicked Photo Analysis! Please send me a photo of your blueberry plant, berries, or leaves. I will: 1) Identify the variety (if berries visible) 2) Diagnose any diseases, pests or nutrient deficiencies 3) Recommend treatment. Just send the photo now! 📸",
        "pl": "Kliknąłeś Analizę Zdjęcia! Wyślij mi zdjęcie swojej borówki — owoców, liści lub krzewu. Zrobię: 1) Rozpoznam odmianę (jeśli widać owoce) 2) Zdiagnozuję choroby, szkodniki lub niedobory 3) Zaproponuję leczenie. Wyślij zdjęcie teraz! 📸",
        "de": "Sie haben Foto-Analyse gewählt! Senden Sie mir ein Foto Ihrer Heidelbeerpflanze. Ich werde: 1) Sorte identifizieren 2) Krankheiten/Schädlinge diagnostizieren 3) Behandlung empfehlen. Foto jetzt senden! 📸",
        "es": "¡Elegiste Análisis de Foto! Envíame una foto de tu planta de arándano. Haré: 1) Identificar variedad 2) Diagnosticar enfermedades/plagas 3) Recomendar tratamiento. ¡Envía la foto ahora! 📸",
        "ru": "Вы выбрали Анализ Фото! Отправьте мне фото вашего растения голубики. Я: 1) Определю сорт 2) Диагностирую болезни/вредителей 3) Порекомендую лечение. Отправьте фото сейчас! 📸",
    },
    "roi": {
        "en": "You are a blueberry investment advisor. Ask the user: 1) Country/region 2) Area in hectares 3) Variety (new like Sekoya/Demba or classic like Bluecrop/Duke) 4) Market target (fresh export/domestic/frozen). Then calculate: setup costs (land prep, plants, irrigation, nets, labor), annual operating costs, expected yield (MT/ha), expected price, gross revenue, net profit, and payback period in years. Use realistic 2025/26 data. Be specific with numbers. Format as a clear financial summary.",
        "pl": "Jesteś doradcą inwestycyjnym ds. borówek. Zapytaj użytkownika: 1) Kraj/region 2) Powierzchnia w ha 3) Odmiana (nowa jak Sekoya/Demba czy klasyczna jak Bluecrop/Duke) 4) Rynek docelowy (świeży eksport/krajowy/mrożony). Następnie oblicz: koszty założenia, koszty operacyjne, spodziewany plon (t/ha), cena, przychód brutto, zysk netto i okres zwrotu. Użyj danych 2025/26. Konkretne liczby. Format jako jasne podsumowanie finansowe.",
        "de": "Sie sind ein Heidelbeer-Investitionsberater. Fragen Sie: 1) Land/Region 2) Fläche in Hektar 3) Sorte 4) Zielmarkt. Berechnen Sie dann: Einrichtungskosten, Betriebskosten, erwarteter Ertrag, Preis, Bruttoeinnahmen, Nettogewinn, Amortisationszeit. Daten 2025/26. Klare Finanzzusammenfassung.",
        "es": "Eres asesor de inversión en arándanos. Pregunta: 1) País/región 2) Área en hectáreas 3) Variedad 4) Mercado objetivo. Calcula: costos de establecimiento, costos operativos, rendimiento esperado, precio, ingresos brutos, ganancia neta, período de recuperación. Datos 2025/26. Resumen financiero claro.",
        "ru": "Вы инвестиционный советник по голубике. Спросите: 1) Страна/регион 2) Площадь в га 3) Сорт 4) Целевой рынок. Рассчитайте: затраты на создание, операционные расходы, ожидаемый урожай, цена, валовой доход, чистая прибыль, срок окупаемости. Данные 2025/26. Чёткое финансовое резюме.",
    },
    "currency": {
        "en": "Current blueberry price converter and market rates June 2026. Show prices in all major currencies: EUR, USD, PLN, GBP, CNY, RUB, UAH, RON, RSD (Serbian Dinar), MAD (Moroccan Dirham). Use verified June 2026 exchange rates. Show: Serbia farm gate EUR 5-7/kg in all currencies, Peru FOB $4.19/kg in all currencies, Poland wholesale 30-40 PLN/kg in all currencies, Netherlands wholesale $4.06/kg in all currencies, China market $6.79/kg in all currencies. Also show retail prices per country. User can ask: 'convert 5 EUR to PLN for blueberry price' or 'what is 40 PLN/kg in EUR?'",
        "pl": "Przelicznik cen borówek i aktualne kursy czerwiec 2026. Pokaż ceny we wszystkich głównych walutach: EUR, USD, PLN, GBP, CNY, RUB, UAH, RON, RSD, MAD. Użyj kursów z czerwca 2026. Pokaż: Serbia skup EUR 5-7/kg we wszystkich walutach, Peru FOB $4,19/kg, Polska hurt 30-40 PLN/kg, Holandia $4,06/kg, Chiny $6,79/kg we wszystkich walutach. Też ceny detaliczne. Użytkownik może pytać: 'przelicz 5 EUR na PLN dla ceny borówki'.",
        "de": "Heidelbeer-Preisrechner und Wechselkurse Juni 2026. Preise in EUR, USD, PLN, GBP, CNY, RUB, RON, RSD, MAD. Serbien Erzeuger EUR 5-7/kg, Peru FOB $4,19/kg, Polen Großhandel 30-40 PLN/kg, NL $4,06/kg, China $6,79/kg — alle in allen Währungen.",
        "es": "Conversor de precios de arándanos y tasas de cambio junio 2026. Precios en EUR, USD, PLN, GBP, CNY, RUB, RON, RSD, MAD. Serbia productor EUR 5-7/kg, Perú FOB $4,19/kg, Polonia mayorista 30-40 PLN/kg, NL $4,06/kg, China $6,79/kg — todos en todas las divisas.",
        "ru": "Конвертер цен на голубику и курсы валют июнь 2026. Цены в EUR, USD, PLN, GBP, CNY, RUB, UAH, RON, RSD, MAD. Сербия EUR 5-7/кг, Перу FOB $4,19/кг, Польша опт 30-40 зл/кг, Нидерланды $4,06/кг, Китай $6,79/кг — всё во всех валютах.",
    },
    "health": {
        "en": "Comprehensive blueberry health benefits guide: 1) ANTIOXIDANTS — ORAC value 9,621 μmol TE/100g (highest among common fruits), anthocyanins (malvidin, delphinidin, cyanidin, petunidin, peonidin), pterostilbene, resveratrol. 2) BRAIN HEALTH — studies show 26% reduction in cognitive decline (Harvard 2012, 16,000 women), improve memory and motor skills, cross blood-brain barrier. 3) HEART — lower LDL oxidation, reduce blood pressure by 4-6mmHg, reduce heart attack risk 32% (women, Harvard Nurses Study). 4) DIABETES — low GI (53), improve insulin sensitivity, regulate blood glucose. 5) CANCER — anthocyanins inhibit tumor cell growth (colon, breast, liver cancer studies), pterostilbene more bioavailable than resveratrol. 6) EYES — lutein, zeaxanthin protect against macular degeneration, improve night vision. 7) GUT HEALTH — prebiotic fiber, polyphenols feed beneficial bacteria. 8) ANTI-AGING — reduce DNA damage, slow cellular aging. 9) SPORTS PERFORMANCE — reduce muscle damage, faster recovery (studies: 300g before exercise). 10) NUTRITION per 100g: 57 kcal, 14.5g carbs, 2.4g fiber, 0.7g protein, Vitamin C 9.7mg, K 19μg, Mn 0.34mg. Fresh vs frozen — frozen retains 90%+ of antioxidants. Wild blueberries (bilberry) have 2-3x more anthocyanins than cultivated.",
        "pl": "Kompleksowy przewodnik po właściwościach zdrowotnych borówki: 1) ANTYOKSYDANTY — ORAC 9621 μmol TE/100g (najwyższy wśród popularnych owoców), antocyjany (malwidyna, delfinidyna, cjanidyna), pterostilben, resweratrol. 2) MÓZG — badania pokazują 26% redukcję spadku funkcji poznawczych (Harvard 2012, 16.000 kobiet), poprawa pamięci i motoryki, przenikają barierę krew-mózg. 3) SERCE — obniżenie utleniania LDL, redukcja ciśnienia o 4-6mmHg, zmniejszenie ryzyka zawału o 32%. 4) CUKRZYCA — niski IG (53), poprawa wrażliwości na insulinę. 5) RAK — antocyjany hamują wzrost komórek nowotworowych (okrężnica, pierś, wątroba). 6) OCZY — luteina, zeaksantyna chronią plamkę. 7) JELITA — błonnik prebiotyczny, polifenole odżywiają dobre bakterie. 8) SPORT — redukcja uszkodzeń mięśni, szybsza regeneracja (300g przed treningiem). 9) WARTOŚCI odżywcze/100g: 57 kcal, 14,5g węglowodanów, 2,4g błonnika, wit. C 9,7mg. Mrożone zachowują 90%+ antyoksydantów.",
        "de": "Umfassender Gesundheitsleitfaden Heidelbeeren: ORAC 9.621 μmol TE/100g, Anthocyane, Pterostilben. Gehirn: -26% kognitive Abnahme (Harvard 2012). Herz: -32% Herzinfarktrisiko, -4-6mmHg Blutdruck. Diabetes: GI 53, Insulinsensitivität. Krebs: Anthocyane hemmen Tumorwachstum. Augen: Lutein, Zeaxanthin. Darm: Präbiotika. Sport: Muskelregeneration. 100g: 57kcal, 14,5g KH, 2,4g Ballaststoffe, Vit.C 9,7mg.",
        "es": "Guía completa beneficios salud arándanos: ORAC 9.621 μmol TE/100g, antocianinas, pterostilbeno. Cerebro: -26% declive cognitivo (Harvard 2012). Corazón: -32% infarto, -4-6mmHg presión. Diabetes: IG 53, sensibilidad insulina. Cáncer: antocianinas inhiben tumores. Ojos: luteína, zeaxantina. Intestino: prebióticos. Deporte: recuperación muscular. 100g: 57kcal, 14,5g carbos, 2,4g fibra, Vit.C 9,7mg.",
        "ru": "Полное руководство по пользе черники для здоровья: ORAC 9621 мкмоль TE/100г, антоцианы, птеростильбен. Мозг: -26% снижение когнитивных функций (Гарвард 2012). Сердце: -32% риск инфаркта, -4-6мм рт.ст. давление. Диабет: ГИ 53, чувствительность к инсулину. Рак: антоцианы подавляют опухоли. Глаза: лютеин, зеаксантин. Кишечник: пребиотики. Спорт: восстановление мышц. 100г: 57 ккал, 14,5г углеводов, 2,4г клетчатки, Вит.С 9,7мг.",
    },
    "search": {
        "en": "Search web for latest 2025-2026 blueberry news from FreshPlaza, IBO, Proarándanos. Current prices, export data, new varieties. Combine with knowledge base.",
        "pl": "Szukaj najnowszych wiadomości borówkowych 2025-2026 z FreshPlaza, IBO, Proarándanos. Aktualne ceny, eksport, nowe odmiany.",
        "de": "Aktuelle Heidelbeernews 2025-2026 von FreshPlaza, IBO suchen. Preise, Export, neue Sorten.",
        "es": "Buscar noticias arándanos 2025-2026 FreshPlaza, IBO, Proarándanos. Precios actuales, exportación, nuevas variedades.",
        "ru": "Поиск новостей черники 2025-2026 с FreshPlaza, IBO, Proarándanos. Цены, экспорт, новые сорта.",
    },
}

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
        [InlineKeyboardButton(labels["roi"],          callback_data="topic_roi"),
         InlineKeyboardButton(labels["currency"],     callback_data="topic_currency")],
        [InlineKeyboardButton(labels["health"],       callback_data="topic_health"),
         InlineKeyboardButton(labels["search"],       callback_data="topic_search")],
        [InlineKeyboardButton(labels["lang"],         callback_data="choose_lang")],
    ]
    return InlineKeyboardMarkup(keyboard)

def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
        for code, name in LANGUAGES.items()
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user = update.effective_user
    s = load_stats()
    is_new = str(user.id) not in s["users"]

    # Show welcome message first
    await update.message.reply_text(WELCOME[lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))

    # Show sponsor ad only to NEW users
    if is_new:
        ad_texts = {
            "en": (
                "🌱 *Sponsored · Partner of BlueberryBot*\n\n"
                "**NanoGro Aqua Forest** — biostimulant for professional cultivation\n"
                "Improves root development, stress resistance and yield quality.\n"
                "Trusted by blueberry growers across Europe.\n\n"
                "🔗 [Learn more → agrarius.eu](https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/)"
            ),
            "pl": (
                "🌱 *Sponsor · Partner BlueberryBot*\n\n"
                "**NanoGro Aqua Forest** — biostymulator dla profesjonalnych upraw\n"
                "Poprawia ukorzenianie, odporność na stres i jakość plonów.\n"
                "Stosowany przez plantatorów borówek w całej Europie.\n\n"
                "🔗 [Dowiedz się więcej → agrarius.eu](https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/)"
            ),
            "de": (
                "🌱 *Gesponsert · Partner von BlueberryBot*\n\n"
                "**NanoGro Aqua Forest** — Biostimulans für professionellen Anbau\n"
                "Verbessert Wurzelentwicklung, Stressresistenz und Ertragsqualität.\n\n"
                "🔗 [Mehr erfahren → agrarius.eu](https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/)"
            ),
            "es": (
                "🌱 *Patrocinado · Partner de BlueberryBot*\n\n"
                "**NanoGro Aqua Forest** — bioestimulante para cultivo profesional\n"
                "Mejora el desarrollo radicular, resistencia al estrés y calidad del rendimiento.\n\n"
                "🔗 [Saber más → agrarius.eu](https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/)"
            ),
            "ru": (
                "🌱 *Реклама · Партнёр BlueberryBot*\n\n"
                "**NanoGro Aqua Forest** — биостимулятор для профессионального выращивания\n"
                "Улучшает корнеобразование, устойчивость к стрессу и качество урожая.\n\n"
                "🔗 [Узнать больше → agrarius.eu](https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/)"
            ),
        }
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        ad_button = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🌱 NanoGro Aqua Forest → agrarius.eu",
                url="https://agrarius.eu/en/our-solutions/specialised-products-for-forestry-cultivation/nanogro-aqua-forest/"
            )
        ]])
        await update.message.reply_text(
            ad_texts.get(lang, ad_texts["en"]),
            parse_mode="Markdown",
            reply_markup=ad_button,
            disable_web_page_preview=False
        )
        track(user.id, user.username or "anon", lang, "question", "NEW USER /start", tg_lang_code=user.language_code)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(WELCOME[lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask <question> command"""
    lang = get_lang(context)
    user = update.effective_user
    question = " ".join(context.args) if context.args else ""

    if not question:
        hints = {
            "en": "💡 Usage: /ask <your question>\n\nExamples:\n/ask best varieties for Poland\n/ask blueberry price in China 2025\n/ask how many tonnes does Peru export",
            "pl": "💡 Użycie: /ask <pytanie>\n\nPrzykłady:\n/ask najlepsze odmiany do Polski\n/ask cena borówek w Chinach 2025\n/ask ile ton eksportuje Peru",
            "de": "💡 Verwendung: /ask <Frage>\n\nBeispiele:\n/ask beste Sorten für Polen\n/ask Heidelbeerpreis China 2025",
            "es": "💡 Uso: /ask <pregunta>\n\nEjemplos:\n/ask mejores variedades para Polonia\n/ask precio arándanos China 2025",
            "ru": "💡 Использование: /ask <вопрос>\n\nПримеры:\n/ask лучшие сорта для Польши\n/ask цена черники в Китае 2025",
        }
        await update.message.reply_text(hints.get(lang, hints["en"]))
        return

    track(user.id, user.username or "anon", lang, "question", f"/ask {question}", tg_lang_code=user.language_code)

    thinking = {"en": "🫐 Analyzing...", "pl": "🫐 Analizuję...", "de": "🫐 Analysiere...",
                "es": "🫐 Analizando...", "ru": "🫐 Анализирую..."}
    msg = await update.message.reply_text(thinking.get(lang, "🫐 Thinking..."))
    try:
        response = await ask_claude(question, lang, use_search=True)
        if len(response) > 4000:
            response = response[:3990] + "\n\n_(truncated)_"
        await msg.edit_text(response, parse_mode="Markdown")
        await update.message.reply_text("─" * 20, reply_markup=main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Ask error: {e}")
        await msg.edit_text("⚠️ Error. Please try again.")

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
        loading = {"en": "⏳ Analyzing market data...", "pl": "⏳ Analizuję dane rynkowe...",
                   "de": "⏳ Marktdaten werden analysiert...", "es": "⏳ Analizando datos...",
                   "ru": "⏳ Анализирую данные..."}
        await query.edit_message_text(loading.get(lang, "⏳ Loading..."))
        use_search = (topic == "search")
        prompt = TOPIC_PROMPTS.get(topic, {}).get(lang) or TOPIC_PROMPTS.get(topic, {}).get("en", "Tell me about blueberries.")
        user = query.from_user
        track(user.id, user.username or "anon", lang, "topic", topic, tg_lang_code=user.language_code)
        try:
            response = await ask_claude(prompt, lang, use_search=use_search)
            if len(response) > 4000:
                response = response[:3990] + "\n\n_(truncated)_"
            await query.edit_message_text(response, parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("⚠️ Error. Please try again.", reply_markup=main_menu_keyboard(lang))

# ── Analytics ──────────────────────────────────────────────────────────────
import json
from datetime import datetime

STATS_FILE = "/tmp/blueberry_stats.json"

def load_stats():
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except:
        return {"users": {}, "topics": {}, "questions": [], "total": 0}

def save_stats(s):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(s, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Stats: {e}")

# Telegram language_code → country mapping
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
    "uz": "🇺🇿 Uzbekistan", "lt": "🇱🇹 Lithuania", "lv": "🇱🇻 Latvia",
    "et": "🇪🇪 Estonia", "mk": "🇲🇰 Macedonia", "sq": "🇦🇱 Albania",
    "ms": "🇲🇾 Malaysia", "id": "🇮🇩 Indonesia", "vi": "🇻🇳 Vietnam",
}

def track(uid, uname, lang, etype, content="", tg_lang_code=None):
    s = load_stats()
    uid = str(uid)
    now = datetime.utcnow().isoformat()
    country = LANG_TO_COUNTRY.get(tg_lang_code, f"🌍 {tg_lang_code or 'unknown'}")
    if uid not in s["users"]:
        s["users"][uid] = {"name": uname, "lang": lang, "first": now, "count": 0, "topics": [], "country": country, "tg_lang": tg_lang_code}
    s["users"][uid]["count"] += 1
    s["users"][uid]["last"] = now
    s["users"][uid]["lang"] = lang
    if tg_lang_code:
        s["users"][uid]["tg_lang"] = tg_lang_code
        s["users"][uid]["country"] = country
    if etype == "topic":
        s["topics"][content] = s["topics"].get(content, 0) + 1
    if etype == "question" and content:
        s["questions"].append({"q": content[:150], "lang": lang, "country": country, "t": now})
        s["questions"] = s["questions"][-500:]
    # Track countries
    if "countries" not in s:
        s["countries"] = {}
    s["countries"][country] = s["countries"].get(country, 0) + 1
    s["total"] = s.get("total", 0) + 1
    save_stats(s)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin /stats command"""
    user = update.effective_user
    admin_id = int(os.getenv("ADMIN_ID", "0"))
    if user.id != admin_id:
        await update.message.reply_text("⛔ Access denied.")
        return
    s = load_stats()
    txt = f"📊 *BlueberryBot Stats*\n"
    txt += f"👥 Users: {len(s['users'])}\n"
    txt += f"📨 Total queries: {s.get('total', 0)}\n\n"
    txt += f"🔝 *Top topics:*\n"
    for t, cnt in sorted(s["topics"].items(), key=lambda x: -x[1])[:10]:
        txt += f"  {t}: {cnt}\n"
    txt += f"\n🌍 *Languages:*\n"
    lang_count = {}
    for u in s["users"].values():
        l = u.get("lang", "en")
        lang_count[l] = lang_count.get(l, 0) + 1
    for l, cnt in sorted(lang_count.items(), key=lambda x: -x[1]):
        txt += f"  {l}: {cnt} users\n"
    txt += f"\n🌍 *Countries (by phone language):*\n"
    countries = s.get("countries", {})
    for country, cnt in sorted(countries.items(), key=lambda x: -x[1])[:15]:
        txt += f"  {country}: {cnt}\n"
    txt += f"\n💬 *Last 5 questions:*\n"
    for q in s["questions"][-5:]:
        txt += f"  [{q.get('country','?')}] {q['q'][:60]}\n"
    await update.message.reply_text(txt[:4000], parse_mode="Markdown")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user_msg = update.message.text
    user = update.effective_user
    track(user.id, user.username or "anon", lang, "question", user_msg, tg_lang_code=user.language_code)

    thinking = {"en": "🫐 Analyzing...", "pl": "🫐 Analizuję...", "de": "🫐 Analysiere...",
                "es": "🫐 Analizando...", "ru": "🫐 Анализирую..."}
    msg = await update.message.reply_text(thinking.get(lang, "🫐 Thinking..."))
    try:
        response = await ask_claude(user_msg, lang, use_search=True)
        if len(response) > 4000:
            response = response[:3990] + "\n\n_(truncated)_"
        await msg.edit_text(response, parse_mode="Markdown")
        await update.message.reply_text("─" * 20, reply_markup=main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("⚠️ Error. Please try again.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages — plant disease detection"""
    lang = get_lang(context)
    user = update.effective_user

    thinking_texts = {
        "en": "🔬 Analyzing photo — identifying variety & checking plant health...",
        "pl": "🔬 Analizuję zdjęcie — rozpoznaję odmianę i stan zdrowia rośliny...",
        "de": "🔬 Foto wird analysiert — Sorte und Pflanzengesundheit werden geprüft...",
        "es": "🔬 Analizando foto — identificando variedad y salud de la planta...",
        "ru": "🔬 Анализирую фото — определяю сорт и состояние здоровья растения...",
    }
    msg = await update.message.reply_text(thinking_texts.get(lang, "🔬 Analyzing..."))

    try:
        # Get highest resolution photo
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        
        # Download photo bytes
        import io
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Analyze with Claude Vision
        result = await analyze_plant_photo(bytes(photo_bytes), lang)
        
        if len(result) > 4000:
            result = result[:3990] + "\n\n_(truncated)_"
        
        await msg.edit_text(result, parse_mode="Markdown")
        
        # Track analytics
        track(user.id, user.username or "anon", lang, "topic", "photo_diagnosis", tg_lang_code=user.language_code)
        
        # Show menu after diagnosis
        followup = {
            "en": "📸 Send another photo or choose a topic:",
            "pl": "📸 Wyślij kolejne zdjęcie lub wybierz temat:",
            "de": "📸 Weiteres Foto senden oder Thema wählen:",
            "es": "📸 Envía otra foto o elige un tema:",
            "ru": "📸 Отправьте ещё фото или выберите тему:",
        }
        await update.message.reply_text(
            followup.get(lang, followup["en"]),
            reply_markup=main_menu_keyboard(lang)
        )

    except Exception as e:
        logger.error(f"Photo analysis error: {e}")
        error_texts = {
            "en": "⚠️ Could not analyze photo. Please send a clear, well-lit photo of the affected plant part.",
            "pl": "⚠️ Nie udało się przeanalizować zdjęcia. Wyślij wyraźne zdjęcie dobrze oświetlonej chorej części rośliny.",
            "de": "⚠️ Foto konnte nicht analysiert werden. Bitte senden Sie ein klares, gut beleuchtetes Foto.",
            "es": "⚠️ No se pudo analizar la foto. Envía una foto clara y bien iluminada.",
            "ru": "⚠️ Не удалось проанализировать фото. Отправьте чёткое, хорошо освещённое фото.",
        }
        await msg.edit_text(error_texts.get(lang, error_texts["en"]))

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
# This is just a marker — actual update is in the knowledge base below
