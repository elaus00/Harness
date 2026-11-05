import { setBooleanFeatureFlagResolver } from '@atlaskit/platform-feature-flags/setBooleanFeatureFlagResolver'
import { setGlobalTheme } from '@atlaskit/tokens/set-global-theme'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

setBooleanFeatureFlagResolver(() => false)
void setGlobalTheme({ light: 'light', dark: 'dark', colorMode: 'light' })

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
