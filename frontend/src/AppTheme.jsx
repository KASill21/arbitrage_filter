import React from "react";
import { createTheme, ThemeProvider, CssBaseline } from "@mui/material";

export function getTheme(mode) {
  return createTheme({
    palette: {
      mode,
      primary: { main: '#1976d2' },
      secondary: { main: '#ff9800' },
    },
  });
}

export default function AppTheme({ mode, children }) {
  return (
    <ThemeProvider theme={getTheme(mode)}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
