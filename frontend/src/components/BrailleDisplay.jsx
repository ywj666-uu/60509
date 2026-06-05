import { BRAILLE_DOTS } from '../utils/constants'

export default function BrailleDisplay({ text, showDots = true }) {
  const renderCell = (char) => {
    const dots = BRAILLE_DOTS[char.toLowerCase()] || []
    // Braille cell: 2 columns x 3 rows, dots numbered 1-6
    // Left: 1,2,3  Right: 4,5,6
    const positions = [
      [1, 4],
      [2, 5],
      [3, 6],
    ]

    return (
      <div key={char} className="inline-flex flex-col items-center mx-1">
        {showDots && (
          <div className="border-2 border-gray-300 rounded p-1 mb-1">
            {positions.map((row, rowIdx) => (
              <div key={rowIdx} className="flex gap-1">
                {row.map((dotNum) => (
                  <div
                    key={dotNum}
                    className={`w-3 h-3 rounded-full ${
                      dots.includes(dotNum) ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
            ))}
          </div>
        )}
        <span className="text-xs text-gray-600">{char}</span>
      </div>
    )
  }

  return (
    <div className="flex flex-wrap items-center gap-2 p-4 bg-gray-50 rounded-lg">
      {text.split('').map((char, idx) => (
        <div key={idx}>{renderCell(char)}</div>
      ))}
    </div>
  )
}
