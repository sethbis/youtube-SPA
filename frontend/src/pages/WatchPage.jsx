import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { videoService, commentService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const WatchPage = () => {
  const { id } = useParams();
  const { user } = useAuth();

  const [video, setVideo] = useState(null);
  const [comments, setComments] = useState([]);
  const [recommended, setRecommended] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadVideoData = async () => {
      setLoading(true);
      setError('');
      try {
        // Cargar video
        const videoRes = await videoService.getVideoById(id);
        setVideo(videoRes.data);

        // Cargar comentarios
        const commentsRes = await commentService.getComments(id);
        setComments(commentsRes.data);

        // Cargar videos recomendados dinamicamente excluyendo el actual
        const recRes = await videoService.getVideos({ exclude_id: id, limit: 6 });
        setRecommended(recRes.data);
      } catch (err) {
        setError('Error al cargar la informacion del video.');
      } finally {
        setLoading(false);
      }
    };

    loadVideoData();
  }, [id]);

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmittingComment(true);
    try {
      const response = await commentService.addComment(id, newComment.trim());
      setComments([...comments, response.data]);
      setNewComment('');
    } catch (err) {
      alert('Error al publicar el comentario.');
    } finally {
      setSubmittingComment(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <p>Cargando reproductor de video...</p>
      </div>
    );
  }

  if (error || !video) {
    return (
      <div className="container">
        <div className="error-banner">{error || 'Video no encontrado.'}</div>
        <Link to="/" className="btn btn-secondary">Volver al inicio</Link>
      </div>
    );
  }

  const ownerName = video.owner ? video.owner.name : 'Usuario';
  const formattedDate = video.created_at
    ? new Date(video.created_at).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : '';

  return (
    <div className="watch-container">
      {/* Columna Principal: Reproductor, Info y Comentarios */}
      <div className="main-content">
        <div className="player-wrapper">
          <video
            src={video.video_url}
            controls
            autoPlay
            className="player-video"
          >
            Tu navegador no soporta el elemento de video.
          </video>
        </div>

        <div className="video-details">
          <h1>{video.title}</h1>
          <div className="video-stats">
            <div>
              <strong>{ownerName}</strong>
            </div>
            <div>
              <span>{video.views} vistas</span> • <span>{formattedDate}</span>
            </div>
          </div>

          {video.description && (
            <div className="video-description-box">
              {video.description}
            </div>
          )}
        </div>

        {/* Seccion de Comentarios */}
        <div className="comments-section">
          <h3>Comentarios ({comments.length})</h3>

          {user ? (
            <form onSubmit={handleCommentSubmit} className="comment-form">
              <textarea
                className="form-textarea"
                placeholder="Escribe un comentario publico..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                required
              />
              <button
                type="submit"
                className="btn btn-primary"
                style={{ alignSelf: 'flex-start' }}
                disabled={submittingComment}
              >
                {submittingComment ? 'Publicando...' : 'Comentar'}
              </button>
            </form>
          ) : (
            <p style={{ margin: '1rem 0', color: '#aaaaaa' }}>
              <Link to="/auth" style={{ color: '#ff3344', textDecoration: 'underline' }}>
                Inicia sesion
              </Link>{' '}
              para dejar un comentario.
            </p>
          )}

          <div className="comment-list">
            {comments.map((comm) => (
              <div key={comm.id} className="comment-item">
                <div className="comment-header">
                  <span className="comment-author">
                    {comm.author ? comm.author.name : 'Usuario'}
                  </span>
                  <span>
                    {comm.created_at ? new Date(comm.created_at).toLocaleDateString('es-ES') : ''}
                  </span>
                </div>
                <p style={{ color: '#e0e0e0', fontSize: '0.9rem' }}>{comm.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Columna Lateral: Videos Recomendados */}
      <div className="sidebar">
        <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Videos Recomendados</h3>
        <div className="recommended-list">
          {recommended.length === 0 ? (
            <p style={{ color: '#888888', fontSize: '0.9rem' }}>No hay recomendaciones adicionales.</p>
          ) : (
            recommended.map((rec) => (
              <Link to={`/watch/${rec.id}`} key={rec.id} className="rec-video-card">
                <img
                  src={rec.thumbnail_url}
                  alt={rec.title}
                  className="rec-thumbnail"
                />
                <div className="rec-info">
                  <h4 className="rec-title">{rec.title}</h4>
                  <div className="rec-meta">
                    <div>{rec.owner ? rec.owner.name : 'Usuario'}</div>
                    <div>{rec.views} vistas</div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default WatchPage;
