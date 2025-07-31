'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useMorphik } from '@/contexts/morphik-context'

export default function Home() {
  const router = useRouter()
  const { authToken } = useMorphik()

  useEffect(() => {
    if (authToken) {
      router.replace('/documents')
    } else {
      router.replace('/login')
    }
  }, [authToken, router])

  return null
}
