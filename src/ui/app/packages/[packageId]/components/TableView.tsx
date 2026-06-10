"use client'

import { useState, useEffect } from 'react'

interface TableViewProps {
  table: any
}

export function TableView({ table }: TableViewProps) {
  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">{table.table_id}</span>
        <span className="text-xs text-muted-foreground">
          {table.format} • {table.row_count} rows × {table.col_count} cols
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              {table.headers.map((header: string, i: number) => (
                <th key={i} className="py-2 px-3 text-left font-medium">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.data.slice(0, 3).map((row: any, i: number) => (
              <tr key={i} className="border-b">
                {table.headers.map((header: string, j: number) => (
                  <td key={j} className="py-2 px-3">
                    {row[header]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}