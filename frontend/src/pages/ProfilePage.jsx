import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { videoService, authService } from '../services/api';

const ProfilePage = () => {
  const { user, token, refreshUserData } = useAuth();
  const navigate = useNavigate();

  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Formulario de publicacion
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [thumbFile, setThumbFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Modal de edicion
  const [editingVideo, setEditingVideo] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/auth');
      return;
    }
    loadUserVideos();
  }, [token, user?.id]);

  const loadUserVideos = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const response = await videoService.getVideos({ user_id: user.id });
      setVideos(response.data);
      await refreshUserData();
    } catch (err) {
      setError('Error al cargar la lista de videos del usuario.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!videoFile || !thumbFile) {
      setError('Por favor selecciona tanto el archivo de video como la miniatura.');
      return;
    }

    // Validacion de extension de video (MP4)
    if (!videoFile.name.toLowerCase().endsWith('.mp4')) {
      setError('El formato del video debe ser MP4.');
      return;
    }

    // Validacion de tamano de video (max 100MB)
    if (videoFile.size > 100 * 1024 * 1024) {
      setError('El tamano del video no debe superar los 100 MB.');
      return;
    }

    // Validacion de extension de miniatura (JPG, JPEG, PNG)
    const validThumb = /\.(jpg|jpeg|png)$/i.test(thumbFile.name);
    if (!validThumb) {
      setError('La miniatura debe tener formato JPG, JPEG o PNG.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('video_file', videoFile);
    formData.append('thumbnail_file', thumbFile);

    setUploading(true);
    try {
      await videoService.uploadVideo(formData);
      setSuccess('Video publicado exitosamente en la plataforma.');
      setTitle('');
      setDescription('');
      setVideoFile(null);
      setThumbFile(null);
      // Reset file input elements in DOM
      e.target.reset();
      await loadUserVideos();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al publicar el video en S3/RDS.';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (videoId) => {
    const confirmDelete = window.confirm('Deseas eliminar permanentemente este video?');
    if (!confirmDelete) return;

    try {
      await videoService.deleteVideo(videoId);
      setSuccess('Video eliminado exitosamente.');
      await loadUserVideos();
    } catch (err) {
      setError('No fue posible eliminar el video.');
    }
  };

  const openEditModal = (video) => {
    setEditingVideo(video);
    setEditTitle(video.title);
    setEditDesc(video.description || '');
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!editingVideo) return;

    setUpdating(true);
    try {
      await videoService.updateVideo(editingVideo.id, {
        title: editTitle,
        description: editDesc,
      });
      setSuccess('Informacion del video actualizada correctamente.');
      setEditingVideo(null);
      await loadUserVideos();
    } catch (err) {
      setError('Error al actualizar la informacion del video.');
    } finally {
      setUpdating(false);
    }
  };

  if (!user) return null;

  return (
    <div className="container">
      {/* Informacion Basica del Usuario */}
      <div className="profile-header">
        <h2>Perfil de Usuario</h2>
        <div className="profile-stats">
          <div>
            <strong>Nombre:</strong> {user.name}
          </div>
          <div>
            <strong>Correo:</strong> {user.email}
          </div>
          <div>
            <strong>Videos Publicados:</strong> {videos.length}
          </div>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{success}</div>}

      {/* Formulario de Publicacion de Video */}
      <div style={{ backgroundColor: '#1a1a1a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #2e2e2e', marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Publicar Nuevo Video</h3>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Titulo del Video</label>
            <input
              type="text"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="Ingresa el titulo"
            />
          </div>

          <div className="form-group">
            <label>Descripcion</label>
            <textarea
              className="form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detalles sobre el contenido del video..."
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div className="form-group">
              <label>Archivo de Video (MP4, max 100 MB)</label>
              <input
                type="file"
                accept="video/mp4"
                className="form-input"
                onChange={(e) => setVideoFile(e.target.files[0])}
                required
              />
            </div>
            <div className="form-group">
              <label>Miniatura (JPG, JPEG, PNG)</label>
              <input
                type="file"
                accept="image/jpeg,image/png,image/jpg"
                className="form-input"
                onChange={(e) => setThumbFile(e.target.files[0])}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading}
          >
            {uploading ? 'Subiendo archivos a S3...' : 'Publicar Video'}
          </button>
        </form>
      </div>

      {/* Lista de Videos Subidos */}
      <h3 style={{ marginBottom: '1rem' }}>Mis Videos Subidos</h3>
      {loading && <p>Cargando lista de videos...</p>}

      {!loading && videos.length === 0 && (
        <p style={{ color: '#888888' }}>Aun no has publicado videos.</p>
      )}

      <div>
        {videos.map((vid) => (
          <div key={vid.id} className="user-video-item">
            <div className="user-video-details">
              <img
                src={vid.thumbnail_url}
                alt={vid.title}
                className="user-video-thumb"
              />
              <div>
                <h4 style={{ fontSize: '1rem', marginBottom: '0.2rem' }}>{vid.title}</h4>
                <span style={{ fontSize: '0.85rem', color: '#aaaaaa' }}>
                  {vid.views} vistas • {new Date(vid.created_at).toLocaleDateString('es-ES')}
                </span>
              </div>
            </div>

            <div className="user-video-actions">
              <Link to={`/watch/${vid.id}`} className="btn btn-secondary">
                Ver
              </Link>
              <button
                onClick={() => openEditModal(vid)}
                className="btn btn-secondary"
              >
                Editar
              </button>
              <button
                onClick={() => handleDelete(vid.id)}
                className="btn btn-danger"
              >
                Eliminar
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de Actualizacion de Informacion de Video */}
      {editingVideo && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ marginBottom: '1rem' }}>Actualizar Video</h3>
            <form onSubmit={handleUpdate}>
              <div className="form-group">
                <label>Titulo</label>
                <input
                  type="text"
                  className="form-input"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Descripcion</label>
                <textarea
                  className="form-textarea"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', gap: '0.8rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setEditingVideo(null)}
                  className="btn btn-secondary"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={updating}
                >
                  {updating ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
