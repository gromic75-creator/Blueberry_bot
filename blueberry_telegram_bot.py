"""
🫐 BlueberryBot - Global Blueberry Market Intelligence Bot
Supports: English, Polish, German, Spanish, Russian
"""

import os
import logging
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ── Config ────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Language config ───────────────────────────────────────────────────────────
LANGUAGES = {
    "en": "🇬🇧 English",
    "pl": "🇵🇱 Polski",
    "de": "🇩🇪 Deutsch",
    "es": "🇪🇸 Español",
    "ru": "🇷🇺 Русский",
}

WELCOME = {
    "en": "🫐 *BlueberryBot* — Global Blueberry Market Intelligence\n\nChoose your language / topic below, or just ask me anything about blueberries!",
    "pl": "🫐 *BlueberryBot* — Globalny Wywiad Rynku Borówek\n\nWybierz język / temat poniżej lub po prostu zadaj mi pytanie o borówki!",
    "de": "🫐 *BlueberryBot* — Globale Heidelbeer-Marktintelligenz\n\nWählen Sie Ihre Sprache / Ihr Thema unten oder stellen Sie mir einfach eine Frage über Heidelbeeren!",
    "es": "🫐 *BlueberryBot* — Inteligencia del Mercado Global de Arándanos\n\n¡Elige tu idioma / tema a continuación o simplemente pregúntame lo que quieras sobre los arándanos!",
    "ru": "🫐 *BlueberryBot* — Глобальная аналитика рынка черники\n\nВыберите язык / тему ниже или просто задайте мне любой вопрос о чернике!",
}

MENU_LABELS = {
    "en": {
        "market":    "📊 Global Market Value",
        "countries": "🌍 Production by Country",
        "export":    "🚢 Export Data",
        "prices":    "💰 Prices & Trends",
        "varieties": "🌱 New Varieties",
        "search":    "🔍 Live Search",
        "lang":      "🌐 Change Language",
    },
    "pl": {
        "market":    "📊 Wartość rynku globalnego",
        "countries": "🌍 Produkcja według kraju",
        "export":    "🚢 Dane eksportowe",
        "prices":    "💰 Ceny i trendy",
        "varieties": "🌱 Nowe odmiany",
        "search":    "🔍 Wyszukiwanie na żywo",
        "lang":      "🌐 Zmień język",
    },
    "de": {
        "market":    "📊 Globaler Marktwert",
        "countries": "🌍 Produktion nach Land",
        "export":    "🚢 Exportdaten",
        "prices":    "💰 Preise & Trends",
        "varieties": "🌱 Neue Sorten",
        "search":    "🔍 Live-Suche",
        "lang":      "🌐 Sprache ändern",
    },
    "es": {
        "market":    "📊 Valor del mercado global",
        "countries": "🌍 Producción por país",
        "export":    "🚢 Datos de exportación",
        "prices":    "💰 Precios y tendencias",
        "varieties": "🌱 Nuevas variedades",
        "search":    "🔍 Búsqueda en vivo",
        "lang":      "🌐 Cambiar idioma",
    },
    "ru": {
        "market":    "📊 Мировой рынок",
        "countries": "🌍 Производство по странам",
        "export":    "🚢 Экспортные данные",
        "prices":    "💰 Цены и тренды",
        "varieties": "🌱 Новые сорта",
        "search":    "🔍 Поиск в реальном времени",
        "lang":      "🌐 Сменить язык",
    },
}

