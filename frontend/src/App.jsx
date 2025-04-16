import React, { useEffect, useState } from "react";
import {
  Container, Paper, Typography, Box, TextField, Select, MenuItem, InputLabel, OutlinedInput, Checkbox, ListItemText, Stack, Collapse, IconButton, Button
} from "@mui/material";
import SortableTable from "./SortableTable";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const EXCHANGES = ["Binance", "Bybit", "KuCoin", "Mexc", "Gate", "BitGet", "OKX", "XT", "HTX"];
const AUTOREFRESH_OPTIONS = [5, 10, 20, 30, 60];

export default function App() {
  // Фильтры
  const [selectedExchanges, setSelectedExchanges] = useState(EXCHANGES);
  const [whiteList, setWhiteList] = useState("");
  const [blackList, setBlackList] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [minProfit, setMinProfit] = useState("");
  const [maxProfit, setMaxProfit] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(10);
const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(true);
const [refreshTrigger, setRefreshTrigger] = useState(0);
// const [pair, setPair] = useState("BTCUSDT");
const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState([]);

  // Эффект для загрузки данных
useEffect(() => {
  setLoading(true);
  fetch(`http://localhost:8000/arbitrage/all`)
  .then(res => res.json())
  .then(data => {
    if (data && data.opportunities && data.opportunities.length > 0) {
      setRows(data.opportunities.map(op => ({
        pair: op.pair,
        buy: op.buy,
        buy_url: op.buy_url ?? "#",
        buy_price: op.buy_price ?? '-',
        sell: op.sell,
        sell_url: op.sell_url ?? "#",
        sell_price: op.sell_price ?? '-',
        volume_coin: op.volume_coin ?? '-',
        volume_usd: op.volume_usd ?? '-',
        profit_percent: ((op.profit / op.buy_price) * 100).toFixed(2),
        lifetime: op.lifetime ?? '-',
        withdraw: op.withdraw ?? '-',
        deposit: op.deposit ?? '-',
        hedge: op.hedge ?? '-'
      })));
    } else {
      setRows([]);
    }
  })
  .catch(() => setRows([]))
  .finally(() => setLoading(false));
}, [refreshTrigger]);

// Эффект для автообновления
useEffect(() => {
  if (!isAutoRefreshEnabled) return;
  const timer = setInterval(() => {
    setRefreshTrigger(v => v + 1);
  }, autoRefresh * 1000);
  return () => clearInterval(timer);
}, [autoRefresh, isAutoRefreshEnabled]);

const handleManualRefresh = () => {
  setRefreshTrigger(v => v + 1);
};

  return (
    <>
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="xl">
          <Paper sx={{ p: 3, mb: 3 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" flexWrap="wrap">
              <Box sx={{ minWidth: 220 }}>
                <InputLabel>Отслеживаемые биржи</InputLabel>
                <Select
                  multiple
                  value={selectedExchanges}
                  onChange={e => setSelectedExchanges(e.target.value)}
                  input={<OutlinedInput label="Отслеживаемые биржи" />}
                  renderValue={selected => selected.join(', ')}
                  size="small"
                  sx={{ width: 220 }}
                >
                  {EXCHANGES.map(ex => (
                    <MenuItem key={ex} value={ex}>
                      <Checkbox checked={selectedExchanges.indexOf(ex) > -1} />
                      <ListItemText primary={ex} />
                    </MenuItem>
                  ))}
                </Select>
              </Box>
              {/* <TextField label="Валютная пара" value={pair} onChange={e => setPair(e.target.value.toUpperCase())} size="small" sx={{ minWidth: 140 }} placeholder="BTCUSDT" /> */}
<TextField label="Белый список валют" value={whiteList} onChange={e => setWhiteList(e.target.value)} size="small" sx={{ minWidth: 170 }} placeholder="BTC,ETH..." />
              <TextField label="Чёрный список валют" value={blackList} onChange={e => setBlackList(e.target.value)} size="small" sx={{ minWidth: 170 }} placeholder="TON,SHIB..." />
              <TextField label="Мин. сумма сделки, $" value={minAmount} onChange={e => setMinAmount(e.target.value)} size="small" sx={{ width: 120 }} />
              <TextField label="Мин. профит, %" value={minProfit} onChange={e => setMinProfit(e.target.value)} size="small" sx={{ width: 100 }} />
              <TextField label="Макс. профит, %" value={maxProfit} onChange={e => setMaxProfit(e.target.value)} size="small" sx={{ width: 100 }} />
              <Box>
                <InputLabel sx={{ fontSize: 13, mb: 0.5 }}>Автообновление</InputLabel>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Checkbox
                    checked={isAutoRefreshEnabled}
                    onChange={e => setIsAutoRefreshEnabled(e.target.checked)}
                    size="small"
                  />
                  <Typography variant="body2">Вкл.</Typography>
                  <Select
                    value={autoRefresh}
                    onChange={e => setAutoRefresh(e.target.value)}
                    size="small"
                    sx={{ width: 100 }}
                    disabled={!isAutoRefreshEnabled}
                  >
                    {AUTOREFRESH_OPTIONS.map(opt => (
                      <MenuItem key={opt} value={opt}>{opt} секунд</MenuItem>
                    ))}
                  </Select>
                  <Box sx={{ ml: 1 }}>
                    <Button onClick={handleManualRefresh} variant="contained" size="small">Обновить</Button>
                  </Box>
                </Stack>
              </Box>
              <IconButton onClick={() => setShowAdvanced(v => !v)} size="small" sx={{ ml: 1 }}>
                <ExpandMoreIcon sx={{ transform: showAdvanced ? 'rotate(180deg)' : 'none', transition: '0.2s' }} />
              </IconButton>
            </Stack>
            <Collapse in={showAdvanced}>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">Расширенные настройки (можно добавить любые поля)</Typography>
                {/* Здесь можно добавить дополнительные фильтры */}
              </Box>
            </Collapse>
          </Paper>
          <Paper sx={{ p: 2 }}>
            <SortableTable
              columns={[
                { id: 'pair', label: 'Валютная пара' },
                { id: 'buy', label: 'Биржа для покупки', render: row => (
                  <>
                    <a href={row.buy_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'inherit', fontWeight: 600 }}>{row.buy}</a>
                    <br /><span style={{ fontSize: 13, color: '#888' }}>{row.buy_price} $</span>
                  </>
                ) },
                { id: 'sell', label: 'Биржа для продажи', render: row => (
                  <>
                    <a href={row.sell_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'inherit', fontWeight: 600 }}>{row.sell}</a>
                    <br /><span style={{ fontSize: 13, color: '#888' }}>{row.sell_price} $</span>
                  </>
                ) },
                { id: 'volume_coin', label: 'Объём', render: row => `${row.volume_coin} (${row.volume_usd} $)` },
                { id: 'profit_percent', label: 'Профит', render: row => <span style={{ color: row.profit_percent > 0 ? '#388e3c' : undefined, fontWeight: 600 }}>{row.profit_percent > 0 ? '+' : ''}{row.profit_percent}%</span> },
                { id: 'lifetime', label: 'Время жизни' },
                { id: 'withdraw', label: 'Сети вывода' },
                { id: 'deposit', label: 'Сети депозита' },
                { id: 'hedge', label: 'Хеджирование' },
              ]}
              rows={loading ? [] : rows.filter(row => selectedExchanges.includes(row.buy) && selectedExchanges.includes(row.sell))}
            />
            {loading && <Box sx={{ textAlign: 'center', p: 2 }}>Загрузка...</Box>}
          </Paper>
        </Container>
      </Box>
    </>
  );
}
