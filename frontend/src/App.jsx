import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import WatchPage from './pages/WatchPage';
import ProfilePage from './pages/ProfilePage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-root">
          <Navbar />
          <main>
            <Routes>
              {/* Pagina 2: Principal */}
              <Route path="/" element={<HomePage />} />
              {/* Pagina 1: Registro / Login */}
              <Route path="/auth" element={<AuthPage />} />
              {/* Pagina 3: Reproductor */}
              <Route path="/watch/:id" element={<WatchPage />} />
              {/* Pagina 4: Perfil del usuario */}
              <Route path="/profile" element={<ProfilePage />} />
              {/* Ruta por defecto */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
