'use client'

import axios, { AxiosInstance, AxiosResponse } from 'axios'

export interface Job {
  job_id: string
  status: string
  file_name: string
  created_at: string
  updated_at: string
  processing_time?: number
  error_message?: string
  package_id?: string
}

export interface Package {
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

export interface ProcessResponse {
  job_id: string
  status: string
  file_name: string
  created_at: string
  updated_at: string
}

export interface ListResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ErrorResponse {
  detail: string
}

export class AlchemyAPI {
  private client: AxiosInstance

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized error
          console.error('Unauthorized access')
        } else if (error.response?.status === 404) {
          // Handle not found error
          console.error('Resource not found')
        } else if (error.response?.status >= 500) {
          // Handle server error
          console.error('Server error:', error.response.data)
        }
        return Promise.reject(error)
      }
    )
  }

  // Process a file
  async processFile(file: File): Promise<ProcessResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post<ProcessResponse>('/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  // Get job status
  async getJobStatus(jobId: string): Promise<Job> {
    const response = await this.client.get<Job>(`/jobs/${jobId}`)
    return response.data
  }

  // List jobs
  async listJobs(options?: {
    status?: string
    limit?: number
    offset?: number
  }): Promise<ListResponse<Job>> {
    const params = new URLSearchParams()
    if (options?.status) params.append('status', options.status)
    if (options?.limit) params.append('limit', options.limit.toString())
    if (options?.offset) params.append('offset', options.offset.toString())

    const response = await this.client.get<ListResponse<Job>>(`/jobs?${params.toString()}`)
    return response.data
  }

  // Get package
  async getPackage(packageId: string): Promise<Package> {
    const response = await this.client.get<Package>(`/packages/${packageId}`)
    return response.data
  }

  // List packages
  async listPackages(options?: {
    source_agent?: string
    target_agent?: string
    limit?: number
    offset?: number
  }): Promise<ListResponse<Package>> {
    const params = new URLSearchParams()
    if (options?.source_agent) params.append('source_agent', options.source_agent)
    if (options?.target_agent) params.append('target_agent', options.target_agent)
    if (options?.limit) params.append('limit', options.limit.toString())
    if (options?.offset) params.append('offset', options.offset.toString())

    const response = await this.client.get<ListResponse<Package>>(`/packages?${params.toString()}`)
    return response.data
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    const response = await this.client.get('/health')
    return response.data
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage: (data: any) => void, onError?: (error: any) => void): WebSocket {
    const ws = new WebSocket(`${this.client.defaults.baseURL?.replace('/api/v1', '')}/ws`)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    return ws
  }
}

// Export default instance
export default AlchemyAPI