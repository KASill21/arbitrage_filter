import React, { useState } from "react";
import {
  Table, TableHead, TableRow, TableCell, TableBody, TableSortLabel
} from "@mui/material";

export default function SortableTable({ columns, rows }) {
  const [orderBy, setOrderBy] = useState(columns[0].id);
  const [order, setOrder] = useState("desc");

  const handleSort = (col) => {
    if (orderBy === col) {
      setOrder(order === "asc" ? "desc" : "asc");
    } else {
      setOrderBy(col);
      setOrder("desc");
    }
  };

  const sortedRows = [...rows].sort((a, b) => {
    let v1 = a[orderBy];
    let v2 = b[orderBy];
    // Try to compare as number if possible
    const n1 = parseFloat(v1);
    const n2 = parseFloat(v2);
    if (!isNaN(n1) && !isNaN(n2)) {
      v1 = n1;
      v2 = n2;
    }
    if (v1 < v2) return order === "asc" ? -1 : 1;
    if (v1 > v2) return order === "asc" ? 1 : -1;
    return 0;
  });

  return (
    <Table size="small" sx={{ minWidth: 900 }}>
      <TableHead>
        <TableRow>
          {columns.map(col => (
            <TableCell key={col.id} sortDirection={orderBy === col.id ? order : false}>
              <TableSortLabel
                active={orderBy === col.id}
                direction={orderBy === col.id ? order : "asc"}
                onClick={() => handleSort(col.id)}
              >
                {col.label}
              </TableSortLabel>
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {sortedRows.length ? sortedRows.map((row, i) => (
          <TableRow key={i}>
            {columns.map(col => (
              <TableCell key={col.id}>{col.render ? col.render(row) : row[col.id]}</TableCell>
            ))}
          </TableRow>
        )) : (
          <TableRow><TableCell colSpan={columns.length} align="center">Нет данных</TableCell></TableRow>
        )}
      </TableBody>
    </Table>
  );
}