# ── Knowledge base (built-in) ─────────────────────────────────────────────────
BLUEBERRY_KNOWLEDGE = """
You are BlueberryBot, the world's most comprehensive blueberry market intelligence assistant.
You have deep expertise on ALL aspects of global blueberry production, trade, and economics.

=== GLOBAL MARKET ===
- Global blueberry market value: ~$3.5–4.2 billion USD (2023–2024), growing at ~7% CAGR
- Projected to reach ~$6.5 billion by 2030
- Fresh blueberries dominate (~65% of market), frozen/processed ~35%

=== TOP PRODUCING COUNTRIES (annual tonnes) ===
1. USA: ~360,000–400,000 MT — States: Michigan, Oregon, Washington, Georgia, New Jersey
2. Canada: ~170,000 MT — British Columbia, Quebec, Nova Scotia
3. Chile: ~150,000 MT — world's largest exporter by volume
4. Peru: ~120,000–140,000 MT — fastest growing
5. Spain: ~110,000 MT — main EU producer (Huelva)
6. Poland: ~70,000–80,000 MT — largest EU highbush producer
7. Mexico: ~65,000 MT — rapidly expanding
8. South Africa: ~35,000 MT
9. Morocco: ~20,000 MT
10. China: ~550,000 MT (mostly wild/half-high, Guizhou, Jilin provinces — largely domestic)
11. Russia: ~15,000 MT cultivated + large wild harvest
12. Germany: ~12,000 MT
13. Netherlands: ~10,000 MT
14. Portugal: ~25,000 MT
15. Argentina: ~18,000 MT
16. Australia: ~20,000 MT
17. New Zealand: ~8,000 MT
18. Ukraine: ~25,000 MT (before 2022 conflict significantly higher)
19. Serbia: ~8,000 MT
20. Romania: ~5,000 MT

=== EXPORT DATA ===
CHILE:
- Total export: ~120,000–130,000 MT/year, value ~$900M–1.1B USD
- To USA: ~55% of exports (~$500M)
- To Europe (EU+UK): ~30% (~$280M) — Netherlands, UK, Spain main receivers
- To China: ~8% and growing rapidly
- To Russia: ~2% (reduced post-sanctions)

PERU:
- Total export: ~100,000–120,000 MT/year, value ~$800M–1.0B USD
- To USA: ~50% (~$400M)
- To Europe: ~35% (~$280M)
- To China: ~10% and growing fast
- Season: Sept–Dec (counter-season to Northern Hemisphere)

USA:
- Exports ~50,000–60,000 MT, value ~$200M
- Main destinations: Canada, Japan, South Korea, Netherlands

SPAIN:
- Exports ~90,000 MT, value ~$450M
- Main EU supplier during spring season (April–June)
- 80% to EU, 15% to UK, 5% other

POLAND:
- Exports ~50,000 MT, value ~€180M
- Mainly to Germany, Netherlands, UK, Scandinavia

MOROCCO:
- Growing export player, mainly EU in early season (Feb–April)

=== EXPORT TO KEY MARKETS ===
CHINA:
- Imports: ~80,000–100,000 MT/year, value ~$500–700M
- Main suppliers: Chile, Peru, Australia, New Zealand
- Growing middle class driving demand
- Premium fresh blueberry market expanding 25%+/year

USA:
- World's largest importer: ~200,000 MT/year, value ~$800M–1.0B
- Counter-season from Chile, Peru, Mexico (Oct–May)
- Also Canadian imports (June–August)

EUROPE (EU+UK):
- Total imports: ~180,000–220,000 MT/year, value ~$1.0–1.3B
- Netherlands as redistribution hub
- Main suppliers: Morocco (Feb–Apr), Spain (Apr–Jun), Poland (Jul–Sep), Chile/Peru (Nov–Mar)
- Germany largest EU consumer (~35,000 MT/year)

RUSSIA:
- Pre-2022: imported ~30,000 MT, value ~$80M mainly from Serbia, Poland, Belarus
- Post-2022 sanctions: significantly reduced Western imports
- Now sourcing more from Belarus, China, Azerbaijan, Iran
- Domestic production growing (Leningrad region, Krasnodar)

=== PRICES ===
Fresh blueberries (FOB export price):
- Peak season (Jul-Aug Northern Hemisphere): $1.5–2.5/kg
- Off-season (Nov-Mar, Southern Hemisphere): $3.0–6.0/kg
- Organic premium: +40–80%
- China market premium: +20–30% over EU

Retail prices:
- USA: $4–8/pint (~$8–16/kg)
- Germany: €3–6/punnet 250g (~€12–24/kg)
- Poland: 8–18 PLN/250g (~32–72 PLN/kg)
- Russia: 400–800 RUB/250g (~1600–3200 RUB/kg)

Frozen (bulk):
- EU import price: €0.90–1.50/kg
- USA import: $1.0–1.8/kg

=== NEW VARIETIES (2020–2025) ===
HIGHBUSH NORTHERN:
- 'Cargo' — high yield, firm, excellent shelf life
- 'Aurora' — late season, very large berry
- 'Calypso' — patented, disease resistant
- 'Draper' — premium, self-fruitful, excellent flavor
- 'Sweetcrisp' — very sweet, extended season

SOUTHERN HIGHBUSH:
- 'Springhigh' — early season, excellent flavor
- 'Farthing' — large berry, good for warm climates
- 'Meadowlark' — low-chill requirement
- 'Rebel' — low-chill, high yield, suited for Chile/Peru

HALF-HIGH:
- 'Northblue' — cold hardy to -35°C, suited for Scandinavia/Poland
- 'Polaris' — very aromatic, cold tolerant

FOR CHINA MARKET (low-chill):
- 'O'Neal' adaptation — widely planted Guizhou
- 'Misty' — low chill ~150h, very popular SE China
- 'Sharpblue' — nearly evergreen, S. China / Vietnam

FOR POLAND/RUSSIA:
- 'Bluecrop' — still dominant (reliable, proven)
- 'Duke' — early, very cold tolerant
- 'Patriot' — cold hardy, well-drained soils
- 'Toro' — high yield, medium chill requirement

ORGANIC / SPECIALTY:
- 'Pink Lemonade' — pink-berried novelty, growing demand
- 'Jelly Bean' — very small, intensely flavored
"""

