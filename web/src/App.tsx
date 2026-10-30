import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router'
import { AdoptPage } from './features/adopt/AdoptPage'
import { Gate } from './features/auth/Gate'
import { LoginPage } from './features/auth/LoginPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { JourneyMapPage } from './features/journey/JourneyMapPage'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Gate page="/login" />}>
            <Route path="/login" element={<LoginPage />} />
          </Route>
          <Route element={<Gate page="/adopt" />}>
            <Route path="/adopt" element={<AdoptPage />} />
          </Route>
          <Route element={<Gate page="/" />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/voyage" element={<JourneyMapPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
