import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        CloudVideo
      </Link>
      <div className="navbar-links">
        <Link to="/">Principal</Link>
        {user ? (
          <>
            <Link to="/profile">Mi Perfil ({user.name})</Link>
            <button onClick={handleLogout} className="btn btn-secondary">
              Cerrar Sesion
            </button>
          </>
        ) : (
          <Link to="/auth" className="btn btn-primary">
            Ingresar / Registro
          </Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
