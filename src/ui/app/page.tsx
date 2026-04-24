'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, FileText, Package, Activity, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

interface Job {
  job_id: string
  status: string
  file_name: string
  created_at: string
  updated_at: string
  processing_time?: number
  error_message?: string
  package_id?: string
}

interface Package {
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

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [packages, setPackages] = useState<Package[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchJobs()
    fetchPackages()
    const interval = setInterval(() => {
      fetchJobs()
      fetchPackages()
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(interval)
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/jobs`)
      const data = await response.json()
      setJobs(data)
    } catch (error) {
      console.error('Error fetching jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPackages = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/packages`)
      const data = await response.json()
      setPackages(data)
    } catch (error) {
      console.error('Error fetching packages:', error)
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_URL}/api/v1/process`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        alert(`File uploaded successfully! Job ID: ${data.job_id}`)
        setSelectedFile(null)
        fetchJobs()
      } else {
        const error = await response.json()
        alert(`Error uploading file: ${error.detail}`)
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Error uploading file')
    } finally {
      setUploading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'processing':
        return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'failed':
        return 'text-red-600'
      case 'processing':
        return 'text-blue-600'
      default:
        return 'text-yellow-600'
    }
  }

  const stats = {
    totalJobs: jobs.length,
    completedJobs: jobs.filter(j => j.status === 'completed').length,
    failedJobs: jobs.filter(j => j.status === 'failed').length,
    processingJobs: jobs.filter(j => j.status === 'processing').length,
    totalPackages: packages.length,
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            🌐 ALCHEMY Dashboard
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Temporal Content Transmuter - Monitor your content processing pipeline
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalJobs}</div>
              <p className="text-xs text-muted-foreground">All processing jobs</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.completedJobs}</div>
              <p className="text-xs text-muted-foreground">Successfully processed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Processing</CardTitle>
              <Activity className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.processingJobs}</div>
              <p className="text-xs text-muted-foreground">Currently in progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Packages</CardTitle>
              <Package className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.totalPackages}</div>
              <p className="text-xs text-muted-foreground">Generated packages</p>
            </CardContent>
          </Card>
        </div>

        {/* Upload Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Upload File for Processing</CardTitle>
            <CardDescription>
              Upload PDF, TXT, or HTML files to process through the Archaeologist workflow
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <input
                type="file"
                accept=".pdf,.txt,.html,.htm"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="flex-1"
                disabled={uploading}
              />
              <Button
                onClick={handleFileUpload}
                disabled={!selectedFile || uploading}
                className="min-w-[120px]"
              >
                {uploading ? (
                  <>
                    <Activity className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Jobs Table */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Recent Jobs</CardTitle>
            <CardDescription>Track your file processing jobs</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <Activity className="h-8 w-8 animate-spin mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Loading jobs...</p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No jobs yet. Upload a file to get started!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium">Status</th>
                      <th className="text-left py-3 px-4 font-medium">File Name</th>
                      <th className="text-left py-3 px-4 font-medium">Created</th>
                      <th className="text-left py-3 px-4 font-medium">Processing Time</th>
                      <th className="text-left py-3 px-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((job) => (
                      <tr key={job.job_id} className="border-b hover:bg-slate-50 dark:hover:bg-slate-800">
                        <td className="py-3 px-4">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(job.status)}
                            <span className={`text-sm font-medium ${getStatusColor(job.status)}`}>
                              {job.status}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm">{job.file_name}</td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {new Date(job.created_at).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-sm">
                          {job.processing_time ? `${job.processing_time.toFixed(2)}s` : '-'}
                        </td>
                        <td className="py-3 px-4">
                          {job.package_id && (
                            <Button variant="ghost" size="sm" asChild>
                              <a href={`/packages/${job.package_id}`}>View Package</a>
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Packages Grid */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Packages</CardTitle>
            <CardDescription>View processed content packages</CardDescription>
          </CardHeader>
          <CardContent>
            {packages.length === 0 ? (
              <div className="text-center py-8">
                <Package className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">No packages yet. Complete a job to generate packages!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {packages.slice(0, 6).map((pkg) => (
                  <Card key={pkg.package_id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{pkg.package_id}</CardTitle>
                      <CardDescription>
                        {pkg.source_agent} → {pkg.target_agent}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Content:</span>
                          <span className="font-medium">{pkg.content.length} chunks</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Tables:</span>
                          <span className="font-medium">{pkg.tables.length} tables</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Quality:</span>
                          <span className="font-medium">{pkg.quality?.overall_quality || 'N/A'}</span>
                        </div>
                        <div className="text-xs text-muted-foreground pt-2">
                          {new Date(pkg.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <Button variant="outline" size="sm" className="w-full mt-4" asChild>
                        <a href={`/packages/${pkg.package_id}`}>View Details</a>
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
