"use client";

import { useEffect, useRef } from "react";
import { products } from "@/data/products";

/**
 * Faithful re-implementation of the Agrumea Farm (Nuxt) jar slider.
 * Constants and formulas are extracted verbatim from the live bundle
 * (_nuxt/D3S2afzA.js) so the arrangement matches www.agrumeafarm.it/en:
 *  - 10 jars evenly spaced on a loop that wraps seamlessly
 *  - marquee tilted by --jar-marquee-angle (10deg)
 *  - drag / wheel scrolling with inertia
 *  - rotation drives the circular text badge (--jar-circle-rotation)
 *  - mouse-hover parallax (--jar-parallax-x/y)
 *  - per-jar spring physics: lean toward the pointer, lift, pull, scale-up
 *    and brightness boost for the focused jar (the interactive 3D feel)
 *  - hover dwell triggers a full spin cycle; the label overlay image is
 *    cross-faded across the jar during the spin (canvas strip mapping,
 *    approximated here with a masked CSS crossfade)
 */

/* ---- constants copied from the live bundle ---- */
const JAR_ARC_DEG = 18; // `or` — sine amplitude of the vertical arc (deg)
const ASPECT = 1013 / 630; // `Xt` — jar image aspect ratio
const LEAN_OFFSETS = [-0.053, 0.043, -0.024, 0.057, -0.048, 0.029, -0.038, 0.053]; // `Bt`
const CYCLE_MS = 4000; // `Gt` (xa export used as hover-cycle duration)
const IDLE_SCALE = 0.55; // `Yt`
const ACTIVE_SCALE = 1.35; // `Le`
const EDGE_DIM = 0.1; // `ur`
const BRIGHT_MIN = 0.7; // `Ht`
const BRIGHT_MAX = 1.1; // `hr`
const BLUR_MAX = 4; // `mr` desktop
const BLUR_MAX_MOBILE = 2; // `_r`
const INTRO_MS = 1150; // `qe`
const INTRO_LIFT = 56; // `Se` px
const INTRO_OPACITY_FROM = 0.9; // `Ut`
const BADGE_INTRO_ROT = -18; // `Wt` deg
const ITEM_RATIO = 1.15; // `Lr` — width factor over slot base
const WHEEL_SPEED = 1.15; // `Ir`
const DRAG_SPEED = 1.5; // `zt`
const FLING_SPEED = 190; // `wr`
const FLING_CLAMP = 3.5; // `Jt`
const FRAME_CAP = 1 / 30; // `br`
const MAX_SPEED = 2400; // `Vt` px/s
const STREAK_DEG = 6; // `Tr`
const STREAK_SCALE = 0.05; // `Cr`
const STREAK_PULL_X = 3.2; // `Mr`
const STREAK_PULL_Y = 1.6; // `Pr`
const EASE_CENTER = 0.55; // `Ar`
const EASE_K = 0.16; // `qt`
const SEED_BASE = 70; // `xr`
const SEED_SPREAD = 0.3; // `Qt`
const SPRING_DAMP = 9; // `Dr`
const SPIN_TILT = 38; // `Nr` deg — rotateY while spinning
const SPIN_LEAN = 30; // `Fr` deg
const SPIN_BIAS = 0.3; // `Kt`
const SPIN_LIFT = 0.05; // `jr`
const SPIN_PULL = 16; // `Zt` px
const GAUSS_R = 1.6; // `Xr`
const PARALLAX_GAIN = 26; // `ea`
const SPEED_TO_DEG = -0.012; // `Rr` desktop, `Or` mobile (-0.03)
const FRONT_ROT = 182; // `FRONT_ROT` deg where the label faces front
const LABEL_FADE = 1; // `gr`
const TILT_LEFT_DEG = -20; // triptych: left jar leans ~20°, centre/right upright
const MOUSE_TILT_DEG = 6; // pointer-driven rotateX/rotateY amplitude (±6°)
const DEPTH_FACTOR = [26, 54, 34]; // per-slot parallax depth (px per unit pointer offset)

