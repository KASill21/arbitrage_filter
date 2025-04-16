import React from "react";
import { Container, Typography, Paper } from "@mui/material";

export default function About() {
  return (
    <Container maxWidth="md" sx={{ mt: 5 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>О проекте Arbitrage Scanner</Typography>
        <Typography variant="body1" paragraph>
          Этот сайт позволяет отслеживать арбитражные возможности между крупнейшими криптобиржами (Binance, Bybit, KuCoin и др.) в реальном времени.
        </Typography>
        <Typography variant="body1" paragraph>
          Данные собираются через публичные API бирж. Для каждой торговой пары отображаются цены, возможная прибыль, комиссии и статус по каждой бирже.
        </Typography>
        <Typography variant="body1" paragraph>
          <b>Исходный код</b>: <a href="https://github.com/your-repo/arbitrage-scanner" target="_blank" rel="noopener noreferrer">GitHub</a>
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Разработано с помощью AI Cascade, 2025
        </Typography>
      </Paper>
    </Container>
  );
}
