import React from "react";
import { Button } from "@mui/material";

export default function ExportCSV({ data, filename = "arbitrage.csv" }) {
  const handleExport = () => {
    if (!data || !data.length) return;
    const header = Object.keys(data[0]);
    const csv = [header.join(",")].concat(
      data.map(row => header.map(h => row[h]).join(","))
    ).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <Button variant="outlined" size="small" onClick={handleExport} sx={{ ml: 2 }}>
      Экспорт CSV
    </Button>
  );
}
