export default function GeometricBG() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
      {/* Layer 1: Main diagonal gradient */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background: 'linear-gradient(135deg, #0f172a, #1e3a8a, #22d3ee)',
          clipPath: 'polygon(0 0, 100% 0, 50% 100%)',
        }}
      ></div>

      {/* Layer 2: Second gradient polygon for depth */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background: 'linear-gradient(225deg, #1e3a8a, #22d3ee, #0f172a)',
          clipPath: 'polygon(0 100%, 100% 0, 100% 100%)',
        }}
      ></div>

      {/* Optional: subtle radial glow */}
      <div
        className="absolute inset-0 w-full h-full"
        style={{
          background: 'radial-gradient(circle at center, rgba(34, 211, 238, 0.1), transparent 70%)',
        }}
      ></div>
    </div>
  );
}