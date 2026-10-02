import React from 'react';
import { Link } from 'react-router-dom';

const VideoCard = ({ video }) => {
  const formattedDate = video.created_at
    ? new Date(video.created_at).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : '';

  const ownerName = video.owner ? video.owner.name : 'Usuario';

  return (
    <Link to={`/watch/${video.id}`} className="video-card">
      <div className="video-thumbnail-wrapper">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="video-thumbnail"
          loading="lazy"
        />
      </div>
      <div className="video-info">
        <h3 className="video-title">{video.title}</h3>
        <div className="video-meta">
          <span>Publicado por: {ownerName}</span>
          <span>{video.views} vistas • {formattedDate}</span>
        </div>
      </div>
    </Link>
  );
};

export default VideoCard;
