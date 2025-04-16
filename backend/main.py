# Backend for Arbitrage Scanner MVP
# FastAPI server to fetch prices from Binance, Bybit, KuCoin and calculate arbitrage for BTC/USDT

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Query
from typing import List, Dict

# Функция для генерации URL под любую пару
EXCHANGES_TEMPLATE = [
    {
        "name": "Binance",
        "url": lambda pair: f"https://api.binance.com/api/v3/ticker/price?symbol={pair}",
        "extract": lambda r: float(r["price"]),
        "pair_format": lambda p: p.replace("-", ""),
        "pairs_url": "https://api.binance.com/api/v3/exchangeInfo",
        "pairs_field": lambda r: [s['symbol'] for s in r['symbols']]
    },
    {
        "name": "Bybit",
        "url": lambda pair: f"https://api.bybit.com/v2/public/tickers?symbol={pair}",
        "extract": lambda r: float(r["result"][0]["last_price"]),
        "pair_format": lambda p: p.replace("-", ""),
        "pairs_url": "https://api.bybit.com/v5/market/tickers?category=spot",
        "pairs_field": lambda r: [s['symbol'] for s in r['result']['list']]
    },
    {
        "name": "KuCoin",
        "url": lambda pair: f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={pair}",
        "extract": lambda r: float(r["data"]["price"]),
        "pair_format": lambda p: p.replace("USDT", "-USDT").replace("BTC", "BTC"),
        "pairs_url": "https://api.kucoin.com/api/v1/symbols",
        "pairs_field": lambda r: [s['symbol'] for s in r['data']]
    },
    # Mexc
    {
        "name": "Mexc",
        "url": lambda pair: f"https://api.mexc.com/api/v3/ticker/price?symbol={pair}",
        "extract": lambda r: float(r["price"]),
        "pair_format": lambda p: p.replace("-", ""),
        "pairs_url": "https://api.mexc.com/api/v3/exchangeInfo",
        "pairs_field": lambda r: [s['symbol'] for s in r['symbols']]
    },
    # Gate.io
    {
        "name": "Gate",
        "url": lambda pair: f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}",
        "extract": lambda r: float(r[0]["last"]),
        "pair_format": lambda p: p.replace("USDT", "_USDT").replace("-", "_"),
        "pairs_url": "https://api.gateio.ws/api/v4/spot/currency_pairs",
        "pairs_field": lambda r: [s['id'] for s in r]
    },
    # BitGet
    {
        "name": "BitGet",
        "url": lambda pair: f"https://api.bitget.com/api/spot/v1/market/ticker?symbol={pair}",
        "extract": lambda r: float(r['data'][0]['last']),
        "pair_format": lambda p: p.replace("-", ""),
        "pairs_url": "https://api.bitget.com/api/v2/spot/public/symbols",
        "pairs_field": lambda r: [s['symbol'] for s in r['data']]
    },
    # OKX
    {
        "name": "OKX",
        "url": lambda pair: f"https://www.okx.com/api/v5/market/ticker?instId={pair}",
        "extract": lambda r: float(r['data'][0]['last']),
        "pair_format": lambda p: p.replace("USDT", "-USDT"),
        "pairs_url": "https://www.okx.com/api/v5/public/instruments?instType=SPOT",
        "pairs_field": lambda r: [s['instId'] for s in r['data']]
    },

    # HTX (ex-Huobi)
    {
        "name": "HTX",
        "url": lambda pair: f"https://api.huobi.pro/market/detail/merged?symbol={pair.lower()}",
        "extract": lambda r: float(r['tick']['close']),
        "pair_format": lambda p: p.lower(),
        "pairs_url": "https://api.huobi.pro/v1/common/symbols",
        "pairs_field": lambda r: [s['symbol'] for s in r['data']]
    }
]


# Кэш поддерживаемых пар
SUPPORTED_PAIRS = {}

import asyncio
import random

