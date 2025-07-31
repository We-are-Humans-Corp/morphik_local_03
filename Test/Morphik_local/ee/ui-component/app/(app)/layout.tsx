'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { MorphikSidebarStateful } from '@/components/morphik-sidebar-stateful'
import { DynamicSiteHeader } from '@/components/dynamic-site-header'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar-new'
import { HeaderProvider } from '@/contexts/header-context'
import { useMorphik } from '@/contexts/morphik-context'

type ValidSection = 'documents' | 'pdf' | 'search' | 'chat' | 'graphs' | 'workflows' | 'connections' | 'settings' | 'logs'

const pathToSection: Record<string, ValidSection> = {
  '/documents': 'documents',
  '/pdf': 'pdf',
  '/search': 'search',
  '/chat': 'chat',
  '/graphs': 'graphs',
  '/workflows': 'workflows',
  '/connections': 'connections',
  '/settings': 'settings',
  '/logs': 'logs',
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { setAuthToken } = useMorphik()
  const [userProfile, setUserProfile] = useState<{
    name: string
    email: string
    avatar: string
  } | null>(null)

  // Get current section from pathname
  const currentSection = pathname ? (pathToSection[pathname] || 'documents') : 'documents'

  // Load user profile from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser)
        setUserProfile({
          name: user.username || 'User',
          email: user.email || '',
          avatar: '/assets/placeholder-user.svg'
        })
      } catch (error) {
        console.error('Failed to parse user data:', error)
      }
    }
  }, [])

  const handleSectionChange = (section: string) => {
    router.push(`/${section}`)
  }

  const handleLogout = () => {
    // Clear auth token
    setAuthToken(null)
    
    // Redirect to login
    router.push('/login')
  }

  const handleProfileNavigate = (section: 'account' | 'billing' | 'notifications') => {
    // Navigate to settings with specific section
    router.push(`/settings?section=${section}`)
  }

  return (
    <div className="min-h-screen bg-sidebar">
      <HeaderProvider>
        <SidebarProvider
          style={{
            '--sidebar-width': 'calc(var(--spacing) * 72)',
            '--header-height': 'calc(var(--spacing) * 12)',
          } as React.CSSProperties}
        >
          <MorphikSidebarStateful
            variant="inset"
            currentSection={currentSection}
            onSectionChange={handleSectionChange}
            userProfile={userProfile || undefined}
            onLogout={handleLogout}
            onProfileNavigate={handleProfileNavigate}
          />
          <SidebarInset>
            <DynamicSiteHeader userProfile={userProfile || undefined} />
            <div className="flex flex-1 flex-col p-4 md:p-6">{children}</div>
          </SidebarInset>
        </SidebarProvider>
      </HeaderProvider>
    </div>
  )
}