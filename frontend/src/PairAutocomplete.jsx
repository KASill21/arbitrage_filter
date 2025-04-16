import React from "react";
import { Autocomplete, TextField } from "@mui/material";

export default function PairAutocomplete({ value, onChange, options }) {
  return (
    <Autocomplete
      freeSolo
      options={options}
      value={value}
      onInputChange={(_, newValue) => onChange(newValue.toUpperCase())}
      renderInput={(params) => (
        <TextField {...params} label="Пара (например, BTCUSDT)" variant="outlined" />
      )}
      sx={{ minWidth: 220 }}
    />
  );
}