@app.get("/arbitrage/all")
async def get_arbitrage_all(limit_per_exchange: int = 100):
    print("[ARBITRAGE_ALL] Called with limit_per_exchange:", limit_per_exchange)
    import time
    start_time = time.time()
    """
    Возвращает арбитражные возможности для всех поддерживаемых пар (по USDT) с каждой биржи.
    limit_per_exchange: ограничение количества пар с каждой биржи для ускорения.
    """
    results = []
    # Собираем все уникальные пары USDT с каждой биржи
    all_pairs = set()
    for pairs in SUPPORTED_PAIRS.values():
        all_pairs.update([p for p in pairs if p.endswith("USDT") or p.endswith("-USDT")])
    all_pairs = list(all_pairs)
    print(f"[ARBITRAGE_ALL] Total unique pairs (before limit): {len(all_pairs)}")
    # Ограничим для ускорения
    all_pairs = all_pairs[:limit_per_exchange]
    print(f"[ARBITRAGE_ALL] Pairs after limit: {len(all_pairs)}")
    async def process_pair(pair, client):
        filtered_exchanges = []
        for ex in EXCHANGES_TEMPLATE:
            ex_pair = ex["pair_format"](pair)
            if SUPPORTED_PAIRS.get(ex["name"]) and ex_pair in SUPPORTED_PAIRS[ex["name"]]:
                filtered_exchanges.append(ex)
        prices = []
        for ex in filtered_exchanges:
            try:
                ex_pair = ex["pair_format"](pair)
                url = ex["url"](ex_pair)
                resp = await client.get(url)
                if resp.status_code != 200 or not resp.text.strip():
                    continue
                try:
                    data = resp.json()
                except Exception:
                    continue
                price = ex["extract"](data)
                prices.append({"exchange": ex["name"], "price": price})
            except Exception:
                continue
        valid_prices = [p for p in prices if p["price"] is not None]
        if len(valid_prices) >= 2:
            sorted_prices = sorted(valid_prices, key=lambda x: x["price"])
            min_ex = sorted_prices[0]
            max_ex = sorted_prices[-1]
            # Случайный объем
            volume = round(random.uniform(0.1, 10), 3)
            # Случайное время жизни
            total_seconds = random.randint(10, 300)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            lifetime = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
            # Случайные сети
            networks = ['Ethereum', 'TRON', 'BSC', 'Polygon']
            withdraw_net = random.choice(networks)
            deposit_net = random.choice(networks)
            # Хедж: список всех бирж, участвующих в цене
            hedge = ', '.join([p["exchange"] for p in sorted_prices])
            # Формируем ссылки на покупку/продажу монеты на биржах
            buy_url = None
            sell_url = None
            # Примеры шаблонов (можно расширить при необходимости)
            url_templates = {
                "Binance": "https://www.binance.com/ru/trade/{base}_{quote}",
                "Bybit": "https://www.bybit.com/trade/spot/{pair}",
                "KuCoin": "https://www.kucoin.com/trade/{pair}",
                "Mexc": "https://www.mexc.com/exchange/{base}_{quote}",
                "Gate": "https://www.gate.io/trade/{base}_{quote}",
                "BitGet": "https://www.bitget.com/spot/{pair}",
                "OKX": "https://www.okx.com/ru/trade-spot/{base}-{quote}",
                "HTX": "https://www.htx.com/en-us/trade/{pair}/"
            }
            # Разделяем пару на base и quote
            def split_pair(p):
                # Примитивно: если пара заканчивается на USDT, USD, BTC, ETH, TRY, BUSD, TUSD, USDC, DAI и т.д.
                for q in ["USDT", "USD", "BTC", "ETH", "TRY", "BUSD", "TUSD", "USDC", "DAI"]:
                    if p.endswith(q):
                        return p[:-len(q)], q
                # fallback
                return p[:-3], p[-3:]
            base, quote = split_pair(pair)
            buy_pair_url = pair
            sell_pair_url = pair
            buy_kwargs = {"pair": buy_pair_url, "base": base, "quote": quote}
            sell_kwargs = {"pair": sell_pair_url, "base": base, "quote": quote}
            # Для KuCoin и OKX: другой формат пары
            if min_ex["exchange"] == "KuCoin":
                buy_kwargs["pair"] = f"{base}-{quote}"
            if min_ex["exchange"] == "OKX":
                buy_kwargs["pair"] = f"{base}-{quote}"
            if max_ex["exchange"] == "KuCoin":
                sell_kwargs["pair"] = f"{base}-{quote}"
            if max_ex["exchange"] == "OKX":
                sell_kwargs["pair"] = f"{base}-{quote}"
            buy_url = url_templates.get(min_ex["exchange"], "").format(**buy_kwargs)
            sell_url = url_templates.get(max_ex["exchange"], "").format(**sell_kwargs)
            return {
                "pair": pair,
                "buy": min_ex["exchange"],
                "buy_price": min_ex["price"],
                "buy_url": buy_url,
                "sell": max_ex["exchange"],
                "sell_price": max_ex["price"],
                "sell_url": sell_url,
                "profit": max_ex["price"] - min_ex["price"],
                "volume": volume,  # legacy
                "volume_coin": volume,
                "volume_usd": round(volume * min_ex["price"], 2) if min_ex["price"] else 0,
                "lifetime": lifetime,
                "withdraw": f"{withdraw_net} (${round(random.uniform(0.5, 5), 2)})",
                "deposit": deposit_net,
                "hedge": hedge,
                "all_prices": sorted_prices
            }
        return None

    async with httpx.AsyncClient(timeout=7) as client:
        tasks = [process_pair(pair, client) for pair in all_pairs]
        results_raw = await asyncio.gather(*tasks)
        results = [r for r in results_raw if r]

    print(f"[ARBITRAGE_ALL] Results ready: {len(results)} opportunities, elapsed: {round(time.time()-start_time,2)}s")
    return {"opportunities": results, "count": len(results)}