# ── System prompt builder ─────────────────────────────────────────────────────
def build_system_prompt(lang: str) -> str:
    lang_name = LANGUAGES.get(lang, "English")
    return f"""
{BLUEBERRY_KNOWLEDGE}

=== RESPONSE RULES ===
1. ALWAYS respond in {lang_name} language ONLY.
2. Use emojis appropriately (🫐📊🌍💰🚢🌱).
3. Format data in clear tables using Markdown when showing statistics.
4. When you have web search results, integrate them with your knowledge base.
5. Be specific with numbers — cite years for data (e.g., 2023/2024).
6. Structure long answers with headers (bold **text**) for readability.
7. Keep answers focused and practical for blueberry industry professionals.
8. If asked about current prices, note these fluctuate and recommend checking live market sources.
9. Always be helpful, precise, and comprehensive.
"""

# ── Anthropic Claude call ─────────────────────────────────────────────────────
async def ask_claude(prompt: str, lang: str, use_search: bool = False) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    tools = []
    if use_search:
        tools = [{"type": "web_search_20250305", "name": "web_search"}]

    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "system": build_system_prompt(lang),
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools

    response = client.messages.create(**kwargs)

    # Collect all text from response
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)

    return "\n".join(parts) if parts else "⚠️ No response generated."

