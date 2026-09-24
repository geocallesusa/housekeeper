const { useEffect, useMemo, useState } = React;
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const LABELS = { Mon:"Lun", Tue:"Mar", Wed:"Mié", Thu:"Jue", Fri:"Vie", Sat:"Sáb", Sun:"Dom" };

function isAvailable(p, date, time) {
  if (!date || !time) return true;
  return p.days.includes(DAYS[new Date(date + "T12:00:00").getDay()]) && time >= p.start && time < p.end;
}

function ProviderMap({ providers, selected, onSelect }) {
  const position = p => ({ left: `${((p.lng + 89.275) / .09) * 100}%`, top: `${((13.75 - p.lat) / .10) * 100}%` });
  return <div className="map local-map">
    <svg viewBox="0 0 1000 620" preserveAspectRatio="none" aria-label="Mapa de San Salvador">
      <rect width="1000" height="620" fill="#eaf0e8"/><path d="M-30 490 C180 400 240 510 450 360 S760 310 1040 120" stroke="#fffdf8" strokeWidth="34" fill="none"/><path d="M-30 490 C180 400 240 510 450 360 S760 310 1040 120" stroke="#d3b27e" strokeWidth="5" fill="none"/>
      <path d="M70 -20 C240 130 320 100 410 280 S590 490 940 650 M-20 200 C170 230 350 180 550 230 S820 370 1030 340 M210 0 L510 620 M650 0 L430 620" stroke="#fff" strokeWidth="14" fill="none"/><path d="M90 70 L870 550 M80 570 L860 70" stroke="#c8d7c6" strokeWidth="8" fill="none" strokeDasharray="16 14"/>
      <text x="410" y="315" className="city-label">SAN SALVADOR</text><text x="725" y="500" className="district-label">Santa Elena</text><text x="135" y="150" className="district-label">Mejicanos</text><text x="205" y="410" className="district-label">Escalón</text>
    </svg>
    <div className="map-key">⌖ San Salvador, El Salvador</div>
    {providers.map(p => <button key={p.id} className={'map-pin '+(selected?.id===p.id?'active':'')} style={position(p)} onClick={()=>onSelect(p)}><img src={p.photo}/><b>${p.fee}</b></button>)}
    {selected && <div className="map-popup"><button onClick={()=>onSelect(null)}>×</button><img src={selected.photo}/><div><strong>{selected.name}</strong><span>★ {selected.rating} · {selected.area}</span><em>${selected.fee}/hora</em><small>{selected.start} – {selected.end}</small></div></div>}
  </div>;
}

