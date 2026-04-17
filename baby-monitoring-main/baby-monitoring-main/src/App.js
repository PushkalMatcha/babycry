import React, { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

function App() {
  const [user, setUser] = useState(false);

  return (
    <div>
      {user ? <Dashboard /> : <Login setUser={setUser} />}
    </div>
  );
}

export default App;