# ── Preset topic prompts ──────────────────────────────────────────────────────
TOPIC_PROMPTS = {
    "market": {
        "en": "Give me a comprehensive overview of the global blueberry market value in USD, market size, growth rate (CAGR), segmentation (fresh vs frozen vs processed), and projections to 2030. Include key market drivers.",
        "pl": "Podaj mi kompleksowy przegląd wartości globalnego rynku borówek w USD, wielkości rynku, tempa wzrostu (CAGR), segmentacji (świeże vs mrożone vs przetworzone) i prognozy do 2030 roku. Uwzględnij kluczowe czynniki rynkowe.",
        "de": "Geben Sie mir einen umfassenden Überblick über den globalen Heidelbeer-Marktwert in USD, Marktgröße, Wachstumsrate (CAGR), Segmentierung (frisch vs. gefroren vs. verarbeitet) und Prognosen bis 2030.",
        "es": "Dame una descripción completa del valor del mercado global de arándanos en USD, tamaño del mercado, tasa de crecimiento (CAGR), segmentación (fresco vs congelado vs procesado) y proyecciones hasta 2030.",
        "ru": "Дайте мне исчерпывающий обзор стоимости мирового рынка черники в долларах США, размера рынка, темпов роста (CAGR), сегментации (свежие / замороженные / переработанные) и прогнозов до 2030 года.",
    },
    "countries": {
        "en": "List all major blueberry producing countries with their annual production in metric tonnes, which regions/states they grow in, and their share of global production. Include both cultivated and wild harvests.",
        "pl": "Wymień wszystkie główne kraje produkujące borówki z roczną produkcją w tonach metrycznych, w których regionach/stanach uprawiają, oraz ich udział w globalnej produkcji. Uwzględnij zarówno uprawiane, jak i dzikie zbiory.",
        "de": "Listen Sie alle wichtigen Heidelbeer-produzierenden Länder mit ihrer Jahresproduktion in Tonnen, in welchen Regionen/Bundesstaaten sie angebaut werden, und ihrem Anteil an der Weltproduktion auf.",
        "es": "Lista todos los principales países productores de arándanos con su producción anual en toneladas métricas, en qué regiones/estados los cultivan y su participación en la producción mundial.",
        "ru": "Перечислите все основные страны-производители черники с указанием годового производства в метрических тоннах, в каких регионах/штатах выращивают, и их долей в мировом производстве.",
    },
    "export": {
        "en": "Give detailed blueberry export data: top exporting countries, volumes in MT, export values in USD, and breakdown of exports to China, USA, Europe, and Russia. Include trade flow trends 2022–2024.",
        "pl": "Podaj szczegółowe dane eksportowe borówek: czołowe kraje eksportujące, wolumeny w tonach, wartości eksportu w USD oraz podział eksportu do Chin, USA, Europy i Rosji. Uwzględnij trendy przepływów handlowych 2022–2024.",
        "de": "Geben Sie detaillierte Heidelbeer-Exportdaten: Top-Exportländer, Mengen in MT, Exportwerte in USD und Aufschlüsselung der Exporte nach China, USA, Europa und Russland.",
        "es": "Dame datos detallados de exportación de arándanos: principales países exportadores, volúmenes en TM, valores de exportación en USD y desglose de exportaciones a China, EE.UU., Europa y Rusia.",
        "ru": "Предоставьте подробные данные по экспорту черники: ведущие страны-экспортёры, объёмы в тоннах, стоимость экспорта в долларах, разбивка по экспорту в Китай, США, Европу и Россию.",
    },
    "prices": {
        "en": "What are current blueberry prices? Show FOB export prices, wholesale prices, retail prices in key markets (USA, Germany, Poland, Russia, China). Include seasonal price variations and organic premium.",
        "pl": "Jakie są aktualne ceny borówek? Pokaż ceny FOB eksportowe, ceny hurtowe, ceny detaliczne na kluczowych rynkach (USA, Niemcy, Polska, Rosja, Chiny). Uwzględnij sezonowe wahania cen i premię za produkty organiczne.",
        "de": "Was sind die aktuellen Heidelbeerpreise? Zeigen Sie FOB-Exportpreise, Großhandelspreise, Einzelhandelspreise auf wichtigen Märkten (USA, Deutschland, Polen, Russland, China).",
        "es": "¿Cuáles son los precios actuales de los arándanos? Muestra precios FOB de exportación, precios mayoristas, precios minoristas en mercados clave (EE.UU., Alemania, Polonia, Rusia, China).",
        "ru": "Каковы текущие цены на чернику? Покажите цены FOB на экспорт, оптовые цены, розничные цены на ключевых рынках (США, Германия, Польша, Россия, Китай).",
    },
    "varieties": {
        "en": "What are the newest blueberry varieties released 2020–2025? Include highbush, southern highbush, half-high varieties. Note which are suited for warm climates (China, Peru), cold climates (Poland, Russia, Scandinavia), and which have best export characteristics.",
        "pl": "Jakie są najnowsze odmiany borówek wprowadzone w latach 2020–2025? Uwzględnij wysokopienne, południowe wysokopienne i półwysokopienne. Zaznacz, które nadają się do ciepłych klimatów (Chiny, Peru), zimnych klimatów (Polska, Rosja, Skandynawia) i które mają najlepsze cechy eksportowe.",
        "de": "Was sind die neuesten Heidelbeersorten, die 2020–2025 eingeführt wurden? Umfassen Sie Highbush, Southern Highbush, Half-High-Sorten. Notieren Sie, welche für warme Klimata (China, Peru), kalte Klimata (Polen, Russland, Skandinavien) geeignet sind.",
        "es": "¿Cuáles son las variedades de arándanos más nuevas lanzadas entre 2020 y 2025? Incluye highbush, southern highbush, half-high. Nota cuáles son adecuadas para climas cálidos (China, Perú) y fríos (Polonia, Rusia, Escandinavia).",
        "ru": "Какие новейшие сорта черники были выпущены в 2020–2025 годах? Включите высокорослые, южные высокорослые, полувысокорослые сорта. Отметьте, какие подходят для тёплого климата (Китай, Перу) и холодного (Польша, Россия, Скандинавия).",
    },
}

