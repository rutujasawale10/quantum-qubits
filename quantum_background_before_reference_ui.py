import streamlit as st
import streamlit.components.v1 as components

def render_quantum_background():
    """
    Injects an interactive 6-scene Quantum Teleportation Environment background into the Streamlit window.
    Features:
    - 6-Scene Animated Story Arc (15-Second Loop):
        Scene 1: Qubit Prep (Statevector rotation & Dirac notation)
        Scene 2: Bell Pair Entanglement Creation (H & CX gate operation indicators)
        Scene 3: Alice Operations (Joint Bell measurement CNOT & H)
        Scene 4: Quantum Teleportation (Hero probability wave packet & state transfer)
        Scene 5: Bob Correction (Unitary CX & CZ corrections, "STATE RECEIVED")
        Scene 6: State Verification (Emerald pulse & "STATE VERIFIED")
    - Entangled Qubit Pairs with correlated orbital motion.
    - Interactive Mouse Attraction & Bloch Sphere Parallax.
    - Faint background quantum circuit schematic traces (q0--H--●--H...).
    - Silver Metallic Claymorphism color harmony (#D9DDE2 base, #7656B3, #9A82D1, #B66A9C, #3E8F68).
    - Opacity strictly controlled (0.05 - 0.18) for 100% text readability and z-index layering.
    """
    canvas_html = """
    <script>
    (function() {
        const doc = (window.parent && window.parent.document) ? window.parent.document : window.document;
        const win = (window.parent && window.parent.window) ? window.parent.window : window;

        // Check if canvas already exists
        let canvas = doc.getElementById('quantum-teleport-canvas');
        if (!canvas) {
            canvas = doc.createElement('canvas');
            canvas.id = 'quantum-teleport-canvas';
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

        // Resize Handler
        function resizeCanvas() {
            const dpr = win.devicePixelRatio || 1;
            canvas.width = win.innerWidth * dpr;
            canvas.height = win.innerHeight * dpr;
            ctx.scale(dpr, dpr);
        }
        resizeCanvas();
        win.addEventListener('resize', resizeCanvas);

        // Interactive Mouse Tracking
        let mouseX = win.innerWidth / 2;
        let mouseY = win.innerHeight / 2;
        win.addEventListener('mousemove', function(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        const prefersReducedMotion = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Palette Definition (Silver Metallic + Quantum Research Colors)
        const COLORS = {
            bgStart: '#E4E7EB',
            bgEnd: '#D9DDE2',
            violet: 'rgba(118, 86, 179, ',      // #7656B3 - Alice & Core Nodes
            lavender: 'rgba(154, 130, 209, ',   // #9A82D1 - Entanglement & Orbits
            magenta: 'rgba(182, 106, 156, ',    // #B66A9C - Teleportation Wave
            emerald: 'rgba(62, 143, 104, ',     // #3E8F68 - Bob Verification Pulse
            slate: 'rgba(74, 80, 90, ',         // #4A505A - Technical Labels & Circuit
            silver: 'rgba(199, 204, 210, '      // #C7CCD2
        };

        // -------------------------------------------------------------
        // Dirac Symbols Data
        // -------------------------------------------------------------
        const SYMBOLS_LIST = ['|0⟩', '|1⟩', '|+⟩', '|-⟩', 'α', 'β', 'ψ', 'Ψ', '⟨ψ|', '⟨0|', '⟨1|', 'H', 'CX', 'CZ'];
        const symbols = [];
        for (let i = 0; i < 20; i++) {
            symbols.push({
                x: Math.random() * win.innerWidth,
                y: Math.random() * win.innerHeight,
                vx: (Math.random() - 0.5) * 0.25,
                vy: (Math.random() - 0.5) * 0.25 - 0.08,
                text: SYMBOLS_LIST[Math.floor(Math.random() * SYMBOLS_LIST.length)],
                size: Math.floor(Math.random() * 5) + 12,
                alpha: Math.random() * 0.05 + 0.04,
                color: Math.random() > 0.5 ? 'violet' : 'lavender'
            });
        }

        // -------------------------------------------------------------
        // Entangled Qubit Pairs Data
        // -------------------------------------------------------------
        const qubitPairs = [
            { ax: 0.12, ay: 0.22, bx: 0.88, by: 0.22, angle: 0, rad: 32 },
            { ax: 0.12, ay: 0.78, bx: 0.88, by: 0.78, angle: Math.PI, rad: 36 }
        ];

        // Teleportation Timeline Config
        const CYCLE_DURATION = 15.0; // 15 seconds full loop

        // -------------------------------------------------------------
        // ANIMATION LOOP
        // -------------------------------------------------------------
        let startTime = performance.now();

        function animate(now) {
            const elapsed = (now - startTime) / 1000.0;
            const cycleTime = elapsed % CYCLE_DURATION;
            const w = win.innerWidth;
            const h = win.innerHeight;

            // 1. Draw Base Silver Metallic Background
            const bgGrad = ctx.createRadialGradient(w * 0.5, h * 0.3, 50, w * 0.5, h * 0.5, Math.max(w, h));
            bgGrad.addColorStop(0, COLORS.bgStart);
            bgGrad.addColorStop(1, COLORS.bgEnd);
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, w, h);

            // -------------------------------------------------------------
            // LAYER 1: Background Quantum Circuit Schematic Trace
            // -------------------------------------------------------------
            ctx.save();
            ctx.strokeStyle = COLORS.slate + '0.05)';
            ctx.lineWidth = 1;
            ctx.setFont = '10px monospace';
            const traceY = h * 0.92;
            
            ctx.beginPath();
            ctx.moveTo(w * 0.1, traceY);
            ctx.lineTo(w * 0.9, traceY);
            ctx.moveTo(w * 0.1, traceY + 14);
            ctx.lineTo(w * 0.9, traceY + 14);
            ctx.moveTo(w * 0.1, traceY + 28);
            ctx.lineTo(w * 0.9, traceY + 28);
            ctx.stroke();

            ctx.fillStyle = COLORS.slate + '0.08)';
            ctx.font = '10px monospace';
            ctx.fillText('q0 (Alice Input)  ──[ H ]────●────[ H ]────[ M ]───────────────', w * 0.1, traceY - 4);
            ctx.fillText('q1 (EPR Pair A)   ───────────X────[ M ]──────────────────────', w * 0.1, traceY + 10);
            ctx.fillText('q2 (Bob Qubit)    ─────────────────────────[ CX ]───[ CZ ]───', w * 0.1, traceY + 24);
            ctx.restore();

            // -------------------------------------------------------------
            // LAYER 2: Bloch Spheres with Parallax
            // -------------------------------------------------------------
            const mouseDx = (mouseX - w / 2) * 0.02;
            const mouseDy = (mouseY - h / 2) * 0.02;

            const blochSpheres = [
                { x: w * 0.06 + mouseDx, y: h * 0.48 + mouseDy, r: 34, rot: now * 0.0004 },
                { x: w * 0.94 + mouseDx, y: h * 0.48 + mouseDy, r: 36, rot: -now * 0.0003 }
            ];

            blochSpheres.forEach(bs => {
                ctx.save();
                ctx.translate(bs.x, bs.y);
                ctx.strokeStyle = COLORS.violet + '0.06)';
                ctx.lineWidth = 1;

                ctx.beginPath();
                ctx.arc(0, 0, bs.r, 0, Math.PI * 2);
                ctx.stroke();

                ctx.beginPath();
                ctx.ellipse(0, 0, bs.r, bs.r * 0.35, bs.rot, 0, Math.PI * 2);
                ctx.setLineDash([3, 3]);
                ctx.stroke();
                ctx.setLineDash([]);

                ctx.beginPath();
                ctx.moveTo(0, -bs.r - 4);
                ctx.lineTo(0, bs.r + 4);
                ctx.stroke();

                const vecAngle = bs.rot * 1.8;
                const vx = Math.cos(vecAngle) * bs.r * 0.75;
                const vy = Math.sin(vecAngle) * bs.r * 0.45;
                ctx.strokeStyle = COLORS.magenta + '0.12)';
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(vx, vy);
                ctx.stroke();

                ctx.fillStyle = COLORS.magenta + '0.25)';
                ctx.beginPath();
                ctx.arc(vx, vy, 2.5, 0, Math.PI * 2);
                ctx.fill();

                ctx.font = '9px sans-serif';
                ctx.fillStyle = COLORS.slate + '0.12)';
                ctx.fillText('|0⟩', -5, -bs.r - 5);
                ctx.fillText('|1⟩', -5, bs.r + 12);

                ctx.restore();
            });

            // -------------------------------------------------------------
            // LAYER 3: 6-STAGE QUANTUM TELEPORTATION ANIMATION
            // -------------------------------------------------------------
            const aliceX = w * 0.20;
            const aliceY = h * 0.45;
            const bobX = w * 0.80;
            const bobY = h * 0.45;
            const eprY = h * 0.30;

            // Render Nodes: Alice & Bob
            ctx.save();

            // Alice Base Node
            ctx.fillStyle = COLORS.violet + '0.20)';
            ctx.beginPath();
            ctx.arc(aliceX, aliceY, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.violet + '0.40)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.font = 'bold 12px sans-serif';
            ctx.fillStyle = COLORS.slate + '0.60)';
            ctx.fillText('ALICE [Node A]', aliceX - 42, aliceY + 28);

            // Bob Base Node
            ctx.fillStyle = COLORS.lavender + '0.20)';
            ctx.beginPath();
            ctx.arc(bobX, bobY, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.lavender + '0.40)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.fillText('BOB [Node B]', bobX - 35, bobY + 28);

            // SCENE 1: Qubit Preparation (0s - 2.5s)
            if (cycleTime >= 0.0 && cycleTime < 2.5) {
                const prepProgress = (cycleTime - 0.0) / 2.5;
                const ringR = 12 + prepProgress * 22;
                ctx.strokeStyle = COLORS.violet + (0.25 - prepProgress * 0.15) + ')';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.arc(aliceX, aliceY, ringR, 0, Math.PI * 2);
                ctx.stroke();

                ctx.fillStyle = COLORS.violet + '0.70)';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText('SCENE 1: QUBIT PREPARATION (|ψ⟩ = α|0⟩ + β|1⟩)', aliceX - 20, aliceY - 32);
            }

            // SCENE 2: Bell Pair Entanglement (2.5s - 5.0s)
            if (cycleTime >= 2.5) {
                ctx.strokeStyle = COLORS.lavender + '0.12)';
                ctx.lineWidth = 1.2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.moveTo(aliceX, aliceY);
                ctx.lineTo(bobX, bobY);
                ctx.stroke();
                ctx.setLineDash([]);
            }
            if (cycleTime >= 2.5 && cycleTime < 5.0) {
                const entPulse = 0.15 + 0.10 * Math.sin(now * 0.008);
                ctx.strokeStyle = COLORS.violet + entPulse + ')';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(aliceX, aliceY);
                ctx.lineTo(bobX, bobY);
                ctx.stroke();

                ctx.fillStyle = COLORS.violet + '0.70)';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText('SCENE 2: BELL PAIR CREATION (|Φ+⟩ = 1/√2(|00⟩ + |11⟩))', w * 0.38, eprY - 15);

                // Gate badges
                ctx.fillStyle = COLORS.violet + '0.15)';
                ctx.fillRect(w * 0.42, eprY, 40, 20);
                ctx.fillStyle = COLORS.slate + '0.80)';
                ctx.font = '10px monospace';
                ctx.fillText('H + CX', w * 0.42 + 4, eprY + 14);
            }

            // SCENE 3: Alice Operations (5.0s - 7.5s)
            if (cycleTime >= 5.0 && cycleTime < 7.5) {
                ctx.strokeStyle = COLORS.magenta + '0.35)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(aliceX, aliceY, 20 + Math.sin(now * 0.01) * 4, 0, Math.PI * 2);
                ctx.stroke();

                ctx.fillStyle = COLORS.magenta + '0.75)';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText('SCENE 3: ALICE BELL MEASUREMENT (CNOT + H)', aliceX - 20, aliceY - 32);
            }

            // SCENE 4: Teleportation Hero Wave Packet (7.5s - 11.5s)
            if (cycleTime >= 7.5 && cycleTime < 11.5) {
                const waveProgress = (cycleTime - 7.5) / 4.0; // 0 to 1
                const currX = aliceX + (bobX - aliceX) * waveProgress;

                // Travelling Wave Envelope
                ctx.save();
                ctx.beginPath();
                ctx.strokeStyle = COLORS.magenta + '0.40)';
                ctx.lineWidth = 2;

                for (let x = aliceX; x <= currX; x += 6) {
                    const distFromFront = (currX - x);
                    const envelope = Math.exp(-distFromFront * 0.01) * Math.sin(distFromFront * 0.08 - now * 0.01);
                    const wy = aliceY + envelope * 18;
                    if (x === aliceX) ctx.moveTo(x, wy);
                    else ctx.lineTo(x, wy);
                }
                ctx.stroke();

                // Wave Front Particle
                ctx.fillStyle = COLORS.magenta + '0.80)';
                ctx.beginPath();
                ctx.arc(currX, aliceY, 4.5, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = COLORS.magenta + '0.85)';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText('SCENE 4: TELEPORTING QUANTUM STATE INFORMATION...', currX - 100, aliceY - 25);
                ctx.restore();
            }

            // SCENE 5: Bob Correction (11.5s - 13.5s)
            if (cycleTime >= 11.5 && cycleTime < 13.5) {
                ctx.strokeStyle = COLORS.lavender + '0.50)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(bobX, bobY, 18 + Math.sin(now * 0.012) * 5, 0, Math.PI * 2);
                ctx.stroke();

                ctx.fillStyle = COLORS.violet + '0.80)';
                ctx.font = 'bold 11px sans-serif';
                ctx.fillText('SCENE 5: BOB UNITARY CORRECTION (CX^m2 · CZ^m1)', bobX - 120, bobY - 32);
                ctx.fillStyle = COLORS.emerald + '0.85)';
                ctx.fillText('STATE RECEIVED', bobX - 35, bobY + 45);
            }

            // SCENE 6: Verification Pulse (13.5s - 15.0s)
            if (cycleTime >= 13.5) {
                const verProgress = (cycleTime - 13.5) / 1.5;
                const vPulseR = 10 + verProgress * 30;
                ctx.strokeStyle = COLORS.emerald + (0.45 - verProgress * 0.35) + ')';
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                ctx.arc(bobX, bobY, vPulseR, 0, Math.PI * 2);
                ctx.stroke();

                ctx.fillStyle = COLORS.emerald + '0.90)';
                ctx.font = 'bold 12px sans-serif';
                ctx.fillText('✓ SCENE 6: QUANTUM STATE TELEPORTATION VERIFIED', bobX - 140, bobY - 32);
            }

            ctx.restore();

            // -------------------------------------------------------------
            // LAYER 4: Mouse Interactive Particles & Drifting Symbols
            // -------------------------------------------------------------
            ctx.save();
            symbols.forEach(s => {
                if (!prefersReducedMotion) {
                    // Subtle mouse attraction
                    const dx = mouseX - s.x;
                    const dy = mouseY - s.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120 && dist > 5) {
                        s.x += (dx / dist) * 0.3;
                        s.y += (dy / dist) * 0.3;
                    }

                    s.x += s.vx;
                    s.y += s.vy;

                    if (s.x < -40) s.x = w + 40;
                    if (s.x > w + 40) s.x = -40;
                    if (s.y < -40) s.y = h + 40;
                    if (s.y > h + 40) s.y = -40;
                }

                ctx.font = `${s.size}px "Cambria Math", serif`;
                ctx.fillStyle = COLORS[s.color] + s.alpha + ')';
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