async def fetch_supported_pairs():
    global SUPPORTED_PAIRS
    async with httpx.AsyncClient(timeout=10) as client:
        for ex in EXCHANGES_TEMPLATE:
            try:
                # Для XT.COM добавляем заголовок Accept: application/json
                if ex["name"] == "XT":
                    # Пробуем v3 endpoint и добавляем User-Agent
                    xt_urls = [
                        "https://api.xt.com/spot/v4/public/symbol",
                        "https://api.xt.com/spot/v3/public/symbol"
                    ]
                    resp = None
                    for url in xt_urls:
                        try:
                            resp = await client.get(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
                            if resp.status_code == 200 and resp.text.strip():
                                break
                        except Exception:
                            continue
                    if resp is None:
                        raise Exception("XT.COM: All endpoints failed")
                else:
                    resp = await client.get(ex["pairs_url"])
                data = resp.json()
                pairs = None
                try:
                    pairs = ex["pairs_field"](data)
                    if pairs is None or not isinstance(pairs, list):
                        raise ValueError("pairs_field did not return a valid list")
                    SUPPORTED_PAIRS[ex["name"]] = set(pairs)
                    print(f"[PAIRS] {ex['name']}: {len(SUPPORTED_PAIRS[ex['name']])} pairs loaded")
                except Exception as e_inner:
                    SUPPORTED_PAIRS[ex["name"]] = set()
                    print(f"[PAIRS] {ex['name']}: FAILED to parse pairs ({e_inner})")
                    print(f"[PAIRS-DEBUG] {ex['name']} response: {data}")
            except Exception as e:
                SUPPORTED_PAIRS[ex["name"]] = set()
                print(f"[PAIRS] {ex['name']}: FAILED to load pairs ({e})")

@app.on_event("startup")
async def startup_event():
    await fetch_supported_pairs()

@app.get("/arbitrage")
async def get_arbitrage(pair: str = Query("BTCUSDT", description="Trading pair, e.g. BTCUSDT, ETHUSDT, LTCUSDT")):
    results = []
    filtered_exchanges = []
    for ex in EXCHANGES_TEMPLATE:
        ex_pair = ex["pair_format"](pair)
        if SUPPORTED_PAIRS.get(ex["name"]) and ex_pair in SUPPORTED_PAIRS[ex["name"]]:
            filtered_exchanges.append(ex)
    async with httpx.AsyncClient(timeout=5) as client:
        prices = []
        for ex in filtered_exchanges:
            try:
                ex_pair = ex["pair_format"](pair)
                url = ex["url"](ex_pair)
                resp = await client.get(url)
                if resp.status_code != 200 or not resp.text.strip():
                    err = f"Код {resp.status_code}, тело: {resp.text[:100]}"
                    raise ValueError(f"Нет данных по паре или ошибка ответа от биржи: {err}")
                try:
                    data = resp.json()
                except Exception:
                    raise ValueError(f"Ответ не является JSON: {resp.text[:100]}")
                price = ex["extract"](data)
                prices.append({"exchange": ex["name"], "price": price})
            except Exception as e:
                prices.append({"exchange": ex["name"], "price": None, "error": str(e)})
        # Find arbitrage
        valid_prices = [p for p in prices if p["price"] is not None]
        if len(valid_prices) >= 2:
            sorted_prices = sorted(valid_prices, key=lambda x: x["price"])
            min_ex = sorted_prices[0]
            max_ex = sorted_prices[-1]
            results.append({
    "buy": min_ex["exchange"],
    "buy_price": min_ex["price"],
    "sell": max_ex["exchange"],
    "sell_price": max_ex["price"],
    "profit": max_ex["price"] - min_ex["price"],
    "volume": 1.23,  # фиктивное значение
    "lifetime": "2m 15s",  # фиктивное значение
    "withdraw": "Ethereum ($2.1)",  # фиктивное значение
    "deposit": "Ethereum",  # фиктивное значение
    "hedge": "-"  # фиктивное значение
})
        return {"prices": prices, "opportunities": results, "available_on": [ex["name"] for ex in filtered_exchanges]}
