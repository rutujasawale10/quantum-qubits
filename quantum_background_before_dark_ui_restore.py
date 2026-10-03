import streamlit as st
import streamlit.components.v1 as components

def render_quantum_background():
    """
    Injects a dark WebGL/Canvas 2D animated Quantum Command Center background into the Streamlit window.
    Features:
    - Base Dark Navy Canvas (#0B0E17).
    - Glowing Qubit Orbit System & Particle Clouds (#A855F7, #EC4899, #06B6D4).
    - Floating Dirac State Symbols (|0⟩, |1⟩, |+⟩, |-⟩, α, β, ψ, Ψ, ⟨ψ|).
    - Pulsing Quantum Entanglement Connection Lines.
    - Low opacity overlays (0.05 - 0.15) recessed behind UI panels (z-index: 0).
    """
    canvas_html = """
    <script>
    (function() {
        const doc = (window.parent && window.parent.document) ? window.parent.document : window.document;
        const win = (window.parent && window.parent.window) ? window.parent.window : window;

        let canvas = doc.getElementById('quantum-command-canvas');
        if (!canvas) {
            canvas = doc.createElement('canvas');
            canvas.id = 'quantum-command-canvas';
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100vw';
            canvas.style.height = '100vh';
            canvas.style.zIndex = '0';
            canvas.style.pointerEvents = 'none';
            
            const targetContainer = doc.querySelector('.stApp') || doc.body;
            targetContainer.insertBefore(canvas, targetContainer.firstChild);
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        function resizeCanvas() {
            const dpr = win.devicePixelRatio || 1;
            canvas.width = win.innerWidth * dpr;
            canvas.height = win.innerHeight * dpr;
            ctx.scale(dpr, dpr);
        }
        resizeCanvas();
        win.addEventListener('resize', resizeCanvas);

        let mouseX = win.innerWidth / 2;
        let mouseY = win.innerHeight / 2;
        win.addEventListener('mousemove', function(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        const prefersReducedMotion = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Dark Palette
        const COLORS = {
            bg: '#0B0E17',
            purple: 'rgba(168, 85, 247, ',
            violet: 'rgba(139, 92, 246, ',
            magenta: 'rgba(236, 72, 153, ',
            cyan: 'rgba(6, 182, 212, ',
            emerald: 'rgba(16, 185, 129, '
        };

        // Particles Data
        const particles = [];
        const numParticles = 40;
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * win.innerWidth,
                y: Math.random() * win.innerHeight,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                r: Math.random() * 2 + 1,
                alpha: Math.random() * 0.15 + 0.05,
                color: Math.random() > 0.4 ? 'purple' : (Math.random() > 0.5 ? 'magenta' : 'cyan')
            });
        }

        // Dirac Symbols Data
        const SYMBOLS_LIST = ['|0⟩', '|1⟩', '|+⟩', '|-⟩', 'α', 'β', 'ψ', 'Ψ', '⟨ψ|', 'H', 'CX', 'CZ'];
        const symbols = [];
        for (let i = 0; i < 16; i++) {
            symbols.push({
                x: Math.random() * win.innerWidth,
                y: Math.random() * win.innerHeight,
                vx: (Math.random() - 0.5) * 0.2,
                vy: (Math.random() - 0.5) * 0.2,
                text: SYMBOLS_LIST[Math.floor(Math.random() * SYMBOLS_LIST.length)],
                size: Math.floor(Math.random() * 4) + 12,
                alpha: Math.random() * 0.08 + 0.04
            });
        }

        // Animation Loop
        function animate(now) {
            const w = win.innerWidth;
            const h = win.innerHeight;

            // 1. Draw Base Dark Navy Fill
            ctx.fillStyle = COLORS.bg;
            ctx.fillRect(0, 0, w, h);

            // 2. Draw Subtle Probability Wave
            ctx.save();
            ctx.lineWidth = 1;
            ctx.strokeStyle = COLORS.purple + '0.06)';
            ctx.beginPath();
            const waveY = h * 0.90;
            for (let x = 0; x < w; x += 15) {
                const y = waveY + Math.sin(x * 0.005 + now * 0.001) * 12;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            ctx.restore();

            // 3. Draw Particles & Entanglement Lines
            ctx.save();
            particles.forEach((p, idx) => {
                if (!prefersReducedMotion) {
                    p.x += p.vx;
                    p.y += p.vy;

                    if (p.x < 0) p.x = w;
                    if (p.x > w) p.x = 0;
                    if (p.y < 0) p.y = h;
                    if (p.y > h) p.y = 0;
                }

                ctx.fillStyle = COLORS[p.color] + p.alpha + ')';
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fill();

                // Connect nearby particles
                for (let j = idx + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 100) {
                        const lineAlpha = (1 - dist / 100) * 0.06;
                        ctx.strokeStyle = COLORS.violet + lineAlpha + ')';
                        ctx.lineWidth = 0.8;
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            });
            ctx.restore();

            // 4. Draw Drifting Dirac Symbols
            ctx.save();
            symbols.forEach(s => {
                if (!prefersReducedMotion) {
                    s.x += s.vx;
                    s.y += s.vy;
                    if (s.x < 0) s.x = w;
                    if (s.x > w) s.x = 0;
                    if (s.y < 0) s.y = h;
                    if (s.y > h) s.y = 0;
                }

                ctx.font = `${s.size}px "Cambria Math", serif`;
                ctx.fillStyle = COLORS.purple + s.alpha + ')';
                ctx.fillText(s.text, s.x, s.y);
            });
            ctx.restore();

            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    })();
    </script>
    """
    components.html(canvas_html, height=0, width=0)
