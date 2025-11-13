import { Palette, Type, Layout } from 'lucide-react';

export function DesignSystemReference() {
  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: '#121212' }}>
      <div className="max-w-6xl mx-auto">
        <h1 className="mb-2" style={{ color: '#F47A20' }}>
          UTEP Design System
        </h1>
        <p className="mb-8" style={{ color: '#B0B0B0' }}>
          A comprehensive dark-mode design system for the UTEP Professor Dashboard
        </p>

        {/* Color Palette */}
        <div
          className="rounded-lg border p-6 mb-8"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#2A2A2A',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Palette className="w-6 h-6" style={{ color: '#F47A20' }} />
            <h2 style={{ color: '#EAEAEA' }}>Color Tokens</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Primary Colors */}
            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Primary Colors
              </h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#F47A20', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>UTEP Orange</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#F47A20</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#002D62', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>UTEP Navy</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#002D62</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#0066CC', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Accent Blue</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#0066CC</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Background Colors */}
            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Background Colors
              </h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded border"
                    style={{ 
                      backgroundColor: '#121212', 
                      borderRadius: '8px',
                      borderColor: '#2A2A2A'
                    }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Background</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#121212</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#1E1E1E', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Card Background</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#1E1E1E</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#2A2A2A', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Border</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#2A2A2A</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Text & Chart Colors */}
            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Text & Charts
              </h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#EAEAEA', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Text Primary</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#EAEAEA</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#B0B0B0', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Text Secondary</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#B0B0B0</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div
                    className="w-16 h-16 rounded"
                    style={{ backgroundColor: '#FFB84D', borderRadius: '8px' }}
                  ></div>
                  <div>
                    <div style={{ color: '#EAEAEA', fontSize: '14px' }}>Chart Accent</div>
                    <div style={{ color: '#B0B0B0', fontSize: '12px' }}>#FFB84D</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Typography */}
        <div
          className="rounded-lg border p-6 mb-8"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#2A2A2A',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Type className="w-6 h-6" style={{ color: '#F47A20' }} />
            <h2 style={{ color: '#EAEAEA' }}>Typography System</h2>
          </div>

          <div className="space-y-6">
            <div>
              <div style={{ color: '#B0B0B0', fontSize: '13px', marginBottom: '8px' }}>
                H1 - Poppins Bold, 24px
              </div>
              <h1 style={{ color: '#EAEAEA' }}>UTEP Professor Dashboard</h1>
            </div>

            <div>
              <div style={{ color: '#B0B0B0', fontSize: '13px', marginBottom: '8px' }}>
                H2 - Poppins Bold, 20px
              </div>
              <h2 style={{ color: '#EAEAEA' }}>Professor Comparison</h2>
            </div>

            <div>
              <div style={{ color: '#B0B0B0', fontSize: '13px', marginBottom: '8px' }}>
                H3 - Inter Medium, 16px
              </div>
              <h3 style={{ color: '#EAEAEA' }}>AI-Generated Summary</h3>
            </div>

            <div>
              <div style={{ color: '#B0B0B0', fontSize: '13px', marginBottom: '8px' }}>
                Body - Inter Regular, 14px
              </div>
              <p style={{ color: '#EAEAEA' }}>
                This is body text used for descriptions, reviews, and general content throughout the dashboard.
              </p>
            </div>

            <div>
              <div style={{ color: '#B0B0B0', fontSize: '13px', marginBottom: '8px' }}>
                Label - Inter Medium, 12-13px
              </div>
              <label style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Overall Rating • Would Take Again
              </label>
            </div>
          </div>
        </div>

        {/* Effects */}
        <div
          className="rounded-lg border p-6"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#2A2A2A',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Layout className="w-6 h-6" style={{ color: '#F47A20' }} />
            <h2 style={{ color: '#EAEAEA' }}>Effects & Spacing</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Card Shadow
              </h4>
              <div
                className="w-full h-24 rounded-lg"
                style={{
                  backgroundColor: '#1E1E1E',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
                }}
              >
                <div className="flex items-center justify-center h-full">
                  <span style={{ color: '#B0B0B0', fontSize: '13px' }}>
                    0 2px 8px rgba(0, 0, 0, 0.15)
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Hover Glow
              </h4>
              <div
                className="w-full h-24 rounded-lg transition-all duration-300"
                style={{
                  backgroundColor: '#1E1E1E',
                  borderRadius: '8px',
                  border: '1px solid #F47A20',
                  boxShadow: '0 4px 16px rgba(244, 122, 32, 0.2)'
                }}
              >
                <div className="flex items-center justify-center h-full">
                  <span style={{ color: '#B0B0B0', fontSize: '13px' }}>
                    Orange glow on hover
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Border Radius
              </h4>
              <div className="flex gap-3">
                <div
                  className="flex-1 h-16"
                  style={{
                    backgroundColor: '#0066CC',
                    borderRadius: '8px'
                  }}
                >
                  <div className="flex items-center justify-center h-full">
                    <span style={{ color: '#FFFFFF', fontSize: '12px' }}>8px</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="mb-3" style={{ color: '#B0B0B0', fontSize: '13px' }}>
                Spacing Scale
              </h4>
              <div className="space-y-2">
                <div style={{ color: '#EAEAEA', fontSize: '13px' }}>• 4px - Tight spacing</div>
                <div style={{ color: '#EAEAEA', fontSize: '13px' }}>• 8px - Default spacing</div>
                <div style={{ color: '#EAEAEA', fontSize: '13px' }}>• 16px - Section spacing</div>
                <div style={{ color: '#EAEAEA', fontSize: '13px' }}>• 24px - Component gaps</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
