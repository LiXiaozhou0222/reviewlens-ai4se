import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from '../src/App'

describe('App bootstrap', () => {
  it('renders the mode shell', () => {
    render(<App />)

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'ReviewLens' })).toBeInTheDocument()
    expect(screen.getByText('Mode shell')).toBeInTheDocument()
  })
})
