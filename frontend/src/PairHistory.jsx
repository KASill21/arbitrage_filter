import React from "react";
import { Chip, Stack } from "@mui/material";

export default function PairHistory({ history, onSelect, onClear }) {
  if (!history || !history.length) return null;
  return (
    <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap' }}>
      {history.map(pair => (
        <Chip
          key={pair}
          label={pair}
          onClick={() => onSelect(pair)}
          sx={{ cursor: 'pointer' }}
        />
      ))}
      <Chip label="Очистить" color="error" onClick={onClear} sx={{ cursor: 'pointer' }} />
    </Stack>
  );
}
