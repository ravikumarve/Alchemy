'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, Package, FileText, Table, CheckCircle, XCircle, Clock } from 'lucide-react'

interface PackageData {
  package_id: string
  version: string
  source_agent: string
  target_agent: string
  timestamp: string
  metadata: any
  content: any[]
  tables: any[]
  quality: any
  handoff: any
}

export default function PackageDetail() {
  const params = useParams()
  const packageId = params.packageId as string
  const [packageData, setPackageData] = useState<PackageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchPackage()
  }, [packageId])

  const fetchPackage = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/packages/${packageId}`)
      if (response.ok) {
        const data = await response.json()
        setPackageData(data)
      } else {
        setError('Package not found')
      }
    } catch (err) {
      setError('Error fetching package')
      console.error('Error fetching package:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Package className="h-12 w-12 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading package...</p>
        </div>
      </div>
    )
  }

  if (error || !packageData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <p className="text-muted-foreground mb-4">{error || 'Package not found'}</p>
          <Button asChild>
            <a href="/">Back to Dashboard</a>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" asChild className="mb-4">
            <a href="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </a>
          </Button>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            Package Details
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            {packageData.package_id}
          </p>
        </div>

        {/* Package Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Version</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{packageData.version}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Source</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{packageData.source_agent}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Target</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{packageData.target_agent}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Created</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-sm font-bold">
                {new Date(packageData.timestamp).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quality Assessment */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Quality Assessment</CardTitle>
            <CardDescription>Overall quality metrics for this package</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Overall Quality:</span>
                  <span className="font-medium">{packageData.quality?.overall_quality || 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Evergreen Score:</span>
                  <span className="font-medium">
                    {packageData.quality?.overall_evergreen_score?.toFixed(2) || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Avg Confidence:</span>
                  <span className="font-medium">
                    {packageData.quality?.average_confidence_score?.toFixed(2) || 'N/A'}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm font-medium mb-2">Quality Distribution:</div>
                {Object.entries(packageData.quality?.quality_distribution || {}).map(([level, count]) => (
                  <div key={level} className="flex justify-between text-sm">
                    <span className="text-muted-foreground capitalize">{level}:</span>
                    <span className="font-medium">{count as number}</span>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                <div className="text-sm font-medium mb-2">Content Themes:</div>
                <div className="flex flex-wrap gap-2">
                  {packageData.handoff?.content_themes?.map((theme: string, index: number) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-primary/10 text-primary rounded-md text-xs"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Content Chunks */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Content Chunks</CardTitle>
            <CardDescription>
              {packageData.content.length} semantic chunks extracted from the document
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {packageData.content.slice(0, 5).map((chunk, index) => (
                <div key={index} className="p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800">
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
              ))}
              {packageData.content.length > 5 && (
                <div className="text-center text-sm text-muted-foreground">
                  And {packageData.content.length - 5} more chunks...
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Tables */}
        {packageData.tables.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Extracted Tables</CardTitle>
              <CardDescription>
                {packageData.tables.length} tables extracted from the document
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {packageData.tables.map((table, index) => (
                  <div key={index} className="p-4 border rounded-lg">
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
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
