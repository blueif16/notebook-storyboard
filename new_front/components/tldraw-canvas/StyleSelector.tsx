'use client'

import { useState } from 'react'

interface StyleOption {
  key: string
  name: string
  description: string
  image_url?: string
}

interface StyleSelectorProps {
  options: StyleOption[]
  onSelect: (key: string) => void
}

export function StyleSelector({ options, onSelect }: StyleSelectorProps) {
  const [selected, setSelected] = useState<number | null>(null)

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500 font-medium">选择插画风格：</p>
      <div className="space-y-2">
        {options.map((style, idx) => (
          <label
            key={style.key}
            className={`flex items-start gap-2 p-2 rounded-lg border cursor-pointer transition-colors ${
              selected === idx
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }`}
            onClick={() => setSelected(idx)}
          >
            <input
              type="radio"
              name="style"
              checked={selected === idx}
              onChange={() => setSelected(idx)}
              className="mt-1 accent-blue-500"
            />
            {style.image_url && (
              <img
                src={style.image_url}
                alt={style.name}
                className="w-16 h-16 rounded-md object-cover flex-shrink-0"
              />
            )}
            <div className="min-w-0">
              <div className="text-sm font-medium text-gray-800">{style.name}</div>
              <div className="text-xs text-gray-500 leading-relaxed">{style.description}</div>
            </div>
          </label>
        ))}
      </div>
      <button
        disabled={selected === null}
        onClick={() => selected !== null && onSelect(options[selected].key)}
        className="w-full mt-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-lg transition-colors"
      >
        确认选择
      </button>
    </div>
  )
}
