// src/pages/Login.js

import React, { useState } from "react";
import "../styles/login.css";

function Login({ setUser }) {
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState(false);

  const submit = () => {
    if (email === "nitinkeshav0805@gmail.com" && password === "1234") {
      setUser(true);
    } else {
      setError(true);
      setTimeout(() => setError(false), 2400);
    }
  };

  const onKey = (e) => { if (e.key === "Enter") submit(); };

  return (
    <div className="login-page">

      {/* ── Left branding panel ──────────────────────────── */}
      <div className="login-left">
        <div className="login-left-inner">
          <div className="login-mark">👶</div>
          <h1 className="login-headline">
            Know your baby<br />is safe. Always.
          </h1>
          <p className="login-tagline">
            Real-time video monitoring with AI-powered<br />
            cry detection and movement alerts.
          </p>
          <div className="login-features">
            {[
              "Live camera stream with safe-zone detection",
              "Instant cry & movement alerts",
              "Full event history via Firebase",
            ].map((f) => (
              <div key={f} className="login-feature">
                <span className="login-feature-dot" />
                {f}
              </div>
            ))}
          </div>
        </div>
        <p className="login-left-footer">BabyGuard · Built with care</p>
      </div>

      {/* ── Right form panel ─────────────────────────────── */}
      <div className="login-right">
        <div className="login-form">

          <div className="login-form-header">
            <div className="login-brand-label">BabyGuard</div>
            <h2 className="login-form-title">Sign in</h2>
            <p className="login-form-sub">Access your monitoring dashboard</p>
          </div>

          <div className="login-fields">
            <div className="login-field">
              <label className="login-label">Email address</label>
              <input
                type="email"
                className={`login-input${error ? " error" : ""}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={onKey}
              />
            </div>

            <div className="login-field">
              <label className="login-label">Password</label>
              <input
                type="password"
                className={`login-input${error ? " error" : ""}`}
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={onKey}
              />
            </div>

            {error && (
              <div className="login-error">
                Incorrect email or password — please try again.
              </div>
            )}

            <button className="login-submit" onClick={submit}>
              Continue →
            </button>
          </div>

          <p className="login-disclaimer">Secure access to your monitoring system</p>
        </div>
      </div>

    </div>
  );
}

export default Login;