/* ==========================================================================
   SIH26141 QUANTUM-QDS — SOC DASHBOARD JAVASCRIPT
   Auto-Run Real Qiskit Simulation & Full Interactive Threat Detection
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

    // -----------------------------------------------------------------------
    // APPLICATION STATE
    // -----------------------------------------------------------------------
    let selectedState    = "+";
    let selectedAttack   = "CHANNEL";
    let selectedVerifier = "Bob";
    let channelGate      = "Z";
    const API_BASE       = "";
    let simStartTime     = null;
    let isSimRunning     = false;
    let autoRunExecuted  = false;
    const recentResults  = [];
    const loadedTabs     = new Set();

    // -----------------------------------------------------------------------
    // QUANTUM STATE DEFINITIONS
    // -----------------------------------------------------------------------
    const STATE_INFO = {
        "0": { label: "|0⟩", basis: "Z", basisLabel: "Z-BASIS", desc: "Z-basis eigenstate" },
        "1": { label: "|1⟩", basis: "Z", basisLabel: "Z-BASIS", desc: "Z-basis eigenstate" },
        "+": { label: "|+⟩", basis: "X", basisLabel: "X-BASIS", desc: "X-basis eigenstate" },
        "-": { label: "|−⟩", basis: "X", basisLabel: "X-BASIS", desc: "X-basis eigenstate" }
    };

    const sleep = (ms) => new Promise(r => setTimeout(r, ms));

    // -----------------------------------------------------------------------
    // DOM REFERENCES
    // -----------------------------------------------------------------------
    const shotsSlider        = document.getElementById("shots-slider");
    const shotsValDisplay    = document.getElementById("shots-val-display");
    const errorThreshSlider  = document.getElementById("error-thresh-slider");
    const errorThreshDisplay = document.getElementById("error-thresh-display");
    const chiThreshSlider    = document.getElementById("chi-thresh-slider");
    const chiThreshDisplay   = document.getElementById("chi-thresh-display");
    const runVerifyBtn       = document.getElementById("run-verify-btn");
    const resetReplayBtn     = document.getElementById("reset-replay-btn");
    const channelGateGroup   = document.getElementById("channel-gate-group");

    // Hero Nodes & Packets
    const nodeAlice     = document.getElementById("node-alice");
    const nodeEve       = document.getElementById("node-eve");
    const nodeBob       = document.getElementById("node-bob");
    const packetAliceEve= document.getElementById("packet-alice-eve");
    const packetEveBob  = document.getElementById("packet-eve-bob");
    const packetState1  = document.getElementById("packet-state-1");
    const packetState2  = document.getElementById("packet-state-2");
    const simSubtitleAttack = document.getElementById("sim-subtitle-attack");
    const simTimer      = document.getElementById("sim-timer");

    // Quantum State HUD
    const qsDisplay     = document.getElementById("qs-display");
    const qsDesc        = document.getElementById("qs-desc");
    const qsStateFrom   = document.getElementById("qs-state-from");
    const qsTransformOp = document.getElementById("qs-transform-op");
    const qsStateTo     = document.getElementById("qs-state-to");
    const qsExpectedVal = document.getElementById("qs-expected-val");
    const qsActualVal   = document.getElementById("qs-actual-val");

    // Pipeline Stages
    const bobStepBasis  = document.getElementById("bob-step-basis");
    const bobStepMeas   = document.getElementById("bob-step-meas");
    const bobStepCounts = document.getElementById("bob-step-counts");
    const bobStepError  = document.getElementById("bob-step-error");
    const bobStepChi    = document.getElementById("bob-step-chi");
    const bobStepVerdict= document.getElementById("bob-step-verdict");

    const bobValBasis   = document.getElementById("bob-val-basis");
    const pipMeasShots  = document.getElementById("pip-meas-shots");
    const bobValCounts  = document.getElementById("bob-val-counts");
    const bobValError   = document.getElementById("bob-val-error");
    const bobValChi     = document.getElementById("bob-val-chi");
    const bobValVerdict = document.getElementById("bob-val-verdict");

    // Verdict Card
    const statusBanner    = document.getElementById("status-banner");
    const statusTitle     = document.getElementById("status-title");
    const statusSubtitle  = document.getElementById("status-subtitle");

    // Metric Cards
    const metricErrorRate  = document.getElementById("metric-error-rate");
    const metricErrorThresh= document.getElementById("metric-error-thresh");
    const metricChiSquare  = document.getElementById("metric-chi-square");
    const metricChiThresh  = document.getElementById("metric-chi-thresh");
    const secTpr           = document.getElementById("sec-tpr");
    const secFnr           = document.getElementById("sec-fnr");
    const secFpr           = document.getElementById("sec-fpr");
    const secTnr           = document.getElementById("sec-tnr");

    // Timeline & Lower Tabs
    const eventTimeline   = document.getElementById("event-timeline");
    const e2eTableBody    = document.querySelector("#e2e-table tbody");
    const secAnalysisBody = document.getElementById("sec-analysis-body");
    const perfContainer   = document.getElementById("perf-results-container");
    const researchBody    = document.getElementById("research-compliance-body");

    // -----------------------------------------------------------------------
    // 1. BACKGROUND PARTICLE CANVAS (Quantum Constellation)
    // -----------------------------------------------------------------------
    const initParticleCanvas = () => {
        const canvas = document.getElementById("quantum-bg-canvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const particles = [];
        const numParticles = Math.min(Math.floor((width * height) / 28000), 50);

        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.35,
                vy: (Math.random() - 0.5) * 0.35,
                radius: Math.random() * 1.5 + 0.8,
                color: Math.random() > 0.4 ? "#38bdf8" : (Math.random() > 0.5 ? "#818cf8" : "#0284c7")
            });
        }

        const render = () => {
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(56, 189, 248, ${0.12 * (1 - dist / 120)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }

            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = width;
                if (p.x > width) p.x = 0;
                if (p.y < 0) p.y = height;
                if (p.y > height) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
            });

            requestAnimationFrame(render);
        };

        render();
    };

    initParticleCanvas();

    // -----------------------------------------------------------------------
    // 2. SIDEBAR NAVIGATION
    // -----------------------------------------------------------------------
    document.querySelectorAll(".sb-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            document.querySelectorAll(".sb-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            const sbMap = {
                "dashboard":   null,
                "e2e":         "lt-e2e",
                "security":    "lt-security",
                "performance": "lt-performance",
                "compliance":  "lt-research"
            };

            const ltTarget = sbMap[item.dataset.sb];
            if (ltTarget) {
                const lowerBtn = document.querySelector(`.pill-tab-btn[data-lt="${ltTarget}"]`);
                if (lowerBtn) lowerBtn.click();
            }
        });
    });

    // -----------------------------------------------------------------------
    // 3. STATE BUTTON SELECTION
    // -----------------------------------------------------------------------
    document.querySelectorAll(".state-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".state-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedState = btn.dataset.state;
            updateQuantumStateHUD();
        });
    });

    // -----------------------------------------------------------------------
    // 4. ATTACK SELECTOR CARDS
    // -----------------------------------------------------------------------
    document.querySelectorAll(".atk-btn-card").forEach(card => {
        card.addEventListener("click", () => {
            document.querySelectorAll(".atk-btn-card").forEach(c => {
                c.classList.remove("active");
                c.classList.remove("active-card-red");
                const t = c.querySelector(".atk-title");
                if (t) t.classList.remove("text-red");
                const s = c.querySelector(".atk-sub");
                if (s) s.classList.remove("text-red-sub");
            });

            card.classList.add("active");
            selectedAttack = card.dataset.attack;

            if (selectedAttack === "CHANNEL") {
                card.classList.add("active-card-red");
                const t = card.querySelector(".atk-title");
                if (t) t.classList.add("text-red");
                const s = card.querySelector(".atk-sub");
                if (s) s.classList.add("text-red-sub");
                if (channelGateGroup) channelGateGroup.classList.remove("hidden");
            } else if (selectedAttack === "FORGERY") {
                card.classList.add("active-card-red");
                if (channelGateGroup) channelGateGroup.classList.add("hidden");
            } else {
                if (channelGateGroup) channelGateGroup.classList.add("hidden");
            }

            updateQuantumStateHUD();
        });
    });

    // -----------------------------------------------------------------------
    // 5. AUTHORIZED VERIFIER SELECTION
    // -----------------------------------------------------------------------
    document.querySelectorAll(".ver-pill-card").forEach(card => {
        card.addEventListener("click", () => {
            document.querySelectorAll(".ver-pill-card").forEach(c => c.classList.remove("ver-active"));
            card.classList.add("ver-active");
            const radio = card.querySelector("input[type=radio]");
            if (radio) {
                radio.checked = true;
                selectedVerifier = radio.value;
            }
        });
    });

    // -----------------------------------------------------------------------
    // 6. CHANNEL GATE RADIOS
    // -----------------------------------------------------------------------
    document.querySelectorAll("input[name='channel_gate']").forEach(r => {
        r.addEventListener("change", e => {
            channelGate = e.target.value;
            updateQuantumStateHUD();
        });
    });

    // -----------------------------------------------------------------------
    // 7. SLIDER HANDLERS
    // -----------------------------------------------------------------------
    if (shotsSlider) {
        shotsSlider.addEventListener("input", e => {
            const v = e.target.value;
            if (shotsValDisplay) shotsValDisplay.textContent = v;
            if (pipMeasShots) pipMeasShots.textContent = `${v} shots`;
        });
    }

    if (errorThreshSlider) {
        errorThreshSlider.addEventListener("input", e => {
            const v = parseFloat(e.target.value).toFixed(1);
            if (errorThreshDisplay) errorThreshDisplay.textContent = `${v}%`;
            if (metricErrorThresh) metricErrorThresh.textContent = `Threshold: ${v}%`;
        });
    }

    if (chiThreshSlider) {
        chiThreshSlider.addEventListener("input", e => {
            const v = parseFloat(e.target.value).toFixed(1);
            if (chiThreshDisplay) chiThreshDisplay.textContent = v;
            if (metricChiThresh) metricChiThresh.textContent = `Threshold: ${v}`;
        });
    }

    // -----------------------------------------------------------------------
    // 8. QUANTUM STATE HUD UPDATE
    // -----------------------------------------------------------------------
    function updateQuantumStateHUD() {
        const info = STATE_INFO[selectedState] || STATE_INFO["+"];
        if (qsDisplay) qsDisplay.textContent = info.label;
        if (qsDesc)    qsDesc.textContent    = info.desc;
        if (packetState1) packetState1.textContent = info.label;

        if (bobValBasis) bobValBasis.textContent = `${info.basis}-basis`;

        const fromLabel = info.label;
        let opLabel  = "No attack";
        let toLabel  = info.label;
        let expected = info.label;
        let actual   = info.label;

        switch (selectedAttack) {
            case "NONE":
                opLabel  = "No attack";
                toLabel  = info.label;
                expected = info.label;
                actual   = info.label;
                if (simSubtitleAttack) simSubtitleAttack.textContent = "Clean Transmission";
                break;

            case "FORGERY": {
                const flip = { "0": "|1⟩", "1": "|0⟩", "+": "|−⟩", "-": "|+⟩" };
                opLabel  = "Modified";
                toLabel  = flip[selectedState] || "|?⟩";
                expected = info.label;
                actual   = toLabel;
                if (simSubtitleAttack) simSubtitleAttack.textContent = "Forgery Attack Active";
                break;
            }

            case "CHANNEL": {
                const g = channelGate;
                opLabel  = `Pauli-${g}`;
                const zFlip = { "0": "|0⟩", "1": "|1⟩", "+": "|−⟩", "-": "|+⟩" };
                const xFlip = { "0": "|1⟩", "1": "|0⟩", "+": "|+⟩", "-": "|−⟩" };
                toLabel  = (g === "Z" ? zFlip : xFlip)[selectedState] || info.label;
                expected = info.label;
                actual   = toLabel;
                if (simSubtitleAttack) simSubtitleAttack.textContent = "Simulated Attack";
                break;
            }

            case "IMPERSONATION":
                opLabel  = "Fake identity";
                toLabel  = info.label;
                expected = "Alice";
                actual   = "Attacker";
                if (simSubtitleAttack) simSubtitleAttack.textContent = "Impersonation Attack Active";
                break;

            case "REPLAY":
                opLabel  = "Reused packet";
                toLabel  = info.label;
                expected = "Fresh Hash";
                actual   = "Reused Hash";
                if (simSubtitleAttack) simSubtitleAttack.textContent = "Replay Attack Active";
                break;
        }

        if (qsStateFrom)     qsStateFrom.textContent     = fromLabel;
        if (qsTransformOp)   qsTransformOp.textContent   = opLabel;
        if (qsStateTo)       qsStateTo.textContent       = toLabel;
        if (packetState2)    packetState2.textContent    = toLabel;
        if (qsExpectedVal)   qsExpectedVal.textContent   = expected;
        if (qsActualVal)     qsActualVal.textContent     = actual;
    }

    // -----------------------------------------------------------------------
    // 9. LIVE EVENT TIMELINE
    // -----------------------------------------------------------------------
    function clearTimeline() {
        if (eventTimeline) eventTimeline.innerHTML = "";
    }

    function addTimelineEvent(icon, text, isRed = false) {
        if (!eventTimeline) return;
        const now = new Date();
        const ts  = `${String(now.getHours()).padStart(2,"0")}:${String(now.getMinutes()).padStart(2,"0")}:${String(now.getSeconds()).padStart(2,"0")}`;
        const div = document.createElement("div");
        div.className = "timeline-row";
        div.innerHTML = `
            <span>${icon}</span>
            <span class="tl-timestamp">${ts}</span>
            <span class="tl-desc ${isRed ? 'text-red' : ''}">${text}</span>
        `;
        eventTimeline.appendChild(div);
        eventTimeline.scrollTop = eventTimeline.scrollHeight;
    }

    // -----------------------------------------------------------------------
    // 10. RECENT RESULTS TABLE
    // -----------------------------------------------------------------------
    function addRecentResult(data) {
        const info = STATE_INFO[data.state || selectedState] || STATE_INFO["+"];
        let detail = "Pauli-Z channel applied";
        if (data.status === "BLOCKED") {
            detail = "Unauthorized verifier blocked";
        } else if (selectedAttack === "NONE") {
            detail = "Clean quantum signature verified";
        } else if (selectedAttack === "FORGERY") {
            detail = "State modification detected";
        } else if (selectedAttack === "IMPERSONATION") {
            detail = "Sender credential mismatch";
        } else if (selectedAttack === "REPLAY") {
            detail = data.attack_details?.replay_detected ? "Duplicate signature detected" : "First signature use verified";
        } else if (selectedAttack === "CHANNEL") {
            detail = `Pauli-${channelGate} channel applied`;
        }

        recentResults.unshift({
            state: info.label,
            attack: data.attack || selectedAttack,
            verifier: data.verifier || selectedVerifier,
            result: data.status,
            detail
        });

        if (recentResults.length > 8) recentResults.pop();
        renderRecentResults();
    }

    function renderRecentResults() {
        if (!e2eTableBody) return;
        if (!recentResults.length) {
            e2eTableBody.innerHTML = `
                <tr>
                    <td>1</td>
                    <td><strong>|+⟩</strong></td>
                    <td><span class="atk-tag-channel">CHANNEL</span></td>
                    <td>Bob</td>
                    <td><span class="res-badge-threat">THREAT</span></td>
                    <td><span class="detail-channel-text">Pauli-Z channel applied</span></td>
                </tr>
            `;
            return;
        }
        e2eTableBody.innerHTML = recentResults.map((r, i) => {
            const isThreat = r.result === "THREAT";
            const isBlocked = r.result === "BLOCKED";
            const resBadge = isThreat ? "res-badge-threat" : (isBlocked ? "res-badge-threat" : "res-badge-valid");
            return `<tr>
                <td>${i+1}</td>
                <td><strong>${r.state}</strong></td>
                <td><span class="atk-tag-channel">${r.attack}</span></td>
                <td>${r.verifier}</td>
                <td><span class="${resBadge}">${r.result}</span></td>
                <td><span class="detail-channel-text">${r.detail}</span></td>
            </tr>`;
        }).join("");
    }

    // -----------------------------------------------------------------------
    // 11. NODE STATES & PACKET MOTION HELPERS
    // -----------------------------------------------------------------------
    function setNodeActive(nodeName) {
        if (nodeAlice) {
            nodeAlice.className = "comm-node-col node-alice" + (nodeName === "Alice" ? " node-active-cyan" : " node-idle");
            const pill = nodeAlice.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = nodeName === "Alice" ? `<span class="dot-green"></span> ACTIVE` : `<span class="dot-green"></span> ONLINE`;
        }
        if (nodeEve) {
            nodeEve.className = "comm-node-col node-eve" + (nodeName === "Eve" ? " node-active-red" : " node-idle");
            const pill = nodeEve.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = nodeName === "Eve" ? `<span class="dot-red"></span> INTERCEPTED` : `<span class="dot-red"></span> ACTIVE`;
        }
        if (nodeBob) {
            nodeBob.className = "comm-node-col node-bob" + (nodeName === "Bob" ? " node-active-purple" : " node-idle");
            const pill = nodeBob.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = nodeName === "Bob" ? `<span class="dot-green"></span> VERIFYING` : `<span class="dot-green"></span> ONLINE`;
        }
    }

    function resetNodeStates() {
        if (nodeAlice) {
            nodeAlice.className = "comm-node-col node-alice node-idle";
            const pill = nodeAlice.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = `<span class="dot-green"></span> ONLINE`;
        }
        if (nodeEve) {
            nodeEve.className = "comm-node-col node-eve node-active";
            const pill = nodeEve.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = `<span class="dot-red"></span> ACTIVE`;
        }
        if (nodeBob) {
            nodeBob.className = "comm-node-col node-bob node-idle";
            const pill = nodeBob.querySelector(".node-status-pill");
            if (pill) pill.innerHTML = `<span class="dot-green"></span> ONLINE`;
        }
    }

    function resetPackets() {
        if (packetAliceEve) {
            packetAliceEve.style.transition = "none";
            packetAliceEve.style.left = "50%";
            packetAliceEve.style.opacity = "1";
        }
        if (packetEveBob) {
            packetEveBob.style.transition = "none";
            packetEveBob.style.left = "50%";
            packetEveBob.style.opacity = "1";
        }
    }

    // -----------------------------------------------------------------------
    // 12. PIPELINE STAGE CONTROLS
    // -----------------------------------------------------------------------
    function resetPipeline() {
        [bobStepBasis, bobStepMeas, bobStepCounts, bobStepError, bobStepChi, bobStepVerdict].forEach((el, idx) => {
            if (!el) return;
            el.className = "pip-stage stage-idle";
            const numEl = el.querySelector(".pip-num");
            if (numEl) numEl.textContent = String(idx + 1);
            const line = el.querySelector(".pip-line");
            if (line) line.className = "pip-line";
            const c = el.querySelector(".pip-circle");
            if (c) c.className = "pip-circle";
        });
        if (bobValBasis)   bobValBasis.textContent   = "--";
        if (pipMeasShots)  pipMeasShots.textContent  = "-- shots";
        if (bobValCounts)  bobValCounts.textContent  = "{0: 0, 1: 0}";
        if (bobValError)   bobValError.textContent   = "0.00%";
        if (bobValChi)     bobValChi.textContent     = "0.00";
        if (bobValVerdict) bobValVerdict.textContent = "Processing...";
    }

    function setStageDone(el, numText = "✓") {
        if (!el) return;
        el.className = "pip-stage stage-done";
        const c = el.querySelector(".pip-circle");
        if (c) c.className = "pip-circle pip-circle-check";
        const numEl = el.querySelector(".pip-num");
        if (numEl) numEl.textContent = numText;
        const line = el.querySelector(".pip-line");
        if (line) line.className = "pip-line line-active";
    }

    function setStageActive(el, numText = "▶") {
        if (!el) return;
        el.className = "pip-stage stage-active";
        const c = el.querySelector(".pip-circle");
        if (c) c.className = "pip-circle pip-circle-active";
        const numEl = el.querySelector(".pip-num");
        if (numEl) numEl.textContent = numText;
    }

    function resetVerdictCard() {
        if (!statusBanner) return;
        statusBanner.className = "soc-card verdict-card";
        statusBanner.style.borderColor = "rgba(56, 189, 248, 0.25)";
        statusBanner.style.boxShadow = "none";
        const iconEl = statusBanner.querySelector(".status-icon");
        if (iconEl) {
            iconEl.textContent = "⋯";
            iconEl.parentElement.style.borderColor = "rgba(56, 189, 248, 0.35)";
            iconEl.parentElement.style.boxShadow = "none";
            iconEl.style.color = "#38bdf8";
        }
        if (statusTitle) {
            statusTitle.textContent = "ANALYZING";
            statusTitle.style.color = "#38bdf8";
            statusTitle.style.textShadow = "none";
        }
        if (statusSubtitle) {
            statusSubtitle.textContent = "Quantum Verification in Progress...";
        }
    }

    function showErrorVerdict(errMsg) {
        if (!statusBanner) return;
        statusBanner.className = "soc-card verdict-card verdict-threat";
        statusBanner.style.borderColor = "#f59e0b";
        statusBanner.style.boxShadow = "0 0 20px rgba(245, 158, 11, 0.4)";
        const iconEl = statusBanner.querySelector(".status-icon");
        if (iconEl) {
            iconEl.textContent = "⚠";
            iconEl.parentElement.style.borderColor = "#f59e0b";
            iconEl.parentElement.style.boxShadow = "0 0 10px rgba(245, 158, 11, 0.4)";
            iconEl.style.color = "#f59e0b";
        }
        if (statusTitle) {
            statusTitle.textContent = "API ERROR";
            statusTitle.style.color = "#f59e0b";
            statusTitle.style.textShadow = "0 0 10px rgba(245, 158, 11, 0.4)";
        }
        if (statusSubtitle) {
            statusSubtitle.textContent = errMsg || "Server connection failed";
        }
    }

    // -----------------------------------------------------------------------
    // 13. RESET REPLAY CACHE
    // -----------------------------------------------------------------------
    if (resetReplayBtn) {
        resetReplayBtn.addEventListener("click", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/replay/reset`, { method: "POST" });
                const d   = await res.json();
                addTimelineEvent("🔄", `Replay Cache Cleared: ${d.message || "OK"}`);
            } catch (e) {
                alert(`Reset failed: ${e.message}`);
            }
        });
    }

    // -----------------------------------------------------------------------
    // 14. LOWER TABS NAVIGATION
    // -----------------------------------------------------------------------
    document.querySelectorAll(".pill-tab-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const ltId = btn.dataset.lt;

            document.querySelectorAll(".pill-tab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            document.querySelectorAll(".lower-tab-pane").forEach(c => c.classList.add("hidden"));
            const pane = document.getElementById(ltId);
            if (pane) pane.classList.remove("hidden");

            const ltToSb = { "lt-e2e":"e2e", "lt-security":"security", "lt-performance":"performance", "lt-research":"compliance" };
            const sbId = ltToSb[ltId];
            if (sbId) {
                document.querySelectorAll(".sb-item").forEach(i => i.classList.remove("active"));
                const sbEl = document.querySelector(`.sb-item[data-sb="${sbId}"]`);
                if (sbEl) sbEl.classList.add("active");
            }

            if (loadedTabs.has(ltId)) return;
            loadedTabs.add(ltId);

            try {
                if (ltId === "lt-e2e") {
                    const res  = await fetch(`${API_BASE}/api/end-to-end?shots=1000`);
                    const data = await res.json();
                    const results = data.matrix || data.scenarios || data.results || data;
                    if (Array.isArray(results) && e2eTableBody) {
                        e2eTableBody.innerHTML = results.map((sc, idx) => {
                            const atkRaw = sc.attack || "NONE";
                            const resRaw = sc.actual_decision || sc.observed || "VALID";
                            const resCls = resRaw === "VALID" ? "res-badge-valid" : "res-badge-threat";
                            return `<tr>
                                <td>${idx+1}</td>
                                <td><strong>|${sc.state||"0"}⟩</strong></td>
                                <td><span class="atk-tag-channel">${atkRaw}</span></td>
                                <td>${sc.verifier||"Bob"}</td>
                                <td><span class="${resCls}">${resRaw}</span></td>
                                <td><span class="detail-channel-text">${sc.scenario_name || sc.name || "Automated Matrix Verification"}</span></td>
                            </tr>`;
                        }).join("");
                    }
                }
                else if (ltId === "lt-security") {
                    const res  = await fetch(`${API_BASE}/api/security-analysis?shots=1000`);
                    const data = await res.json();
                    const m = data.metrics_summary || data.consolidated_metrics || {};
                    const val = (v1, v2) => v1 != null ? v1.toFixed(1) : (v2 != null ? v2.toFixed(1) : "100.0");
                    if (secTpr) secTpr.textContent = `${val(m.TPR, m.tpr_percent)}%`;
                    if (secTnr) secTnr.textContent = `${val(m.TNR, m.tnr_percent)}%`;
                    if (secFpr) secFpr.textContent = `${val(m.FPR, m.fpr_percent)}%`;
                    if (secFnr) secFnr.textContent = `${val(m.FNR, m.fnr_percent)}%`;
                    if (secAnalysisBody) secAnalysisBody.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                }
                else if (ltId === "lt-performance") {
                    const res  = await fetch(`${API_BASE}/api/performance?attempts=50&shots=1000`);
                    const data = await res.json();
                    if (perfContainer) perfContainer.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                }
                else if (ltId === "lt-research") {
                    const res  = await fetch(`${API_BASE}/api/research-evaluation?shots=1000`);
                    const data = await res.json();
                    if (researchBody) researchBody.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                }
            } catch (err) {
                console.error(`Tab ${ltId} load error:`, err);
            }
        });
    });

    // -----------------------------------------------------------------------
    // 15. FULL VISUAL COMMUNICATION & VERIFICATION FLOW
    // -----------------------------------------------------------------------
    async function animateFullSimulationFlow(apiPromise, payload) {
        const info = STATE_INFO[payload.state] || STATE_INFO["+"];

        // 0-300 ms: Alice becomes ACTIVE
        setNodeActive("Alice");
        addTimelineEvent("👤", `Alice initialized quantum session (Sender Active)`);
        await sleep(500);

        // ~800 ms: Alice Prepares Quantum State
        if (packetAliceEve) {
            packetAliceEve.style.transition = "none";
            packetAliceEve.style.left = "15%";
            packetAliceEve.style.opacity = "1";
        }
        if (packetState1) packetState1.textContent = info.label;
        addTimelineEvent("👤", `Alice prepared state ${info.label} (${info.desc})`);
        await sleep(400);

        // ~1200 ms: Packet visibly travels Alice -> Eve
        addTimelineEvent("🔵", `Quantum packet transmitting via channel (Alice → Eve)`);
        if (packetAliceEve) {
            packetAliceEve.style.transition = "left 1.0s cubic-bezier(0.25, 0.1, 0.25, 1)";
            packetAliceEve.style.left = "85%";
        }
        await sleep(1000);

        // ~2200 ms: Eve Intercepts & becomes ACTIVE
        setNodeActive("Eve");
        addTimelineEvent("🕵️", `Eve intercepted quantum packet`);
        await sleep(400);

        // Wait for actual backend API response
        const data = await apiPromise;

        const isBlocked     = (data.status === "BLOCKED");
        const attackType    = data.attack || payload.attack;
        const inputState    = data.state || payload.state;
        const receivedState = data.attack_details ? (data.attack_details.received_state || inputState) : inputState;

        if (isBlocked) {
            addTimelineEvent("🔴", `Unauthorized verifier '${data.verifier}' blocked`, true);
            await sleep(400);
            return data;
        }

        // ~2600 ms: Show Attack State Transformation
        if (attackType === "NONE") {
            addTimelineEvent("🔵", `Clean channel: No attack applied`);
        } else if (attackType === "FORGERY") {
            addTimelineEvent("🔴", `State modified (${info.label} → |${receivedState}⟩)`, true);
        } else if (attackType === "CHANNEL") {
            addTimelineEvent("🔴", `Pauli-${channelGate} applied (${info.label} → |${receivedState}⟩)`, true);
        } else if (attackType === "IMPERSONATION") {
            addTimelineEvent("🔴", `Identity spoofing: Attacker impersonated Alice`, true);
        } else if (attackType === "REPLAY") {
            const isRep = data.attack_details?.replay_detected;
            addTimelineEvent(isRep ? "🔴" : "🔵", isRep ? "Replay attack detected (duplicate signature hash)" : "First signature use (registered to session)", isRep);
        }

        updateQuantumStateHUD();

        // Setup Packet 2 at Eve
        if (packetEveBob) {
            packetEveBob.style.transition = "none";
            packetEveBob.style.left = "15%";
            packetEveBob.style.opacity = "1";
        }
        if (packetState2) packetState2.textContent = `|${receivedState}⟩`;
        await sleep(600);

        // ~3200 ms: Packet visibly travels Eve -> Bob
        addTimelineEvent("🔵", `Forwarding quantum packet to Bob (Eve → Bob)`);
        if (packetEveBob) {
            packetEveBob.style.transition = "left 1.0s cubic-bezier(0.25, 0.1, 0.25, 1)";
            packetEveBob.style.left = "85%";
        }
        await sleep(1000);

        // ~4200 ms: Bob becomes ACTIVE
        setNodeActive("Bob");
        addTimelineEvent("👤", `Bob received state |${receivedState}⟩ (Authorized Receiver Active)`);
        await sleep(300);

        return data;
    }

    async function animateVerificationStages(data) {
        if (data.status === "BLOCKED") {
            setStageDone(bobStepBasis, "✗");
            if (bobValBasis) bobValBasis.textContent = "BLOCKED";
            if (bobValVerdict) bobValVerdict.textContent = "BLOCKED";
            setStageDone(bobStepVerdict, "!");
            return;
        }

        // Stage 1: Basis Selection (~480ms)
        setStageDone(bobStepBasis, "✓");
        if (bobValBasis) bobValBasis.textContent = `${data.basis}-basis`;
        addTimelineEvent("🔵", `Step 1/6: Basis Selection — ${data.basis}-basis measurement basis configured`);
        await sleep(480);

        // Stage 2: Quantum Measurement (~480ms)
        setStageActive(bobStepMeas, "2");
        if (pipMeasShots) pipMeasShots.textContent = `${data.shots} shots`;
        addTimelineEvent("🔵", `Step 2/6: Quantum Measurement — ${data.shots} shots executed on Qiskit`);
        await sleep(480);

        // Stage 3: Measurement Counts (~480ms)
        const counts = data.measurement_counts || {};
        const c0 = counts[0] != null ? counts[0] : (counts["0"] || 0);
        const c1 = counts[1] != null ? counts[1] : (counts["1"] || 0);
        if (bobValCounts) bobValCounts.textContent = `{0: ${c0}, 1: ${c1}}`;
        setStageDone(bobStepCounts, "3");
        addTimelineEvent("🔵", `Step 3/6: Measurement Counts — {0: ${c0}, 1: ${c1}}`);
        await sleep(480);

        // Stage 4: Error Rate (~480ms)
        const errVal = data.error_rate_percent != null ? data.error_rate_percent.toFixed(2) : "0.00";
        if (bobValError) bobValError.textContent = `${errVal}%`;
        setStageDone(bobStepError, "4");
        const isErrHigh = data.error_rate_percent > (data.threshold?.error_threshold_percent || 10);
        addTimelineEvent(isErrHigh ? "🔴" : "🔵", `Step 4/6: Error Rate — ${errVal}% (Threshold: ${(data.threshold?.error_threshold_percent || 10).toFixed(1)}%)`, isErrHigh);
        await sleep(480);

        // Stage 5: Chi-Square (~480ms)
        const chiVal = data.chi_square != null ? data.chi_square.toFixed(2) : "0.00";
        if (bobValChi) bobValChi.textContent = chiVal;
        setStageDone(bobStepChi, "5");
        const isChiHigh = data.chi_square > (data.threshold?.chi_threshold || 10);
        addTimelineEvent(isChiHigh ? "🔴" : "🔵", `Step 5/6: Chi-Square Test — ${chiVal} (Critical: ${(data.threshold?.chi_threshold || 10).toFixed(1)})`, isChiHigh);
        await sleep(480);

        // Stage 6: Final Decision (~350ms)
        const isValid = (data.status === "VALID");
        if (bobValVerdict) bobValVerdict.textContent = data.status;
        setStageDone(bobStepVerdict, isValid ? "✓" : "!");
        addTimelineEvent(isValid ? "🔵" : "🔴", `Step 6/6: Verdict — ${data.status} (${isValid ? "Signature Integrity Verified" : "Threat Policy Triggered"})`, !isValid);
        await sleep(350);
    }

    // Backward compatibility alias
    const animateCommunicationFlow = animateFullSimulationFlow;

    // -----------------------------------------------------------------------
    // 16. UPDATE VERIFICATION UI & METRICS
    // -----------------------------------------------------------------------
    function updateVerificationUI(data) {
        if (!statusBanner) return;

        statusBanner.className = "soc-card verdict-card";
        const iconEl = statusBanner.querySelector(".status-icon");

        if (data.status === "VALID") {
            statusBanner.classList.add("verdict-valid");
            statusBanner.style.borderColor = "#10b981";
            statusBanner.style.boxShadow = "0 0 24px rgba(16, 185, 129, 0.4)";
            if (statusTitle) {
                statusTitle.textContent = "VALID";
                statusTitle.style.color = "#10b981";
                statusTitle.style.textShadow = "0 0 10px rgba(16, 185, 129, 0.5)";
            }
            if (statusSubtitle) statusSubtitle.textContent = "Verification Passed";
            if (iconEl) {
                iconEl.textContent = "✓";
                iconEl.parentElement.style.borderColor = "#10b981";
                iconEl.parentElement.style.boxShadow = "0 0 14px rgba(16, 185, 129, 0.5)";
                iconEl.style.color = "#10b981";
            }
        } else if (data.status === "THREAT") {
            const isReplay = data.attack === "REPLAY" && data.attack_details?.replay_detected;
            statusBanner.classList.add("verdict-threat");
            statusBanner.style.borderColor = "#ef4444";
            statusBanner.style.boxShadow = "0 0 24px rgba(239, 68, 68, 0.45)";
            if (statusTitle) {
                statusTitle.textContent = isReplay ? "REPLAY DETECTED" : "THREAT";
                statusTitle.style.color = "#ef4444";
                statusTitle.style.textShadow = "0 0 10px rgba(239, 68, 68, 0.5)";
            }
            if (statusSubtitle) statusSubtitle.textContent = isReplay ? "Duplicate Signature Reused" : "Attack Detected";
            if (iconEl) {
                iconEl.textContent = "!";
                iconEl.parentElement.style.borderColor = "#ef4444";
                iconEl.parentElement.style.boxShadow = "0 0 14px rgba(239, 68, 68, 0.5)";
                iconEl.style.color = "#ef4444";
            }
        } else if (data.status === "BLOCKED") {
            statusBanner.classList.add("verdict-threat");
            statusBanner.style.borderColor = "#f59e0b";
            statusBanner.style.boxShadow = "0 0 24px rgba(245, 158, 11, 0.45)";
            if (statusTitle) {
                statusTitle.textContent = "BLOCKED";
                statusTitle.style.color = "#f59e0b";
                statusTitle.style.textShadow = "0 0 10px rgba(245, 158, 11, 0.5)";
            }
            if (statusSubtitle) statusSubtitle.textContent = `Unauthorized Verifier '${data.verifier}'`;
            if (iconEl) {
                iconEl.textContent = "!";
                iconEl.parentElement.style.borderColor = "#f59e0b";
                iconEl.parentElement.style.boxShadow = "0 0 14px rgba(245, 158, 11, 0.5)";
                iconEl.style.color = "#f59e0b";
            }
        }

        if (data.status === "BLOCKED") {
            if (metricErrorRate) metricErrorRate.textContent = "N/A";
            if (metricChiSquare) metricChiSquare.textContent = "N/A";
            return;
        }

        const errPct = data.error_rate_percent != null ? data.error_rate_percent : 0.0;
        const chiVal = data.chi_square != null ? data.chi_square : 0.0;
        const errThresh = data.threshold?.error_threshold_percent != null ? data.threshold.error_threshold_percent : 10.0;
        const chiThresh = data.threshold?.chi_threshold != null ? data.threshold.chi_threshold : 10.0;

        if (metricErrorRate)   metricErrorRate.textContent   = `${errPct.toFixed(2)}%`;
        if (metricErrorThresh) metricErrorThresh.textContent = `Threshold: ${errThresh.toFixed(1)}%`;
        if (metricChiSquare)   metricChiSquare.textContent   = chiVal.toFixed(2);
        if (metricChiThresh)   metricChiThresh.textContent   = `Threshold: ${chiThresh.toFixed(1)}`;
    }

    // -----------------------------------------------------------------------
    // 17. EXECUTE VERIFICATION WORKFLOW
    // -----------------------------------------------------------------------
    async function executeVerification(isAutoRun = false) {
        if (isSimRunning) return;
        isSimRunning = true;

        if (runVerifyBtn) {
            runVerifyBtn.disabled = true;
            runVerifyBtn.innerHTML = `<span class="play-arrow">⏳</span><span>RUNNING...</span>`;
        }
        simStartTime = Date.now();

        const timerInterval = setInterval(() => {
            if (simStartTime && simTimer) {
                simTimer.textContent = ((Date.now() - simStartTime) / 1000).toFixed(1) + "s";
            }
        }, 100);

        clearTimeline();
        resetPipeline();
        resetVerdictCard();

        const payload = {
            state: selectedState,
            attack: selectedAttack,
            verifier: selectedVerifier,
            sender: (selectedAttack === "IMPERSONATION") ? "Attacker" : "Alice",
            shots: parseInt(shotsSlider ? shotsSlider.value : 1000),
            error_threshold_pct: parseFloat(errorThreshSlider ? errorThreshSlider.value : 10.0),
            chi_threshold: parseFloat(chiThreshSlider ? chiThreshSlider.value : 10.0),
            channel_gate: channelGate,
            digital_message: "SIH26141 Quantum Signature Verification Payload",
            signature_id: `sig_qds_${Date.now()}`
        };

        try {
            // Initiate real backend request immediately in parallel with animation flow
            const apiPromise = fetch(`${API_BASE}/api/verify`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).then(async (res) => {
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || `HTTP ${res.status}`);
                }
                return res.json();
            });

            // Animate Alice -> Eve -> Bob flow
            const data = await animateFullSimulationFlow(apiPromise, payload);

            // Animate 6 Bob verification stages using actual returned Qiskit numbers
            await animateVerificationStages(data);

            // Update UI, Verdict Banner, Metric Cards & Recent Results
            updateVerificationUI(data);
            addRecentResult(data);

        } catch (error) {
            console.error("Verification Error:", error);
            addTimelineEvent("🔴", `Verification Error: ${error.message}`, true);
            if (!isAutoRun) {
                alert(`Verification Error: ${error.message}`);
            }
            showErrorVerdict(error.message);
        } finally {
            clearInterval(timerInterval);
            if (simTimer && simStartTime) {
                simTimer.textContent = ((Date.now() - simStartTime) / 1000).toFixed(1) + "s";
            }
            if (runVerifyBtn) {
                runVerifyBtn.disabled = false;
                runVerifyBtn.innerHTML = `<span class="play-arrow">▶</span><span>VERIFY</span>`;
            }
            isSimRunning = false;
            resetPackets();
            resetNodeStates();
        }
    }

    if (runVerifyBtn) {
        runVerifyBtn.addEventListener("click", () => {
            executeVerification(false);
        });
    }

    // -----------------------------------------------------------------------
    // 18. INITIALIZATION & SINGLE-RUN AUTO-SIMULATION
    // -----------------------------------------------------------------------
    updateQuantumStateHUD();
    renderRecentResults();
    resetPipeline();
    resetVerdictCard();

    // Automatically run ONE real simulation when dashboard loads
    if (!autoRunExecuted) {
        autoRunExecuted = true;
        setTimeout(() => {
            executeVerification(true);
        }, 300);
    }
});