type Spring = { value: number; velocity: number };
const newSpring = (): Spring => ({ value: 0, velocity: 0 });
const stepSpring = (s: Spring, target: number, stiff: number, dt: number) => {
  s.velocity += ((target - s.value) * stiff - s.velocity * SPRING_DAMP) * dt;
  s.value += s.velocity * dt;
  if (Math.abs(s.velocity) < 0.001 && Math.abs(target - s.value) < 0.001) {
    s.value = target;
    s.velocity = 0;
  }
};
const easeOutCubic = (t: number) => 1 - (1 - t) ** 3;
const smoothCycle = (p: number) => {
  const x = p % 1;
  return x < 0.5 ? 0.5 * (1 - Math.cos(Math.PI * x)) : 0.5 * (1 + Math.cos(Math.PI * x));
};

export function JarSlider() {
  const rootRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const wrap = root.querySelector<HTMLElement>("[data-jar-slider-wrap]");
    const track = root.querySelector<HTMLElement>("[data-jar-slider-track]");
    const itemEls = Array.from(root.querySelectorAll<HTMLElement>("[data-jar-slider-item]"));
    if (!wrap || !track || itemEls.length === 0) return;

    const fine = window.matchMedia("(hover: hover) and (pointer: fine)");
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const D = itemEls.length;

    /* Hydration-safe: SSR renders a neutral centered row of jars. We switch to
       JS-driven absolute positioning only after mount, by adding this class. */
    root.classList.add("is-hydrated");

    /* geometry state (mirrors the live closure vars) */
    let N = 0; // slot pitch
    let Z = 0; // viewport / 4 unit
    let u = 0; // item width
    let R = 0; // item height
    let F = 0; // full loop length
    let j = 0; // stagger offset (2*N)
    let ee = 0; // marquee height var
    let T = 0; // track center x relative to root
    let y = 0; // track center y relative to root
    let cosA = 1;
    let sinA = 0;
    let L = 0; // label width factor (label img natural w/h vs jar)

    const measure = () => {
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const xs = vw <= 480;
      const sm = !xs && vw <= 1024;
      /* Triptych layout: slot pitch ≈ one third of the viewport so that at any
         moment only three jars sit on screen (left tilted, centre and right
         upright) — matching www.agrumeafarm.it/en. The remaining jars live far
         off-screen inside the overflow-hidden wrapper (no horizontal scrollbar). */
      Z = vw / 3;
      N = Z * (xs ? 1.08 : sm ? 1.12 : 1.06);
      u = Z * (xs ? 0.82 : sm ? 0.8 : 0.78) * ITEM_RATIO;
      R = u * ASPECT;
      const cap = vh * 0.72;
      if (R > cap) {
        R = cap;
        u = R / ASPECT;
      }
      F = D * N;
      j = 2 * N;
      ee = Math.min(R * 1.35, vh * 0.95);
      root.style.setProperty("--jar-item-w", `${u}px`);
      root.style.setProperty("--jar-item-h", `${R}px`);
      root.style.setProperty("--jar-marquee-h", `${ee}px`);
      const er = root.getBoundingClientRect();
      const tr = track.getBoundingClientRect();
      T = tr.left + tr.width / 2 - er.left;
      y = tr.top + tr.height / 2 - er.top;
      const angleDeg = parseFloat(getComputedStyle(root).getPropertyValue("--jar-marquee-angle")) || 0;
      const C = (angleDeg * Math.PI) / 180;
      cosA = Math.cos(C);
      sinA = Math.sin(C);
    };
    measure();

    /* position of jar i along the loop at scroll H */
    const posOf = (i: number, r: number, add = 0) => {
      let c = (i * N + u / 2 + r + add) % F;
      if (c < 0) c += F;
      return c - j;
    };

    type Item = {
      el: HTMLElement;
      img: HTMLImageElement | null;
      canvas: HTMLCanvasElement | null;
      ctx2d: CanvasRenderingContext2D | null;
      labelImg: HTMLImageElement | null;
      turn: Spring;
      lean: Spring;
      lift: Spring;
      pullX: Spring;
      pullY: Spring;
      cycleStart: number;
      hoverQueued: boolean;
      isPointerOver: boolean;
      pointerEnterTime: number;
      hoverDwellStart: number;
      renderedOffset: number;
      needsRender: boolean;
    };

    const items: Item[] = itemEls.map((el) => {
      const canvas = el.querySelector<HTMLCanvasElement>("canvas.jar-slider__label");
      return {
        el,
        img: el.querySelector<HTMLImageElement>("img.jar-slider__base"),
        canvas,
        ctx2d: canvas?.getContext("2d") ?? null,
        labelImg: null,
        turn: newSpring(),
        lean: newSpring(),
        lift: newSpring(),
        pullX: newSpring(),
        pullY: newSpring(),
        cycleStart: -1,
        hoverQueued: false,
        isPointerOver: false,
        pointerEnterTime: -1,
        hoverDwellStart: -1,
        renderedOffset: NaN,
        needsRender: true,
      };
    });

    /* load label images; derive the wrap-around gap in px like the shader's GAP_LABEL */
    const labelUrls = Array.from(new Set(itemEls.map((el) => el.dataset.label ?? ""))).filter(Boolean);
    void Promise.all(
      labelUrls.map(
        (src) =>
          new Promise<void>((resolve) => {
            const im = new Image();
            im.onload = () => resolve();
            im.onerror = () => resolve();
            im.src = src;
          }),
      ),
    ).then(() => {
      const first = labelUrls[0];
      if (first) {
        const probe = new Image();
        probe.onload = () => {
          if (probe.naturalWidth && probe.naturalHeight) {
            L = (probe.naturalWidth / probe.naturalHeight) * ASPECT;
          }
        };
        probe.src = first;
      }
    });

    /* ---- input state ---- */
    let target = 0; // ae — target scroll
    let H = 0; // current scroll
    let vel = 0; // ce — px/s
    let lastInteract = -1;
    let dragging = false;
    let dragId = -1;
    let movedFar = false;
    let suppressClick = false;
    let dragX = 0;
    let downX = 0;
    let dragVel = 0;
    let dragTime = 0;
    let pointerInside = false;
    let mouseX = 0;
    let mouseY = 0;

    const setTarget = (v: number) => {
      target = v;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const d = Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX;
      setTarget(target - d * WHEEL_SPEED);
    };
    const onDown = (e: PointerEvent) => {
      dragging = true;
      dragId = e.pointerId;
      movedFar = false;
      suppressClick = false;
      dragX = e.clientX;
      downX = e.clientX;
      dragVel = 0;
      dragTime = e.timeStamp || performance.now();
    };
    const onMove = (e: PointerEvent) => {
      if (!dragging || e.pointerId !== dragId) return;
      if (!movedFar) {
        if (Math.abs(e.clientX - downX) <= 6) return;
        try {
          wrap.setPointerCapture(e.pointerId);
        } catch {
          return;
        }
        movedFar = true;
        suppressClick = true;
        dragX = e.clientX;
        dragTime = e.timeStamp || performance.now();
        return;
      }
      const dx = e.clientX - dragX;
      const now = e.timeStamp || performance.now();
      const dtms = Math.max(1, now - dragTime);
      dragVel = dragVel * 0.72 + (dx / dtms) * 0.28;
      dragX = e.clientX;
      dragTime = now;
      setTarget(target + dx * DRAG_SPEED);
    };
    const onUp = (e: PointerEvent) => {
      if (dragId === -1 || e.pointerId !== dragId) return;
      if (movedFar) {
        try {
          wrap.releasePointerCapture(e.pointerId);
        } catch {
          /* noop */
        }
        const v = Math.max(-FLING_CLAMP, Math.min(FLING_CLAMP, dragVel));
        setTarget(target + v * DRAG_SPEED * FLING_SPEED);
      }
      dragVel = 0;
      dragging = false;
      dragId = -1;
      movedFar = false;
    };
    const onClickCapture = (e: MouseEvent) => {
      if (suppressClick) {
        e.preventDefault();
        e.stopPropagation();
        suppressClick = false;
      }
    };
    const onRootMove = (e: PointerEvent) => {
      if (e.pointerType === "touch") return;
      pointerInside = true;
      mouseX = e.clientX;
      mouseY = e.clientY;
    };
    const onRootLeave = () => {
      pointerInside = false;
    };

    items.forEach((it) => {
      const enter = () => {
        if (!fine.matches) return;
        it.isPointerOver = true;
        it.hoverQueued = true;
        it.pointerEnterTime = performance.now();
      };
      const leave = () => {
        it.isPointerOver = false;
        it.hoverQueued = false;
      };
      it.el.addEventListener("pointerenter", enter);
      it.el.addEventListener("pointerleave", leave);
    });

    window.addEventListener("resize", measure);
    wrap.addEventListener("wheel", onWheel, { passive: false });
    wrap.addEventListener("pointerdown", onDown);
    wrap.addEventListener("pointermove", onMove);
    wrap.addEventListener("pointerup", onUp);
    wrap.addEventListener("pointercancel", onUp);
    wrap.addEventListener("click", onClickCapture, true);
    root.addEventListener("pointermove", onRootMove, { passive: true });
    root.addEventListener("pointerleave", onRootLeave);

    /* intro timing */
    const mountT = performance.now();
    let revealAt = -1;
    const orderDelay = () => {
      const vw = window.innerWidth;
      const visible: number[] = [];
      const hidden: { index: number; distance: number }[] = [];
      items.forEach((_, l) => {
        const p = posOf(l, 0);
        if (p + u / 2 > 0 && p - u / 2 < vw) visible.push(l);
        else hidden.push({ index: l, distance: p < vw / 2 ? Math.abs(p + u / 2) : Math.abs(p - vw - u / 2) });
      });
      hidden.sort((a, b) => a.distance - b.distance);
      [...visible, ...hidden.map((h) => h.index)].forEach((index, order) => {
        // store delay via dataset read back in loop? simpler: array
        delays[index] = order * 0; // $t === 0 on the live site
      });
    };
    const delays = new Array<number>(items.length).fill(0);
    orderDelay();
    // The live site reveals jars once ready (introDelay spacing is 0ms).
    revealAt = mountT + 1000; // labelDelayMs = 1000 (`tn`)

    /* parallax smoothing */
    let PX = 0;
    let PY = 0;
    let P = 0; // presence weight

    let raf = 0;
    let prev = performance.now();
    let destroyed = false;

    const frame = (now: number) => {
      if (destroyed) return;
      const dt = Math.min(FRAME_CAP, Math.max(0, (now - prev) / 1000));
      prev = now;

      const animate = !reduced.matches;
      const useParallax = animate && pointerInside && fine.matches;
      let plx = 0;
      let ply = 0;
      if (useParallax || P > 0) {
        const rect = root.getBoundingClientRect();
        plx = mouseX - rect.left;
        ply = mouseY - rect.top;
        if (useParallax && rect.width > 0 && rect.height > 0) {
          const k = 1 - Math.exp(-4 * dt);
          const nx = Math.max(-1, Math.min(1, (plx / rect.width) * 2 - 1));
          const ny = Math.max(-1, Math.min(1, (ply / rect.height) * 2 - 1));
          PX += (nx - PX) * k;
          PY += (ny - PY) * k;
        }
      }
      P += ((useParallax ? 1 : 0) - P) * (1 - Math.exp(-3 * dt));
      if (!useParallax && P < 0.001) P = 0;
      const g = PX * P;
      const E = PY * P;
      root.style.setProperty("--jar-parallax-x", g.toFixed(4));
      root.style.setProperty("--jar-parallax-y", E.toFixed(4));

      const oldH = H;
      const dampRate = dragging ? 11 : 2.3;
      H += (target - H) * (1 - Math.exp(-dampRate * dt));
      if (Math.abs(target - H) < 0.05) H = target;
      vel = dt > 0 ? (H - oldH) / dt : 0;

      const vw = window.innerWidth;
      const degPerPx = vw <= 480 ? -0.03 : SPEED_TO_DEG;
      root.style.setProperty("--jar-circle-rotation", `${H * degPerPx}deg`);

      const hovering = fine.matches;
      const speedAbs = Math.abs(vel);
      if (dragging || speedAbs > 6) lastInteract = now;

      const idleZone = !dragging && speedAbs <= N * 1.4;
      const sp = Math.min(1, speedAbs / MAX_SPEED);
      const sp2 = sp * sp;
      const streakRot = -Math.sign(vel) * sp * STREAK_DEG;
      const streakScale = 1 - sp2 * STREAK_SCALE;
      const streakPull = sp2 * (vw <= 480 ? STREAK_PULL_Y * 0.5 : STREAK_PULL_X);

      const introShape = easeOutCubic(Math.min(1, Math.max(0, (now - mountT) / INTRO_MS)));
      root.style.setProperty("--jar-shape-intro-opacity", `${introShape}`);
      root.style.setProperty("--jar-shape-intro-y", `${(1 - introShape) * INTRO_LIFT * 0.42}px`);
      const introBadge = easeOutCubic(Math.min(1, Math.max(0, (now - mountT) / INTRO_MS)));
      root.style.setProperty("--jar-badge-intro-opacity", `${introBadge}`);
      root.style.setProperty("--jar-badge-intro-y", `${(1 - introBadge) * INTRO_LIFT * 0.22}px`);
      root.style.setProperty("--jar-badge-intro-rotation", `${(1 - introBadge) * BADGE_INTRO_ROT}deg`);

      items.forEach((a, ne) => {
        /* hover dwell → spin cycle (computed first so the 3D vars can use it) */
        let Ct = 0;
        const dwellOk = idleZone && a.isPointerOver;
        if (!dwellOk) a.hoverDwellStart = -1;
        else if (a.hoverDwellStart < 0) a.hoverDwellStart = now;
        const freshEnter = a.pointerEnterTime > lastInteract;
        if (
          hovering &&
          a.isPointerOver &&
          a.hoverQueued &&
          a.cycleStart < 0 &&
          a.hoverDwellStart >= 0 &&
          (freshEnter || now - a.hoverDwellStart >= 260)
        ) {
          a.cycleStart = now;
          a.hoverQueued = false;
        }
        if (hovering && a.cycleStart >= 0) {
          const ve = (now - a.cycleStart) / 1000;
          if (ve >= CYCLE_MS / 1000) a.cycleStart = -1;
          else Ct = smoothCycle(ve / (CYCLE_MS / 1000));
        } else if (!hovering) {
          a.cycleStart = -1;
          a.hoverQueued = false;
          a.isPointerOver = false;
        }

        const fe = posOf(ne, H); // position along loop (0 = centre slot)

        /* ---- index-driven triptych roles: prev / active / next ----
           Only three jars are ever visible: slot -1 (left, leaning ~20°),
           slot 0 (centre, upright) and slot 1 (right, upright). Everything
           else is parked far off-screen inside the overflow-hidden wrapper. */
        const slotIdx = Math.floor(fe / N); // -1 = left, 0 = centre, 1 = right
        const fracPos = fe / N - slotIdx; // wrap-around position inside the slot [0,1)
        const distFromSlot = fracPos > 0.5 ? fracPos - 1 : fracPos; // signed [-0.5,0.5)
        const onStage = slotIdx === -1 || slotIdx === 0 || slotIdx === 1;
        /* tilt only applies to the left jar; cross-fade so a jar straightens
           as it slides from the left slot into the centre slot */
        const triVis = onStage ? 1 - Math.min(1, Math.abs(distFromSlot) * 2) : 0;
        const roleRot = slotIdx === -1 ? TILT_LEFT_DEG * triVis : 0;

        /* Triptych gate: the three stage slots (-1 left / 0 centre / 1 right)
           map to viewport thirds; every other jar is parked far off-screen. */
        let q: number;
        if (slotIdx === -1) q = (fracPos + 0.5) / 3;
        else if (slotIdx === 0) q = (1 + fracPos) / 3;
        else if (slotIdx === 1) q = (2 + fracPos) / 3;
        else q = fe < 0 ? -2 : 5;
        const ft = (q + EASE_CENTER * EASE_K * Math.tanh((q - 0.5) / EASE_K)) * vw; // eased x center
        const gt = onStage ? Math.max(0, Math.cos(distFromSlot * Math.PI)) : 0; // focus bell
        const vt = N / vw;
        const Ye = vt > 0 ? Math.abs(q - 0.5) / vt : 0; // edge proximity
        const ca = 1 - EDGE_DIM * Math.min(1, Ye);
        const yt = (IDLE_SCALE + gt * (ACTIVE_SCALE - IDLE_SCALE)) * ca; // scale
        const da = BRIGHT_MIN + gt ** 1 * (BRIGHT_MAX - BRIGHT_MIN); // brightness
        const ua =
          revealAt < 0
            ? 0
            : easeOutCubic(Math.min(1, Math.max(0, (now - revealAt - delays[ne]) / INTRO_MS)));
        const Pe = ua; // intro progress
        const Lt = (1 - Pe) * INTRO_LIFT; // intro translateY
        const ha = INTRO_OPACITY_FROM + Pe * (1 - INTRO_OPACITY_FROM);
        const pa = Pe; // opacity

        const ma = ne * N + H;
        /* Per-jar resting tilt is suppressed now that the triptych assigns an
           explicit role tilt; the sine term keeps a subtle live "breathing". */
        const _a = Math.sin((ma / (3 * N)) * Math.PI * 2) * JAR_ARC_DEG * 0.4 + roleRot;
        const St = LEAN_OFFSETS[ne % LEAN_OFFSETS.length] * R * (onStage ? 1 : 0); // stagger Y
        const Et = ft - vw / 2;
        const It = St + Lt;
        // rotated marquee coords -> page coords (relative to root)
        const fa = T + Et * cosA - It * sinA;
        const ga = y + Et * sinA + It * cosA;

        /* interactive 3D: lean toward pointer & spin response */
        let wt = animate ? -Math.max(-1, Math.min(1, vel / MAX_SPEED)) * SPIN_TILT : 0;
        let bt = streakRot;
        let Tt = 0;
        let Mt = 0;
        let Pt = 0;
        if (P > 0) {
          const ve = plx - fa;
          const Rt = ply - ga;
          const $e = ve * cosA + Rt * sinA; // local along marquee
          const Ue = -ve * sinA + Rt * cosA; // local across marquee
          const We = u * GAUSS_R;
          const ye = Math.exp(-(($e * $e + Ue * Ue) / (We * We)));
          const ze = Math.tanh($e / We);
          const Ma = Math.tanh(Ue / (R * 0.8));
          const Pa = P * (SPIN_BIAS + (1 - SPIN_BIAS) * ye);
          const Ot = yt / ACTIVE_SCALE;
          const Ca = (g * cosA + E * sinA) * PARALLAX_GAIN * Ot;
          const Ra = (-g * sinA + E * cosA) * PARALLAX_GAIN * Ot;
          wt += ze * SPIN_TILT * Pa;
          bt += ze * SPIN_LEAN * ye * P;
          Tt = SPIN_LIFT * ye * P;
          Mt = ze * SPIN_PULL * ye * P + Ca;
          Pt = Ma * SPIN_PULL * ye * P + Ra;
        }
        const ge = SEED_BASE * (1 - SEED_SPREAD / 2 + SEED_SPREAD * ((ne * 0.618034) % 1));
        stepSpring(a.turn, wt, ge, dt);
        stepSpring(a.lean, bt, ge, dt);
        stepSpring(a.lift, Tt, ge, dt);
        stepSpring(a.pullX, Mt, ge, dt);
        stepSpring(a.pullY, Pt, ge, dt);

        const va = ft - u / 2 + a.pullX.value;
        const ya = St * triVis + Lt + a.pullY.value;
        const La = yt * ha * streakScale * (1 + a.lift.value);

        /* per-frame interactive 3D: expose the spring values as CSS custom
           properties so the base image and label canvas rotate in real 3D
           space around the jar's cylinder axis (perspective on the item).
           Each slot carries its own depth coefficient so the three visible
           jars parallax at different rates while the pointer moves. */
        const slotNo = Math.max(0, Math.min(2, slotIdx + 1));
        const depthK = DEPTH_FACTOR[slotNo] / DEPTH_FACTOR[1];
        const turnY = a.turn.value + Ct * 360; // hover spin adds a full turn
        const st = a.el.style;
        /* triptych role tag drives CSS visibility (prev / active / next) */
        const roleAttr = onStage ? (slotIdx === -1 ? "prev" : slotIdx === 0 ? "active" : "next") : "";
        if (roleAttr) {
          if (a.el.dataset.jarRole !== roleAttr) a.el.setAttribute("data-jar-role", roleAttr);
        } else if (a.el.hasAttribute("data-jar-role")) {
          a.el.removeAttribute("data-jar-role");
        }
        st.setProperty("--jar-turn-y", `${turnY.toFixed(3)}deg`);
        st.setProperty("--jar-turn-x", `${(-E * MOUSE_TILT_DEG * depthK).toFixed(3)}deg`);
        st.setProperty("--jar-turn-z", `${(g * MOUSE_TILT_DEG * 0.45 * depthK).toFixed(3)}deg`);
        st.setProperty("--jar-depth", `${(Tt * 60 + E * 8 * depthK).toFixed(2)}px`);
        st.setProperty("--jar-depth-px", `${DEPTH_FACTOR[slotNo]}px`);
        st.transform = `translate(${va}px, ${ya}px) rotate(${_a + a.lean.value}deg) scale(${La})`;
        st.opacity = `${pa}`;

        const blurCap = vw <= 480 ? BLUR_MAX_MOBILE : BLUR_MAX;
        const Ea = Math.min(blurCap, Ye * Ye * 1) + streakPull;
        a.el.style.filter = `brightness(${da}) blur(${Ea.toFixed(2)}px)`;

        /* label wrap-around offset (shader uOffset equivalent) */
        const wa = Pe * LABEL_FADE;
        const ba = Math.round(a.turn.value / 360 / 0.0005) * 0.0005;
        const He = FRONT_ROT / 360 - Ct - wa - ba;
        const Ta = fe + u > 0 && fe - u < vw; // on-screen

        /* paint label strip onto canvas with the same seam-gap math */
        if (a.ctx2d && a.canvas && a.img) {
          const cw = Math.round(u * devicePixelRatio);
          const ch = Math.round(R * devicePixelRatio);
          if (a.canvas.width !== cw || a.canvas.height !== ch) {
            a.canvas.width = cw;
            a.canvas.height = ch;
          }
          if (a.needsRender || (Ta && a.renderedOffset !== He)) {
            const ctx = a.ctx2d;
            ctx.clearRect(0, 0, cw, ch);
            const labelSrc = a.labelImg ?? undefined;
            if (labelSrc && labelSrc.complete && labelSrc.naturalWidth) {
              // Circumference of the virtual cylinder in canvas px (matches
              // the live site's LatheGeometry: width factor L over jar box).
              const W = u * (L || 1.45) * devicePixelRatio;
              const frac = ((He % 1) + 1) % 1;
              const visW = cw;
              let cursor = 0;
              while (cursor < visW) {
                const srcX = frac * W + cursor;
                const wrapped = ((srcX % W) + W) % W;
                const take = Math.min(visW - cursor, W - wrapped);
                ctx.drawImage(labelSrc, wrapped, 0, take, labelSrc.naturalHeight, cursor, 0, take, ch);
                cursor += take;
              }
              /* mask to the jar silhouette using the base image alpha */
              ctx.globalCompositeOperation = "destination-in";
              ctx.drawImage(a.img, 0, 0, a.img.naturalWidth, a.img.naturalHeight, 0, 0, cw, ch);
              ctx.globalCompositeOperation = "source-over";
            }
            a.renderedOffset = He;
            a.needsRender = false;
          }
        }
      });

      raf = requestAnimationFrame(frame);
    };
    /* preload label elements for canvas drawing */
    items.forEach((a) => {
      const src = a.el.dataset.label;
      if (!src) return;
      const im = new Image();
      im.decoding = "async";
      im.onload = () => {
        a.labelImg = im;
        a.needsRender = true;
      };
      im.src = src;
    });

    raf = requestAnimationFrame(frame);

    return () => {
      destroyed = true;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", measure);
      wrap.removeEventListener("wheel", onWheel);
      wrap.removeEventListener("pointerdown", onDown);
      wrap.removeEventListener("pointermove", onMove);
      wrap.removeEventListener("pointerup", onUp);
      wrap.removeEventListener("pointercancel", onUp);
      wrap.removeEventListener("click", onClickCapture, true);
      root.removeEventListener("pointermove", onRootMove);
      root.removeEventListener("pointerleave", onRootLeave);
    };
  }, []);

  return (
    <section className="jar-slider" ref={rootRef} data-jar-slider data-anim="hero">
      <h1 className="visually-hidden">
        Agrumea Farm: Sicilian artisan marmalades, spreads and preserves
      </h1>

      <div className="jar-slider__shape-layer" aria-hidden="true">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          className="jar-slider__shape-image"
          src="/assets/agrumea/back-slider-home.svg"
          alt=""
          width={1407}
          height={601}
          decoding="async"
        />
        <div className="jar-slider__badge jar-slider__badge--artwork">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="jar-slider__badge-artwork"
            src="/assets/agrumea/circle-text-en.svg"
            alt=""
            width={1168}
            height={1171}
            decoding="async"
          />
        </div>
      </div>

      <div className="jar-slider__overlay">
        <p className="jar-slider__prompt is-ready">Scroll to discover</p>
      </div>

      <div className="jar-slider__wrapper" data-jar-slider-wrap>
        <div className="jar-slider__marquee">
          <div className="jar-slider__track" data-jar-slider-track>
            {products.map((p, i) => (
              <a
                key={p.slug}
                className="jar-slider__item"
                href={`/dispensa/${p.slug}`}
                aria-label={p.name}
                data-jar-slider-item
                data-jar={p.image}
                data-label={p.label}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  className="jar-slider__base"
                  src={p.image}
                  alt={p.name}
                  width={995}
                  height={1600}
                  loading={i < 5 ? "eager" : "lazy"}
                  decoding="async"
                />
                <canvas className="jar-slider__label" aria-hidden="true" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