SEARCH_PROMPTS = {
    "en": "Search for the latest 2024-2025 blueberry market data, prices, export statistics, and new variety releases. Combine with your knowledge to give the most current overview.",
    "pl": "Wyszukaj najnowsze dane rynku borówek 2024–2025, ceny, statystyki eksportowe i nowe odmiany. Połącz z wiedzą, aby dać najbardziej aktualny przegląd.",
    "de": "Suchen Sie nach den neuesten Heidelbeer-Marktdaten 2024–2025, Preisen, Exportstatistiken und neuen Sortenstarts. Kombinieren Sie mit Ihrem Wissen für den aktuellsten Überblick.",
    "es": "Busca los últimos datos del mercado de arándanos 2024–2025, precios, estadísticas de exportación y nuevas variedades. Combina con tu conocimiento para dar el resumen más actual.",
    "ru": "Найдите последние данные рынка черники 2024–2025, цены, статистику экспорта и новые сорта. Объедините с вашими знаниями для самого актуального обзора.",
}

# ── Telegram handlers ─────────────────────────────────────────────────────────
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")

def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    labels = MENU_LABELS[lang]
    keyboard = [
        [
            InlineKeyboardButton(labels["market"],    callback_data="topic_market"),
            InlineKeyboardButton(labels["countries"], callback_data="topic_countries"),
        ],
        [
            InlineKeyboardButton(labels["export"],    callback_data="topic_export"),
            InlineKeyboardButton(labels["prices"],    callback_data="topic_prices"),
        ],
        [
            InlineKeyboardButton(labels["varieties"], callback_data="topic_varieties"),
            InlineKeyboardButton(labels["search"],    callback_data="topic_search"),
        ],
        [
            InlineKeyboardButton(labels["lang"],      callback_data="choose_lang"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def lang_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
        for code, name in LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(context)
    await update.message.reply_text(
        WELCOME[lang],
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(lang),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_lang(context)
    help_texts = {
        "en": "🫐 *BlueberryBot Help*\n\n• Use the menu buttons for preset topics\n• Type any question in chat for custom answers\n• Change language with 🌐 button\n\nTopics covered: market value, production by country, export data (China/USA/EU/Russia), prices, new varieties.",
        "pl": "🫐 *Pomoc BlueberryBot*\n\n• Używaj przycisków menu dla gotowych tematów\n• Wpisz pytanie w czacie dla niestandardowych odpowiedzi\n• Zmień język przyciskiem 🌐\n\nTematy: wartość rynku, produkcja krajowa, dane eksportowe (Chiny/USA/UE/Rosja), ceny, nowe odmiany.",
        "de": "🫐 *BlueberryBot Hilfe*\n\n• Verwenden Sie die Menü-Schaltflächen für voreingestellte Themen\n• Tippen Sie eine Frage im Chat für benutzerdefinierte Antworten\n• Sprache mit 🌐-Schaltfläche ändern",
        "es": "🫐 *Ayuda de BlueberryBot*\n\n• Usa los botones del menú para temas preestablecidos\n• Escribe cualquier pregunta en el chat para respuestas personalizadas\n• Cambia el idioma con el botón 🌐",
        "ru": "🫐 *Помощь BlueberryBot*\n\n• Используйте кнопки меню для готовых тем\n• Введите любой вопрос в чат для индивидуальных ответов\n• Измените язык кнопкой 🌐",
    }
    await update.message.reply_text(
        help_texts.get(lang, help_texts["en"]),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(lang),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    # Language selection menu
    if data == "choose_lang":
        choose_texts = {
            "en": "🌐 Choose your language:",
            "pl": "🌐 Wybierz język:",
            "de": "🌐 Sprache wählen:",
            "es": "🌐 Elige tu idioma:",
            "ru": "🌐 Выберите язык:",
        }
        await query.edit_message_text(
            choose_texts.get(lang, choose_texts["en"]),
            reply_markup=lang_keyboard(),
        )
        return

    # Language set
    if data.startswith("lang_"):
        new_lang = data.split("_", 1)[1]
        context.user_data["lang"] = new_lang
        await query.edit_message_text(
            WELCOME[new_lang],
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(new_lang),
        )
        return

    # Topic buttons
    if data.startswith("topic_"):
        topic = data.split("_", 1)[1]
        loading_texts = {
            "en": "⏳ Fetching blueberry data...",
            "pl": "⏳ Pobieranie danych o borówkach...",
            "de": "⏳ Heidelbeerdaten werden abgerufen...",
            "es": "⏳ Obteniendo datos de arándanos...",
            "ru": "⏳ Получение данных о чернике...",
        }
        await query.edit_message_text(loading_texts.get(lang, loading_texts["en"]))

        use_search = (topic == "search")
        if topic == "search":
            prompt = SEARCH_PROMPTS.get(lang, SEARCH_PROMPTS["en"])
        else:
            prompt = TOPIC_PROMPTS.get(topic, {}).get(lang, TOPIC_PROMPTS.get(topic, {}).get("en", "Tell me about blueberries."))

        try:
            response = await ask_claude(prompt, lang, use_search=use_search)
            # Telegram message limit: 4096 chars
            if len(response) > 4000:
                response = response[:3990] + "\n\n_(truncated)_"
            await query.edit_message_text(
                response,
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard(lang),
            )
        except Exception as e:
            logger.error(f"Claude error: {e}")
            err_texts = {
                "en": "⚠️ Error fetching data. Please try again.",
                "pl": "⚠️ Błąd pobierania danych. Spróbuj ponownie.",
                "de": "⚠️ Fehler beim Abrufen der Daten. Bitte versuchen Sie es erneut.",
                "es": "⚠️ Error al obtener datos. Por favor, inténtalo de nuevo.",
                "ru": "⚠️ Ошибка при получении данных. Пожалуйста, попробуйте снова.",
            }
            await query.edit_message_text(
                err_texts.get(lang, err_texts["en"]),
                reply_markup=main_menu_keyboard(lang),
            )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle free-text questions from users."""
    lang = get_lang(context)
    user_msg = update.message.text

    thinking_texts = {
        "en": "🫐 Thinking...",
        "pl": "🫐 Myślę...",
        "de": "🫐 Denke nach...",
        "es": "🫐 Pensando...",
        "ru": "🫐 Думаю...",
    }
    thinking_msg = await update.message.reply_text(thinking_texts.get(lang, "🫐 Thinking..."))

    try:
        # Use web search for free-text questions to get freshest data
        response = await ask_claude(user_msg, lang, use_search=True)
        if len(response) > 4000:
            response = response[:3990] + "\n\n_(truncated)_"
        await thinking_msg.edit_text(
            response,
            parse_mode="Markdown",
        )
        # Show menu after answer
        await update.message.reply_text(
            "─" * 20,
            reply_markup=main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await thinking_msg.edit_text("⚠️ Error. Please try again.")

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("🫐 BlueberryBot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
