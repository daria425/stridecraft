import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router'
import { AdoptPage } from './features/adopt/AdoptPage'
import { Gate } from './features/auth/Gate'
import { LoginPage } from './features/auth/LoginPage'
import { GalleryPage } from './features/gallery/GalleryPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { ProfilePage } from './features/profile/ProfilePage'
import { JourneyMapPage } from './features/journey/JourneyMapPage'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* TEMPORARY model gallery, no login needed */}
          <Route path="/gallery" element={<GalleryPage />} />
          <Route element={<Gate page="/login" />}>
            <Route path="/login" element={<LoginPage />} />
          </Route>
          <Route element={<Gate page="/adopt" />}>
            <Route path="/adopt" element={<AdoptPage />} />
          </Route>
          <Route element={<Gate page="/" />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/voyage" element={<JourneyMapPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
