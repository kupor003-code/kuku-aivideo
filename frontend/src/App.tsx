import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import WorkspaceSciFiV2 from './pages/WorkspaceSciFiV2';
import ProjectList from './pages/ProjectList';
import './App.css';

function NavBar() {
  const location = useLocation();

  const links = [
    { path: '/projects', label: '📁 项目' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <Link to="/projects" style={{textDecoration: 'none', color: 'inherit'}}>
            🎬 AI短剧创作平台 V2
          </Link>
        </div>
        <div className="navbar-nav">
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <NavBar />
        <Routes>
          <Route path="/projects" element={<ProjectList />} />
          <Route path="/workspace/:projectId" element={<WorkspaceSciFiV2 />} />
          <Route path="/" element={<ProjectList />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
