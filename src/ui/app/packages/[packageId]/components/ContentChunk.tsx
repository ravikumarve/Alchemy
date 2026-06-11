'use client'

import { useState, useEffect } from 'react'

interface ContentChunkProps {
  chunk: any
}

export default function ContentChunk({ chunk }: ContentChunkProps) {
  return (
    <div className="p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">{chunk.chunk_id}</span>
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md">
            {chunk.content_type}
          </span>
          <span className="px-2 py-1 bg-green-100 text-green-700 rounded-md">
            {chunk.quality_level}
          </span>
        </div>
      </div>
      <p className="text-sm text-muted-foreground mb-2 line-clamp-3">
        {chunk.text}
      </p>
      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
        <span>Evergreen: {chunk.evergreen_score.toFixed(2)}</span>
        <span>Confidence: {chunk.confidence_score.toFixed(2)}</span>
        <span>Length: {chunk.length} chars</span>
      </div>
    </div>
  )
}