function App() {
  const [providers, setProviders] = useState([]);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [selected, setSelected] = useState(null);
  const [searched, setSearched] = useState(false);
  const [user, setUser] = useState(null);
  const [loginOpen, setLoginOpen] = useState(true);
  const [loginForm, setLoginForm] = useState({ email: "admin@geovany.com", password: "housekeeper123" });
  const [loginError, setLoginError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetch("/api/providers").then(r => r.json()).then(setProviders).catch(() => setProviders([]));
    fetch("/api/session", { credentials: "same-origin" })
      .then(r => r.json())
      .then(data => {
        if (data.user) {
          setUser(data.user);
          setLoginOpen(false);
        }
      })
      .catch(() => {});
  }, []);

  const results = useMemo(() => providers.filter(p => !searched || isAvailable(p, date, time)), [providers, date, time, searched]);

  const search = () => {
    setSearched(true);
    setSelected(null);
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setLoginError("");

    const response = await fetch("/api/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginForm)
    });

    const data = await response.json().catch(() => ({}));
    setIsSubmitting(false);

    if (!response.ok) {
      setLoginError(data.error || "Credenciales inválidas.");
      return;
    }

    setUser(data.user);
    setLoginOpen(false);
  };

  const handleLogout = async () => {
    await fetch("/api/logout", { method: "POST", credentials: "same-origin" });
    setUser(null);
    setLoginOpen(true);
    setSelected(null);
  };

  return <>
    <style>{`
      .auth-shell {
        position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
        background: rgba(22, 32, 26, 0.48); backdrop-filter: blur(6px); z-index: 20;
      }
      .auth-card {
        width: min(460px, calc(100vw - 32px)); background: #fff; border-radius: 24px;
        box-shadow: 0 30px 80px rgba(10, 27, 23, 0.28); padding: 30px 26px 24px;
        border: 1px solid #edf0eb;
      }
      .auth-brand { display: inline-flex; align-items: center; font-family: "Playfair Display", serif; font-size: 28px; font-weight: 700; color: var(--green); }
      .auth-brand .house { margin-right: 10px; }
      .auth-card h2 { margin: 18px 0 8px; font-size: 30px; }
      .auth-card p { margin: 0 0 18px; color: #5d6d67; }
      .auth-field { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
      .auth-field input { border: 1px solid #dfe5df; border-radius: 12px; padding: 12px 14px; font-size: 15px; }
      .auth-actions { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
      .auth-submit { flex: 1; background: var(--green); color: white; border: none; border-radius: 12px; padding: 12px 18px; font-weight: 700; cursor: pointer; }
      .auth-demo { font-size: 12px; color: #64736d; margin-top: 14px; }
      .auth-error { margin: 0 0 12px; color: #bc4734; font-weight: 600; min-height: 20px; }
      .user-badge { display: inline-flex; align-items: center; gap: 8px; }
      .user-badge .dot { width: 8px; height: 8px; border-radius: 999px; background: #2e715d; }
    `}</style>
    <div className="app">
      <header>
        <div className="brand"><span className="house">⌂</span><span>Geovany<span>Calles</span></span></div>
        <nav>
          <a>Cómo funciona</a>
          <a>Ofrece tu servicio</a>
          {user ? <button className="login user-badge" onClick={handleLogout}><span className="dot"></span>{user.name}</button> : <button className="login" onClick={() => setLoginOpen(true)}>Ingresar</button>}
        </nav>
      </header>

      {loginOpen && !user && <div className="auth-shell"><div className="auth-card"><div className="auth-brand"><span className="house">⌂</span><span>Geovany</span></div><h2>Inicia sesión</h2><p>Accede a los servicios de limpieza y reserva con confianza.</p><form onSubmit={handleLogin}><div className="auth-error">{loginError}</div><div className="auth-field"><label>Correo electrónico</label><input type="email" value={loginForm.email} onChange={e => setLoginForm({ ...loginForm, email: e.target.value })} required /></div><div className="auth-field"><label>Contraseña</label><input type="password" value={loginForm.password} onChange={e => setLoginForm({ ...loginForm, password: e.target.value })} required /></div><div className="auth-actions"><button className="auth-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? "Ingresando..." : "Entrar"}</button></div></form><div className="auth-demo">Demo: admin@geovany.com / housekeeper123</div></div></div>}

      {!loginOpen && user && <main>
        <section className="intro"><div><p className="eyebrow">SERVICIOS DE CONFIANZA EN SAN SALVADOR</p><h1>Tu hogar, en <i>buenas manos.</i></h1><p className="subtitle">Hola, {user.name}. Encuentra a la persona ideal para cuidar y limpiar tu espacio.</p></div></section>
        <section className="search"><div className="field"><label>¿Dónde necesitas el servicio?</label><div>⌖ <span>San Salvador, El Salvador</span></div></div><div className="field"><label>Fecha</label><input type="date" value={date} onChange={e=>setDate(e.target.value)} /></div><div className="field"><label>Hora de inicio</label><input type="time" value={time} onChange={e=>setTime(e.target.value)} /></div><button className="find" onClick={search}>Buscar disponibilidad <span>→</span></button></section>
        <section className="content"><div className="results"><div className="results-head"><div><p className="muted">{searched && date && time ? `Disponibles para ${date} a las ${time}` : "PERSONAS DISPONIBLES"}</p><h2>{results.length} profesionales cerca de ti</h2></div><button className="filter">☷ Filtros</button></div><div className="cards">{results.map(p=><article className={'card '+(selected?.id===p.id?'selected':'')} key={p.id} onClick={()=>setSelected(p)}><img src={p.photo}/><div className="card-main"><div className="topline"><h3>{p.name}</h3><span>★ {p.rating}</span></div><p>{p.area} · {p.services.join(" · ")}</p><p className="availability">Disponible {p.days.map(d=>LABELS[d]).join(", ")}<br/><b>{p.start} – {p.end}</b></p></div><div className="price"><b>${p.fee}</b><span>/hora</span></div></article>)}</div>{!results.length&&<div className="empty">No hay profesionales para ese horario. Prueba otra hora o fecha.</div>}</div><aside><ProviderMap providers={results} selected={selected} onSelect={setSelected}/><div className="map-label">{results.length} servicios disponibles</div></aside></section></main>}
    </div>
  </>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
