import { describe, it, expect, vi } from 'vitest'
import { render, fireEvent } from '@testing-library/react'
import StarRating from '@/components/resenhas/StarRating'

describe('StarRating', () => {
  it('renders 5 stars', () => {
    render(<StarRating value={3} readonly />)
    // Each star is a button element
    const buttons = document.querySelectorAll('button')
    expect(buttons).toHaveLength(5)
  })

  it('calls onChange when a star is clicked in interactive mode', () => {
    const onChange = vi.fn()
    render(<StarRating value={0} onChange={onChange} />)
    const buttons = document.querySelectorAll('button')
    fireEvent.click(buttons[3]) // 4th star = value 4
    expect(onChange).toHaveBeenCalledWith(4)
  })

  it('does not call onChange in readonly mode', () => {
    const onChange = vi.fn()
    render(<StarRating value={3} onChange={onChange} readonly />)
    const buttons = document.querySelectorAll('button')
    fireEvent.click(buttons[0])
    expect(onChange).not.toHaveBeenCalled()
  })

  it('disables all buttons in readonly mode', () => {
    render(<StarRating value={5} readonly />)
    const buttons = document.querySelectorAll('button')
    buttons.forEach((btn) => expect(btn).toBeDisabled())
  })
})
