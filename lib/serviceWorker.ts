'use client'

import { useEffect, useState } from 'react'

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[]
  readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
  prompt(): Promise<void>
}

export function useServiceWorker() {
  const [swStatus, setSwStatus] = useState<'idle' | 'installing' | 'installed' | 'failed'>('idle')
  const [isOnline, setIsOnline] = useState(true)

  useEffect(() => {
    // Register service worker
    if ('serviceWorker' in navigator) {
      setSwStatus('installing')
      
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service worker registered:', registration)
          setSwStatus('installed')
          
          // Check if there's an update
          registration.addEventListener('updatefound', () => {
            console.log('Service worker update found')
            const newWorker = registration.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', (event) => {
                if (newWorker.state === 'installed') {
                  console.log('New service worker installed')
                }
              })
            }
          })
        })
        .catch((error) => {
          console.error('Service worker registration failed:', error)
          setSwStatus('failed')
        })
    }

    // Monitor online/offline status
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    setIsOnline(navigator.onLine)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Function to install service worker (for PWA install prompt)
  const installServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.ready
        console.log('Service worker is ready')
        return registration
      } catch (error) {
        console.error('Failed to get service worker registration:', error)
        throw error
      }
    }
    throw new Error('Service workers not supported')
  }

  // Function to check if app is installable (PWA)
  const canInstallPWA = () => {
    if (typeof window === 'undefined') return false
    
    // Check if service worker is supported
    if (!('serviceWorker' in navigator)) return false
    
    // Check if app is already installed
    if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
      return false
    }
    
    // Check if app is in a web app context
    const navigatorWithStandalone = window.navigator as Navigator & { standalone?: boolean }
    if (navigatorWithStandalone && navigatorWithStandalone.standalone === true) {
      return false
    }
    
    return true
  }

  return {
    swStatus,
    isOnline,
    installServiceWorker,
    canInstallPWA,
  }
}