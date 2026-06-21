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
    "en": "🫐 *BlueberryBot v2.0* — Global Highbush Blueberry Market Intelligence\n\n📊 Data: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Tip:* Type your country name to get variety recommendations for your climate!\n\nChoose a topic or ask me anything!",
    "pl": "🫐 *BlueberryBot v2.0* — Globalny Wywiad Rynku Borówki Amerykańskiej\n\n📊 Dane: IBO · FreshPlaza · USDA · Proarándanos · 2025/26\n\n💡 *Wskazówka:* Napisz nazwę swojego kraju, aby dostać rekomendacje odmian dla Twojego klimatu!\n\nWybierz temat lub zadaj pytanie!",
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
        "prices":    "💰 Prices 2024/25",
        "varieties": "🌱 New Varieties",
        "classics":  "📚 Classic Varieties",
        "nursery":   "🏭 Nursery & Plants",
        "search":    "🔍 Live Search",
        "news":      "📰 Breaking News",
        "lang":      "🌐 Language",
    },
    "pl": {
        "market":    "📊 Rynek globalny",
        "production":"🌍 Produkcja wg kraju",
        "export":    "🚢 Liderzy eksportu",
        "destinations": "🎯 Kluczowe rynki",
        "prices":    "💰 Ceny 2024/25",
        "varieties": "🌱 Nowe odmiany",
        "classics":  "📚 Klasyczne odmiany",
        "nursery":   "🏭 Szkółki i sadzonki",
        "search":    "🔍 Wyszukiwanie live",
        "news":      "📰 Aktualności",
        "lang":      "🌐 Język",
    },
    "de": {
        "market":    "📊 Globaler Markt",
        "production":"🌍 Produktion nach Land",
        "export":    "🚢 Export-Führer",
        "destinations": "🎯 Schlüsselmärkte",
        "prices":    "💰 Preise 2024/25",
        "varieties": "🌱 Neue Sorten",
        "classics":  "📚 Klassische Sorten",
        "nursery":   "🏭 Baumschulen & Pflanzen",
        "search":    "🔍 Live-Suche",
        "news":      "📰 Aktuelle News",
        "lang":      "🌐 Sprache",
    },
    "es": {
        "market":    "📊 Mercado global",
        "production":"🌍 Producción por país",
        "export":    "🚢 Líderes exportación",
        "destinations": "🎯 Mercados clave",
        "prices":    "💰 Precios 2024/25",
        "varieties": "🌱 Nuevas variedades",
        "classics":  "📚 Variedades clásicas",
        "nursery":   "🏭 Viveros y plantas",
        "search":    "🔍 Búsqueda en vivo",
        "news":      "📰 Noticias",
        "lang":      "🌐 Idioma",
    },
    "ru": {
        "market":    "📊 Мировой рынок",
        "production":"🌍 Производство по странам",
        "export":    "🚢 Лидеры экспорта",
        "destinations": "🎯 Ключевые рынки",
        "prices":    "💰 Цены 2024/25",
        "varieties": "🌱 Новые сорта",
        "classics":  "📚 Классические сорта",
        "nursery":   "🏭 Питомники и саженцы",
        "search":    "🔍 Поиск в реальном времени",
        "news":      "📰 Новости",
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
        "en": "Blueberry prices 2025/26: Peru FOB $6.20/kg (-3%). Retail: USA $8-16/kg, Germany €12-24/kg, Poland 50-100 PLN/kg, China 80-200 CNY/kg, Russia 400-900 RUB/250g. Premium (Sekoya/Demba) +20-40%. Frozen €0.90-1.50/kg. Price outlook.",
        "pl": "Ceny borówek 2025/26: Peru FOB $6,20/kg (-3%). Detal: USA $8-16/kg, Niemcy €12-24/kg, Polska 50-100 PLN/kg, Chiny 80-200 CNY/kg, Rosja 400-900 RUB/250g. Premium (Sekoya/Demba) +20-40%. Mrożone €0,90-1,50/kg.",
        "de": "Preise 2025/26: Peru FOB $6,20/kg (-3%). Einzelhandel: USA, DE, PL, CN, RU. Premium +20-40%. Tiefkühl €0,90-1,50/kg.",
        "es": "Precios 2025/26: Perú FOB $6,20/kg (-3%). Retail: USA, DE, PL, CN, RU. Premium +20-40%. Congelado €0,90-1,50/kg.",
        "ru": "Цены 2025/26: Перу FOB $6,20/кг (-3%). Розница: США, Германия, Польша, Китай, Россия. Премиум +20-40%. Замороженные €0,90-1,50/кг.",
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
    await update.message.reply_text(WELCOME[lang], parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))

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

    track(user.id, user.username or "anon", lang, "question", f"/ask {question}")

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
        track(user.id, user.username or "anon", lang, "topic", topic)
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

def track(uid, uname, lang, etype, content=""):
    s = load_stats()
    uid = str(uid)
    now = datetime.utcnow().isoformat()
    if uid not in s["users"]:
        s["users"][uid] = {"name": uname, "lang": lang, "first": now, "count": 0, "topics": []}
    s["users"][uid]["count"] += 1
    s["users"][uid]["last"] = now
    s["users"][uid]["lang"] = lang
    if etype == "topic":
        s["topics"][content] = s["topics"].get(content, 0) + 1
    if etype == "question" and content:
        s["questions"].append({"q": content[:150], "lang": lang, "t": now})
        s["questions"] = s["questions"][-500:]
    s["total"] = s.get("total", 0) + 1
    save_stats(s)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user_msg = update.message.text
    user = update.effective_user
    track(user.id, user.username or "anon", lang, "question", user_msg)

    # Admin stats command
    if user_msg.strip() == "/stats" and user.id in [int(os.getenv("ADMIN_ID", "0"))]:
        s = load_stats()
        txt = f"📊 BlueberryBot Stats\n👥 Users: {len(s['users'])}\n📨 Total queries: {s.get('total',0)}\n\n🔝 Top topics:\n"
        for t, c in sorted(s["topics"].items(), key=lambda x: -x[1])[:10]:
            txt += f"  {t}: {c}\n"
        txt += f"\n💬 Last questions:\n"
        for q in s["questions"][-5:]:
            txt += f"  [{q['lang']}] {q['q']}\n"
        await update.message.reply_text(txt[:4000])
        return

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

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("🫐 BlueberryBot v2.0 starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
# This is just a marker — actual update is in the knowledge base below
