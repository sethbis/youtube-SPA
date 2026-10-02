import React, { useEffect, useState } from 'react';
import { videoService } from '../services/api';
import VideoCard from '../components/VideoCard';

const HomePage = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const response = await videoService.getVideos();
        setVideos(response.data);
      } catch (err) {
        setError('No fue posible cargar los videos de la plataforma.');
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, []);

  return (
    <div className="container">
      <h2 style={{ marginBottom: '1.5rem', fontWeight: 600 }}>Videos Disponibles</h2>

      {loading && <p>Cargando catalogo de videos...</p>}
      {error && <div className="error-banner">{error}</div>}

      {!loading && !error && videos.length === 0 && (
        <p style={{ color: '#888888' }}>
          No hay videos publicados todavia. Inicia sesion y publica el primero desde tu perfil.
        </p>
      )}

      <div className="video-grid">
        {videos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </div>
  );
};

export default HomePage;
