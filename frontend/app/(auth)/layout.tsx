// app/(auth)/layout.tsx
// Fills the space under the navbar (h-16 = 4rem) so the site footer stays
// below the fold, vertically centers the form, and gives the empty space an
// intentional backdrop. Server component — no hooks, no "use client".

export default function AuthLayout({
    children,
  }: {
    children: React.ReactNode
  }) {
    return (
      <div className="relative flex min-h-[calc(100dvh-4rem)] items-center justify-center overflow-hidden px-4 py-10">
        {/* soft brand glow */}
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-1/2 h-[42rem] w-[42rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-500/10 blur-[130px]" />
        </div>
  
        {/* faint dot grid, faded toward the edges */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10 opacity-40"
          style={{
            backgroundImage:
              "radial-gradient(circle, rgba(128,128,128,0.15) 1px, transparent 1px)",
            backgroundSize: "22px 22px",
            maskImage: "radial-gradient(ellipse at center, black, transparent 70%)",
            WebkitMaskImage:
              "radial-gradient(ellipse at center, black, transparent 70%)",
          }}
        />
  
        {children}
      </div>
    )
  }