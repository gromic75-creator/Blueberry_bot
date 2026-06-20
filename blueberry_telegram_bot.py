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

RESPONSE RULES:
1. ALWAYS respond ONLY in {lang_name} language.
2. ALWAYS clarify: we discuss HIGHBUSH BLUEBERRY (Vaccinium corymbosum) = borówka amerykańska = arándano = Kulturheidelbeere. NOT wild bilberry.
3. ALWAYS distinguish PRODUCTION (who grows most) vs EXPORT (who sells most globally). China is #1 producer but #1 EXPORTER is Peru.
4. Use data from the knowledge base above. For anything not covered, use web search.
5. Use emojis 🫐📊🌍💰🚢🌱 appropriately.
6. Format with clear **bold headers** and tables where helpful.
7. Cite data sources: (IBO 2024), (FreshPlaza 2025), (USDA 2024), (Proarándanos 2025/26).
8. Be precise with numbers — always cite the season/year.
9. When discussing varieties: mention breeder, climate suitability, market preference.
10. Be professional — this bot serves industry professionals.
11. COUNTRY ADVISOR: If user mentions a country name or asks "what varieties for X country/climate", provide: climate zone (chill hours), best new varieties (Sekoya/Blue World if applicable), best classic varieties, recommended regions, profitability assessment, and which varieties to AVOID. Be specific and practical.
12. VARIETIES: Always separate NEW (Sekoya, Blue World/Demba, BerryWorld Orb, PeachyBlue = post-2020) from CLASSIC (Bluecrop, Duke, Biloxi, Ventura etc. = pre-2020).
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
        "en": "Give a professional overview of the global highbush blueberry market 2024/2025: total production volume (IBO data), market value, growth trends, key producing regions, and outlook to 2030. Distinguish clearly between production and export volumes.",
        "pl": "Podaj profesjonalny przegląd globalnego rynku borówki amerykańskiej (highbush) 2024/2025: całkowita produkcja (dane IBO), wartość rynku, trendy wzrostu, kluczowe regiony produkcji i perspektywy do 2030. Wyraźnie rozróżnij produkcję od eksportu.",
        "de": "Professioneller Überblick über den globalen Kulturheidelbeer-Markt 2024/2025: Gesamtproduktion (IBO-Daten), Marktwert, Wachstumstrends, wichtigste Produktionsregionen und Ausblick bis 2030. Produktion klar von Export unterscheiden.",
        "es": "Visión profesional del mercado global de arándanos highbush 2024/2025: producción total (datos IBO), valor de mercado, tendencias de crecimiento, regiones clave y perspectivas hasta 2030. Distinguir claramente producción de exportación.",
        "ru": "Профессиональный обзор мирового рынка высокорослой голубики 2024/2025: общий объём производства (данные IBO), стоимость рынка, тенденции роста, ключевые регионы производства и прогноз до 2030 года. Чётко разграничить производство и экспорт.",
    },
    "production": {
        "en": "Detailed production data for ALL major highbush blueberry producing countries 2024/2025. IMPORTANT: Distinguish China (#1 by volume, domestic only) vs export leaders (Peru, Chile, Spain, Morocco). Include: volumes in MT, key regions, varieties, season windows, and whether production is domestic or export-oriented. Source: USDA, IBO, Proarándanos.",
        "pl": "Szczegółowe dane produkcji borówki amerykańskiej dla WSZYSTKICH głównych krajów 2024/2025. WAŻNE: Rozróżnij Chiny (nr 1 wolumenem, tylko rynek wewnętrzny) od liderów eksportu (Peru, Chile, Hiszpania, Maroko). Podaj: wolumeny w tonach, kluczowe regiony, odmiany, okna sezonowe, orientacja rynkowa. Źródła: USDA, IBO, Proarándanos.",
        "de": "Detaillierte Produktionsdaten für ALLE wichtigen Highbush-Heidelbeer-Produzenten 2024/2025. WICHTIG: China (#1 Volumen, nur Inland) vs. Exportführer (Peru, Chile, Spanien, Marokko) unterscheiden. Mengen in MT, Regionen, Sorten, Saisonfenster.",
        "es": "Datos detallados de producción de arándanos highbush para TODOS los países principales 2024/2025. IMPORTANTE: Distinguir China (#1 en volumen, consumo doméstico) de líderes exportadores (Perú, Chile, España, Marruecos). Volúmenes en TM, regiones, variedades, ventanas de temporada.",
        "ru": "Подробные данные производства высокорослой голубики по ВСЕМ основным странам 2024/2025. ВАЖНО: Отличить Китай (#1 по объёму, внутренний рынок) от лидеров экспорта (Перу, Чили, Испания, Марокко). Объёмы в тоннах, регионы, сорта, сезонные окна.",
    },
    "export": {
        "en": "Complete export analysis 2024/2025: Global exports hit 1 million MT ($6.73B) for first time. Show: top 10 exporters with MT and $ values, Peru's dominance (31% share, $2.56B in 2025), Morocco's dramatic rise (from 7th to 4th), Chile's recovery, Spain's EU role. Include season windows for each exporter.",
        "pl": "Pełna analiza eksportu 2024/2025: Globalny eksport osiągnął po raz pierwszy 1 milion MT ($6,73 mld). Pokaż: top 10 eksporterów z wolumenami (MT) i wartościami ($), dominację Peru (31% udziału, $2,56 mld w 2025), dramatyczny wzrost Maroka (z 7 na 4 miejsce), odbicie Chile, rolę Hiszpanii w UE. Uwzględnij okna sezonowe.",
        "de": "Vollständige Exportanalyse 2024/2025: Globale Exporte erreichten erstmals 1 Million MT ($6,73 Mrd). Top 10 Exporteure mit MT und $ Werten, Perus Dominanz (31% Anteil), Marokkos dramatischer Aufstieg (7. auf 4. Platz), Chiles Erholung, Spaniens EU-Rolle.",
        "es": "Análisis completo de exportaciones 2024/2025: Las exportaciones globales alcanzaron por primera vez 1 millón TM ($6.73B). Top 10 exportadores con TM y valores $, dominio de Perú (31%, $2.56B en 2025), ascenso espectacular de Marruecos (del 7° al 4°), recuperación de Chile, papel de España en EU.",
        "ru": "Полный анализ экспорта 2024/2025: Мировой экспорт впервые достиг 1 млн тонн ($6,73 млрд). Топ-10 экспортёров с объёмами и стоимостью, доминирование Перу (31%, $2,56 млрд в 2025), стремительный взлёт Марокко (с 7-го на 4-е место), восстановление Чили, роль Испании в ЕС.",
    },
    "destinations": {
        "en": "Detailed analysis of key import markets 2024/2025: USA (largest importer, ~200,000 MT), China (fastest growing, +153% from Peru in 2025, Chancay Port impact), Europe (seasonal supply chain: Morocco→Spain→Poland→Southern Hemisphere), Russia (post-2022 situation, alternative suppliers). Include prices and trends per market.",
        "pl": "Szczegółowa analiza kluczowych rynków importowych 2024/2025: USA (największy importer, ~200,000 MT), Chiny (najszybciej rosnący, +153% z Peru w 2025, wpływ portu Chancay), Europa (sezonowy łańcuch dostaw: Maroko→Hiszpania→Polska→Półkula Południowa), Rosja (sytuacja po 2022, alternatywni dostawcy). Uwzględnij ceny i trendy.",
        "de": "Detaillierte Analyse der wichtigsten Importmärkte 2024/2025: USA (größter Importeur), China (am schnellsten wachsend, +153% aus Peru 2025, Chancay-Hafen), Europa (saisonale Lieferkette), Russland (Post-2022-Situation).",
        "es": "Análisis detallado de mercados de importación clave 2024/2025: USA (mayor importador), China (crecimiento más rápido, +153% desde Perú en 2025, Puerto Chancay), Europa (cadena de suministro estacional), Rusia (situación post-2022).",
        "ru": "Подробный анализ ключевых рынков импорта 2024/2025: США (крупнейший импортёр), Китай (самый быстрорастущий, +153% из Перу в 2025, порт Чанкай), Европа (сезонная цепочка поставок), Россия (ситуация после 2022 года).",
    },
    "prices": {
        "en": "Blueberry price analysis 2024/2025: Peru FOB average $6.20/kg (-3% vs 2024), seasonal price variations (glut in Sept-Oct), premium varieties (Sekoya, Demba) vs commodity pricing, retail prices by country (USA $8-16/kg, Germany €12-24/kg, Poland 50-100 PLN/kg, China 80-200 CNY/kg, Russia 400-900 RUB/250g), frozen bulk prices, price outlook and margin pressure.",
        "pl": "Analiza cen borówek 2024/2025: Peru FOB średnio $6,20/kg (-3% vs 2024), sezonowe wahania (glut wrzesień-październik), premium (Sekoya, Demba) vs commodity, ceny detaliczne: USA $8-16/kg, Niemcy €12-24/kg, Polska 50-100 PLN/kg, Chiny 80-200 CNY/kg, Rosja 400-900 RUB/250g, ceny mrożonych, perspektywy cen i presja na marże.",
        "de": "Preisanalyse 2024/2025: Peru FOB $6,20/kg (-3%), saisonale Schwankungen, Premium (Sekoya, Demba) vs. Commodity, Einzelhandelspreise: USA, Deutschland, Polen, China, Russland, Tiefkühlpreise, Preisausblick.",
        "es": "Análisis de precios 2024/2025: Perú FOB $6.20/kg (-3%), variaciones estacionales, premium (Sekoya, Demba) vs commodity, precios minoristas: USA, Alemania, Polonia, China, Rusia, precios congelados, perspectivas de precios y presión en márgenes.",
        "ru": "Анализ цен 2024/2025: Перу FOB $6,20/кг (-3%), сезонные колебания, премиум (Sekoya, Demba) vs стандарт, розничные цены: США, Германия, Польша, Китай, Россия, цены на замороженные, прогноз цен и давление на маржу.",
    },
    "varieties": {
        "en": "Complete guide to blueberry varieties 2024/2025: Cover ALL major categories. SEKOYA platform (Pop, Beauty, Crunch, Grande, Nova, ArabellaBlue, Apex FCM14-057 - latest 2026 launch). Blue World/Demba range (Demba, Dana, Selma, Aila - Superior Taste Award winners). Peru's top varieties by market (Ventura dominant in Europe 50%, Sekoya Pop in China 24%, Mágica in China 19%). Northern highbush (Bluecrop, Duke, Draper, Aurora). New mechanical harvest FC11-164. Include: breeder, climate, markets, season, advantages.",
        "pl": "Kompletny przewodnik po odmianach borówek 2024/2025: WSZYSTKIE główne kategorie. Platforma SEKOYA (Pop, Beauty, Crunch, Grande, Nova, ArabellaBlue, Apex FCM14-057 - premiera 2026). Seria Blue World/Demba (Demba, Dana, Selma, Aila - nagrody smaku). Topowe odmiany Peru wg rynku (Ventura dominuje Europa 50%, Sekoya Pop Chiny 24%, Mágica Chiny 19%). Północne wysokopienne. Nowe FC11-164 dla mechanicznego zbioru. Hodowca, klimat, rynki, sezon, zalety.",
        "de": "Kompletter Sortenleitfaden 2024/2025: ALLE wichtigen Kategorien. SEKOYA-Plattform, Blue World/Demba (Superior Taste Award), Perus Top-Sorten nach Märkten, Nördliche Highbush, neue FC11-164. Züchter, Klima, Märkte, Saison, Vorteile.",
        "es": "Guía completa de variedades 2024/2025: TODAS las categorías. Plataforma SEKOYA, Blue World/Demba (Superior Taste Award), top variedades Perú por mercado (Ventura Europa 50%, Sekoya Pop China 24%), Northern Highbush, nueva FC11-164 para cosecha mecánica.",
        "ru": "Полное руководство по сортам 2024/2025: ВСЕ основные категории. Платформа SEKOYA, Blue World/Demba (Superior Taste Award), топ-сорта Перу по рынкам (Ventura Европа 50%, Sekoya Pop Китай 24%), Северные высокорослые, новая FC11-164 для механической уборки.",
    },
    "varieties": {
        "en": "NEW blueberry varieties 2020-2026. TWO MAIN PLATFORMS: 1) SEKOYA® (Fall Creek): B2B, 15 members, 25 countries, 87,000 MT. Low-chill: Sekoya Pop (China favorite 24%), Sekoya Beauty, Sekoya Crunch, Sekoya Grande. High-chill: Nova FC15-173, ArabellaBlue FC14-062, LoretoBlue, Apex FCM14-057 (2026 launch, EMEA Jan-May). FC11-164 mechanical harvest trials. 2) BLUE WORLD / Demba (Onubafruit/FV.BV Netherlands): Demba + Dana = Superior Taste Award winners. Full range: Demba, Dana, Aila, Lena, Selma, Selena. EU protection 2056. 25-30 t/ha, Spain season Nov-June. Also: BerryWorld Orb (2025), PeachyBlue (retail hit USA 2025, +6% category sales at Sprouts). Mention which new varieties suit which climate.",
        "pl": "NOWE odmiany borówki 2020-2026. DWE GŁÓWNE PLATFORMY: 1) SEKOYA® (Fall Creek): B2B, 15 firm, 25 krajów, 87,000 MT. Low-chill: Sekoya Pop (Chiny 24%), Beauty, Crunch, Grande. High-chill: Nova, ArabellaBlue, LoretoBlue, Apex (2026). FC11-164 mechaniczny zbiór. 2) BLUE WORLD/Demba (Onubafruit/FV.BV): Demba+Dana = nagroda smaku. Pełna seria: Demba, Dana, Aila, Lena, Selma, Selena. Ochrona EU 2056. 25-30 t/ha. Też: BerryWorld Orb, PeachyBlue (hit USA 2025).",
        "de": "NEUE Sorten 2020-2026: SEKOYA® (Pop, Beauty, Crunch, Grande, Nova, ArabellaBlue, Apex) + Blue World/Demba (Superior Taste Award, EU-Schutz 2056) + BerryWorld Orb + PeachyBlue. Klimaeignung für jede Sorte.",
        "es": "NUEVAS variedades 2020-2026: SEKOYA® (Pop, Beauty, Crunch, Grande, Nova, ArabellaBlue, Apex) + Blue World/Demba (Superior Taste Award, protección EU 2056) + BerryWorld Orb + PeachyBlue. Clima adecuado para cada variedad.",
        "ru": "НОВЫЕ сорта 2020-2026: SEKOYA® (Pop, Beauty, Crunch, Grande, Nova, ArabellaBlue, Apex) + Blue World/Demba (Superior Taste Award, защита ЕС 2056) + BerryWorld Orb + PeachyBlue. Подходящий климат для каждого сорта.",
    },
    "classics": {
        "en": "CLASSIC blueberry varieties (pre-2020, still widely grown). Northern Highbush (high chill 800-1200h, cold climates: Poland, Canada, NE USA, N.Chile): Bluecrop (most planted worldwide, reliable), Duke (early, cold tolerant, very popular Poland), Draper (premium flavor, shelf life), Aurora (very late, large berry), Liberty (late, excellent flavor), Cargo (high yield), Elliott (late processing), Patriot (cold hardy), Toro, Jersey, Chandler (giant berry). Southern Highbush (low chill 200-500h, warm: Peru, S.Spain, Morocco, S.USA, Mexico): Biloxi (was dominant Peru, now declining), Ventura (Peru #1 now, 26% share, EU preferred), O'Neal, Misty, Sharpblue, Emerald, Jewel, Star, Springhigh, Farthing. Half-High (extreme cold -35°C: Scandinavia, Russia, Canada prairies): Northblue, Polaris, Chippewa, St. Cloud. Also mention: Rabbiteye varieties for SE USA/warm dry climates.",
        "pl": "KLASYCZNE odmiany borówki (przed 2020, nadal szeroko uprawiane). Północne wysokopienne (high chill, zimne klimaty: Polska, Kanada, NE USA): Bluecrop, Duke, Draper, Aurora, Liberty, Cargo, Elliott, Patriot, Toro, Jersey, Chandler. Południowe wysokopienne (low chill, ciepłe: Peru, Hiszpania, Maroko): Biloxi (dominowało Peru, teraz wypierane), Ventura (teraz nr 1 w Peru 26%), O'Neal, Misty, Emerald, Jewel, Star. Półwysokopienne (mróz do -35°C): Northblue, Polaris, Chippewa.",
        "de": "KLASSISCHE Sorten: Nördliche Highbush (Bluecrop, Duke, Draper, Aurora, Liberty, Cargo) + Südliche Highbush (Biloxi, Ventura, O'Neal, Misty, Emerald) + Half-High (Northblue, Polaris). Klimaanforderungen für jede Gruppe.",
        "es": "VARIEDADES clásicas: Northern Highbush (Bluecrop, Duke, Draper, Aurora, Liberty) + Southern Highbush (Biloxi, Ventura, O'Neal, Misty, Emerald) + Half-High (Northblue, Polaris). Requisitos climáticos.",
        "ru": "КЛАССИЧЕСКИЕ сорта: Северные высокорослые (Bluecrop, Duke, Draper, Aurora, Liberty) + Южные высокорослые (Biloxi, Ventura, O'Neal, Misty, Emerald) + Полувысокорослые (Northblue, Polaris). Климатические требования.",
    },
    "nursery": {
        "en": """Top 5 global blueberry nursery & genetics companies (verified data):

1. FALL CREEK® (USA, founded 1978, Oregon HQ) — WORLD LEADER in blueberry genetics:
   40+ million blueberry plants/year | 100+ varieties | 59 countries | 1,000+ employees | 10 facilities
   Locations: USA (Oregon HQ), Peru (14M plants/yr, 5 nurseries in Quilmaná/Cañete), Spain/Seville (14M plants/yr, EMEA hub for 52 countries, 250+ staff), Netherlands, South Africa, Mexico, Chile
   Total: 150+ hectares of nurseries globally
   Platforms: SEKOYA® (premium B2B), Fall Creek Collection (open market), Free Marketing varieties
   
2. PLANASA (Spain, founded 1973, Valtierra/Navarra) — WORLD LEADER in berry plant production overall:
   ~1,000 million plants/year TOTAL (all crops incl. strawberry, raspberry, asparagus, garlic)
   Blueberry focus: members-only licensing model | 27+ countries | 7,000 employees | Revenue ~€220M (2023/24)
   1,500+ hectares of nurseries: Spain, Poland, Morocco, Romania, China, Peru, USA, Mexico
   Blueberry varieties: Blue Manila®, Blue Malibu®, Blue Madeira®, Blue Maldiva®, Blue Marina®, Blue Masirah®
   Climate focus: zero/very-low chill (tropical) varieties — best performance in Peru, Mexico, Morocco, Yunnan (China), S.Africa, Zimbabwe
   2023: acquired 100% China subsidiary | 2024: acquired Hansabred (Germany)
   
3. ONUBAFRUIT / FV.BV (Netherlands + Spain) — BLUE WORLD varieties:
   Producer-breeder cooperative based in Huelva, Spain
   Blue World varieties: Demba, Dana, Aila, Lena, Selma, Selena (EU protection until 2056)
   Demba + Dana = Superior Taste Award (International Taste Institute)
   Exclusive licensee: Onubafruit for Spain, Portugal, Morocco
   Production: ~20,000 MT blueberries, 50% from Blue World varieties, growing 10-15%/yr
   
4. OREGON BLUEBERRY (USA, Oregon) — Major North American wholesale nursery:
   One of largest wholesale blueberry nurseries in North America
   40+ years experience | Commercial focus USA/Canada
   Offers premium genetics for North American growers
   
5. LORSENA (Spain) — European nursery specialist:
   Important supplier for European growers, esp. Spain and Portugal
   Works with licensed varieties from multiple breeders
   
OTHER NOTABLE NURSERIES: BerryWorld Varieties (UK, owns Orb variety), Nourse Farms (USA, small fruit specialist), various national nurseries in Poland, Chile, Canada, Australia.
   
PLANT COSTS (approximate): Tissue culture plug/liner: $0.50–2.00 | Finished plant (1-2L): $2–5 | Premium licensed variety premium: +20-50%
Ask me your country — I'll recommend the best nursery source and varieties for your climate!""",
        "pl": """Top 5 globalnych szkółek i firm genetycznych borówki (zweryfikowane dane):

1. FALL CREEK® (USA, od 1978, Oregon) — ŚWIATOWY LIDER genetyki borówkowej:
   40+ mln sadzonek/rok | 100+ odmian | 59 krajów | 1000+ pracowników | 10 zakładów
   Lokalizacje: USA, Peru (14 mln szt/rok, 5 szkółek), Hiszpania/Sewilla (14 mln szt/rok, centrum EMEA, 52 kraje), Holandia, RPA, Meksyk, Chile
   Łącznie 150+ ha szkółek | Platformy: SEKOYA®, Fall Creek Collection

2. PLANASA (Hiszpania, od 1973, Valtierra/Navarra) — NAJWIĘKSZY producent roślin jagodowych:
   ~1 miliard sadzonek/rok ŁĄCZNIE (wszystkie rośliny) | 27+ krajów | 7000 pracowników | ~220 mln EUR obrót
   1500+ ha szkółek: Hiszpania, Polska, Maroko, Rumunia, Chiny, Peru, USA, Meksyk
   Odmiany borówki: Blue Manila®, Blue Malibu®, Blue Madeira®, Blue Maldiva®, Blue Marina®, Blue Masirah®
   Specjalizacja: zero/very-low chill — Peru, Meksyk, Maroko, Yunnan (Chiny), RPA, Zimbabwe
   Model: tylko dla członków (licencje)

3. ONUBAFRUIT / FV.BV (Holandia + Hiszpania) — seria BLUE WORLD:
   Odmiany: Demba, Dana, Aila, Lena, Selma, Selena (ochrona EU do 2056)
   Nagroda: Superior Taste Award dla Demba i Dana
   Licencja: Onubafruit (Huelva) dla Hiszpanii/Portugali/Maroka
   Produkcja: ~20,000 MT, 50% z Blue World

4. OREGON BLUEBERRY (USA, Oregon) — duża hurtowa szkółka północnoamerykańska

5. LORSENA (Hiszpania) — europejski specjalista szkółkarski

Koszty sadzonek: plug/liner $0.50-2.00 | sadzonka gotowa $2-5 | dopłata za odmiany licencjonowane +20-50%""",
        "de": """Top 5 globale Heidelbeer-Baumschulen (verifizierte Daten):
1. FALL CREEK® (USA/Oregon, 1978): 40+ Mio. Pflanzen/Jahr, 100+ Sorten, 59 Länder, 10 Standorte (Peru 14M, Spanien 14M, NL, SA). SEKOYA® Plattform.
2. PLANASA (Spanien/Navarra, 1973): ~1 Mrd. Pflanzen/Jahr gesamt, 7.000 Mitarbeiter, 1.500+ ha, 27 Länder. Blaubeeren: Blue Manila, Malibu, Madeira, Maldiva, Marina, Masirah. Fokus: zero-chill Sorten.
3. ONUBAFRUIT/FV.BV (Niederlande+Spanien): Blue World (Demba, Dana - Taste Award, EU-Schutz 2056).
4. OREGON BLUEBERRY (USA): Größte Großhandels-Baumschule Nordamerikas.
5. LORSENA (Spanien): Europäischer Spezialist.
Pflanzenkosten: Stecklinge $0,50-2,00, fertige Pflanzen $2-5.""",
        "es": """Top 5 viveros globales de arándano (datos verificados):
1. FALL CREEK® (EE.UU./Oregon, 1978): 40+ millones plantas/año, 100+ variedades, 59 países, 10 instalaciones. Plataforma SEKOYA®.
2. PLANASA (España/Navarra, 1973): ~1.000 millones plantas/año total, 7.000 empleados, 1.500+ ha en 27 países. Variedades: Blue Manila, Malibu, Madeira, Maldiva, Marina, Masirah. Especialidad: cero horas frío.
3. ONUBAFRUIT/FV.BV (Países Bajos+España): Blue World (Demba, Dana - Premio Sabor, protección EU 2056).
4. OREGON BLUEBERRY (EE.UU.): Mayor vivero mayorista de Norteamérica.
5. LORSENA (España): Especialista europeo.
Costos: esquejes $0,50-2,00, plantas terminadas $2-5.""",
        "ru": """Топ-5 мировых питомников голубики (проверенные данные):
1. FALL CREEK® (США/Орегон, 1978): 40+ млн саженцев/год, 100+ сортов, 59 стран, 10 объектов. Платформа SEKOYA®.
2. PLANASA (Испания/Наварра, 1973): ~1 млрд саженцев/год всего, 7000 сотрудников, 1500+ га в 27 странах. Голубика: Blue Manila, Malibu, Madeira, Maldiva, Marina, Masirah. Специализация: нулевые часы холода.
3. ONUBAFRUIT/FV.BV (Нидерланды+Испания): Blue World (Demba, Dana - награда вкуса, защита ЕС до 2056).
4. OREGON BLUEBERRY (США): Крупнейший оптовый питомник Северной Америки.
5. LORSENA (Испания): Европейский специалист.
Стоимость: черенки $0,50-2,00, готовые саженцы $2-5.""",
    },
    "search": {
        "en": "Search the web for the very latest blueberry market news, price reports, and variety releases from 2025-2026. Check FreshPlaza, IBO, Blueberries Consulting for the most recent data. Combine with knowledge base to give the most current professional picture.",
        "pl": "Przeszukaj internet w poszukiwaniu najnowszych wiadomości rynku borówek, raportów cen i nowych odmian z 2025-2026. Sprawdź FreshPlaza, IBO, Blueberries Consulting. Połącz z bazą wiedzy.",
        "de": "Suchen Sie nach den neuesten Heidelbeer-Marktnachrichten 2025-2026 auf FreshPlaza, IBO, Blueberries Consulting. Mit Wissensbasis kombinieren.",
        "es": "Busca las últimas noticias del mercado de arándanos 2025-2026 en FreshPlaza, IBO, Blueberries Consulting. Combinar con base de conocimiento.",
        "ru": "Поиск последних новостей рынка черники 2025-2026 на FreshPlaza, IBO, Blueberries Consulting. Объединить с базой знаний.",
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
        [InlineKeyboardButton(labels["search"],       callback_data="topic_search"),
         InlineKeyboardButton(labels["lang"],         callback_data="choose_lang")],
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
        try:
            response = await ask_claude(prompt, lang, use_search=use_search)
            if len(response) > 4000:
                response = response[:3990] + "\n\n_(truncated)_"
            await query.edit_message_text(response, parse_mode="Markdown", reply_markup=main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("⚠️ Error. Please try again.", reply_markup=main_menu_keyboard(lang))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user_msg = update.message.text
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
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("🫐 BlueberryBot v2.0 starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
# This is just a marker — actual update is in the knowledge base below
