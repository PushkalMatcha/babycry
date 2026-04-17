// src/pages/Dashboard.js

import React, { useEffect, useRef, useState } from "react";
import { db } from "../firebase";
import { ref, onValue, set } from "firebase/database";
import "../styles/dashboard.css";

// ── Helpers ───────────────────────────────────────────────────
const ALERT_LABELS = {
  baby_moved:   "Baby moved outside zone",
  cry_detected: "Cry detected",
  no_baby:      "Baby not visible",
};

function fmtTime(ts) {
  if (!ts) return "";
  const d = new Date(ts.replace(" ", "T"));
  if (isNaN(d)) return ts;
  return d.toLocaleTimeString("en-IN", {
    hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
  });
}

function fmtDate(ts) {
  if (!ts) return "";
  const d = new Date(ts.replace(" ", "T"));
  if (isNaN(d)) return "";
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return "Today";
  const yest = new Date(today); yest.setDate(yest.getDate() - 1);
  if (d.toDateString() === yest.toDateString()) return "Yesterday";
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
}

// ── Component ─────────────────────────────────────────────────
function Dashboard() {
  const streamUrl = "/video-proxy";
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState("off");
  const [drawing, setDrawing] = useState(false);
  const [rect, setRect]     = useState(null);

  const canvasRef    = useRef(null);
  const containerRef = useRef(null);

  // Firebase
  useEffect(() => {
    onValue(ref(db, "events"), (snap) => {
      const data = snap.val() || {};
      setEvents(Object.values(data).reverse());
    });
    onValue(ref(db, "control/status"), (snap) => {
      setStatus(snap.val() || "off");
    });
  }, []);

  const toggle = (val) => set(ref(db, "control/status"), val);

  // Canvas sync
  useEffect(() => {
    const c = canvasRef.current;
    const w = containerRef.current;
    if (c && w) { c.width = w.clientWidth; c.height = w.clientHeight; }
  });

  const coords = (e) => {
    const r = canvasRef.current.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - r.left, y: clientY - r.top };
  };

  const startDrawing = (e) => {
    // If it's a touch event, prevent scrolling
    if (e.type === "touchstart" && e.cancelable) e.preventDefault();
    setDrawing(true);
    const { x, y } = coords(e);
    setRect({ x1: x, y1: y, x2: x, y2: y });
  };

  useEffect(() => {
    const move = (e) => {
      if (!drawing) return;
      const { x, y } = coords(e);
      setRect((p) => ({ ...p, x2: x, y2: y }));
    };
    const up = () => setDrawing(false);
    
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
    window.addEventListener("touchmove", move, { passive: false });
    window.addEventListener("touchend", up);
    
    return () => { 
      window.removeEventListener("mousemove", move); 
      window.removeEventListener("mouseup", up); 
      window.removeEventListener("touchmove", move);
      window.removeEventListener("touchend", up);
    };
  }, [drawing]);

  // Draw zone
  useEffect(() => {
    const c   = canvasRef.current;
    const ctx = c.getContext("2d");
    ctx.clearRect(0, 0, c.width, c.height);
    if (!rect) return;
    const w = rect.x2 - rect.x1, h = rect.y2 - rect.y1;
    ctx.fillStyle   = "rgba(99,102,241,0.07)";
    ctx.fillRect(rect.x1, rect.y1, w, h);
    ctx.strokeStyle = "rgba(99,102,241,0.7)";
    ctx.lineWidth   = 1.5;
    ctx.setLineDash([5, 4]);
    ctx.strokeRect(rect.x1, rect.y1, w, h);
    // Corner handles
    const sz = 5;
    ctx.setLineDash([]);
    ctx.fillStyle = "#6366f1";
    [[rect.x1,rect.y1],[rect.x2,rect.y1],[rect.x1,rect.y2],[rect.x2,rect.y2]].forEach(([cx,cy]) => {
      ctx.fillRect(cx - sz/2, cy - sz/2, sz, sz);
    });
  }, [rect]);

  const saveZone = () => {
    if (!rect) return;
    const c = canvasRef.current;
    set(ref(db, "safe_zone"), {
      x1: rect.x1 / c.width,  y1: rect.y1 / c.height,
      x2: rect.x2 / c.width,  y2: rect.y2 / c.height,
    });
  };

  const resetZone = () => { setRect(null); set(ref(db, "safe_zone"), null); };

  const toggleFullscreen = async () => {
    try {
      if (!document.fullscreenElement) {
        const enterFs = containerRef.current?.requestFullscreen || containerRef.current?.webkitRequestFullscreen;
        if (enterFs) {
          await enterFs.call(containerRef.current);
          if (window.screen?.orientation?.lock) {
            await window.screen.orientation.lock("landscape").catch(e => console.log("Orientation lock skip:", e));
          }
        }
      } else {
        if (window.screen?.orientation?.unlock) {
          window.screen.orientation.unlock();
        }
        const exitFs = document.exitFullscreen || document.webkitExitFullscreen;
        if (exitFs) {
          await exitFs.call(document);
        }
      }
    } catch (err) {
      console.error("Fullscreen/Orientation error:", err);
    }
  };

  // Analytics
  const total = events.length;
  const moves = events.filter((e) => e.type === "baby_moved").length;
  const cries = events.filter((e) => e.type === "cry_detected").length;

  return (
    <div className="app-shell">

      {/* ── Top Bar ────────────────────────────────────────── */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">👶</div>
          <span className="brand-name">BabyGuard</span>
        </div>

        <div className="topbar-center">
          <div className={`live-badge ${status === "on" ? "active" : ""}`}>
            <span className="live-dot" />
            {status === "on" ? "Recording" : "Standby"}
          </div>
        </div>

        <div className="topbar-right">
          <button className="btn btn-start" onClick={() => toggle("on")}>
            ▶ Start
          </button>
          <button className="btn btn-stop" onClick={() => toggle("off")}>
            ■ Stop
          </button>
        </div>
      </header>

      {/* ── Body ──────────────────────────────────────────── */}
      <div className="main">

        {/* ── Video Panel ─────────────────────────────────── */}
        <div className="video-section">
          <div className="video-frame" ref={containerRef}>
            {status === "on" ? (
              <img
                src={streamUrl}
                alt="Live camera feed"
              />
            ) : (
              <div className="video-offline">
                <div className="offline-icon">📷</div>
                <div className="offline-label">Camera offline</div>
                <div className="offline-sub">Press Start to begin monitoring</div>
              </div>
            )}

            {/* Always-on overlay and zone canvas */}
            {status === "on" && (
              <div className="video-overlay-tl">
                <span className="cam-label">CAM 01</span>
              </div>
            )}

            <canvas
              ref={canvasRef}
              className="video-frame-canvas"
              style={{ position:"absolute", inset:0, cursor:"crosshair", pointerEvents: status === "on" ? "auto" : "none", touchAction: "none" }}
              onMouseDown={startDrawing}
              onTouchStart={startDrawing}
            />
          </div>

          {/* Controls */}
          <div className="video-controls">
            <span className="zone-hint">
              <strong>Draw</strong> on the feed to define a safe zone
            </span>
            <div className="controls-right">
              <button className="btn btn-ghost" onClick={toggleFullscreen}>⛶ Full</button>
              <button className="btn btn-ghost" onClick={resetZone}>Clear zone</button>
              <button className="btn btn-accent" onClick={saveZone}>Save zone</button>
            </div>
          </div>
        </div>

        {/* ── Right Sidebar ────────────────────────────────── */}
        <div className="sidebar">

          {/* Stats */}
          <div className="stats-strip">
            <div className="stat">
              <div className="stat-n">{total}</div>
              <div className="stat-l">Total</div>
            </div>
            <div className="stat">
              <div className="stat-n" style={{ color: "var(--amber)" }}>{moves}</div>
              <div className="stat-l">Moves</div>
            </div>
            <div className="stat">
              <div className="stat-n" style={{ color: "var(--danger)" }}>{cries}</div>
              <div className="stat-l">Cries</div>
            </div>
          </div>

          {/* Activity */}
          <div className="feed-header">
            <span className="feed-title">Activity</span>
            <span className="feed-count">{total} events</span>
          </div>

          <div className="feed-list">
            {events.length === 0 ? (
              <div className="feed-empty">
                <span className="feed-empty-icon">🛡</span>
                No alerts recorded yet
              </div>
            ) : (
              events.map((e, i) => (
                <div key={i} className={`alert-row t-${e.type}`}>
                  <span className="alert-pip" />
                  <div className="alert-body">
                    <div className="alert-type">
                      {ALERT_LABELS[e.type] || e.type}
                    </div>
                    <div className="alert-time">
                      {fmtDate(e.time)} · {fmtTime(e.time)}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default Dashboard;