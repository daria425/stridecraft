import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router'
import { AdoptPage } from './features/adopt/AdoptPage'
import { Gate } from './features/auth/Gate'
import { LoginPage } from './features/auth/LoginPage'
import { DashboardPage } from './features/dashboard/DashboardPage'
import { AdoptSandbox } from './dev/AdoptSandbox'
import { DashboardSandbox } from './dev/DashboardSandbox'
import { PickerSandbox } from './dev/PickerSandbox'
import { CreatureSandbox } from './dev/CreatureSandbox'

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
          </Route>
          {import.meta.env.DEV && <Route path="/dev/picker" element={<PickerSandbox />} />}
          {import.meta.env.DEV && <Route path="/dev/adopt" element={<AdoptSandbox />} />}
          {import.meta.env.DEV && <Route path="/dev/login" element={<LoginPage />} />}
          {import.meta.env.DEV && <Route path="/dev/dashboard" element={<DashboardSandbox />} />}
          {import.meta.env.DEV && <Route path="/dev/creature" element={<CreatureSandbox />} />}
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
