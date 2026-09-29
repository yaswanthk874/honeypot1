import { useState, useEffect } from 'react';
import { 
  Activity, 
  ShieldAlert, 
  Users, 
  Terminal,
  Server,
  Download
} from 'lucide-react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('live');
  const [logs, setLogs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = 'http://localhost:8000';

  const fetchData = async () => {
    try {
      const [logsRes, profilesRes] = await Promise.all([
        fetch(`${API_URL}/api/logs`),
        fetch(`${API_URL}/api/profiles`)
      ]);
      const logsData = await logsRes.json();
      const profilesData = await profilesRes.json();
      setLogs(logsData);
      setProfiles(profilesData);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const getBadgeClass = (classification) => {
    switch(classification) {
      case 'botnet': return 'badge-danger';
      case 'advanced hacker': return 'badge-danger';
      case 'script kiddie': return 'badge-warning';
      default: return 'badge-info';
    }
  };

  const renderLiveTraffic = () => (
    <div className="glass-panel" style={{animation: 'fade-in 0.3s ease-in'}}>
      <h2><Terminal size={20} /> Recent Attacks (<span className="live-indicator"></span>LIVE)</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Source IP</th>
              <th>Target Port</th>
              <th>Service</th>
              <th>Payload Snippet</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody>
            {logs.length > 0 ? logs.map(log => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleTimeString()}</td>
                <td style={{fontFamily: 'monospace'}}>{log.source_ip}</td>
                <td>{log.targeted_port}</td>
                <td><span className="badge badge-info">{log.service_mimicked}</span></td>
                <td style={{opacity: 0.7, fontFamily: 'monospace', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                  {log.payload || 'N/A'}
                </td>
                <td>
                  <span className={`badge ${getBadgeClass(log.attacker_profile)}`}>
                    {log.attacker_profile.toUpperCase()}
                  </span>
                </td>
              </tr>
            )) : <tr><td colSpan="6" style={{textAlign: 'center', padding: '2rem'}}>No attacks logged yet... listening.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderProfiles = () => (
    <div className="glass-panel" style={{animation: 'fade-in 0.3s ease-in'}}>
      <h2><Users size={20} /> Adversary Intelligence</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>IP Address</th>
              <th>First Seen</th>
              <th>Last Seen</th>
              <th>Total Attacks</th>
              <th>Frequent Ports</th>
              <th>Classification</th>
            </tr>
          </thead>
          <tbody>
             {profiles.length > 0 ? profiles.map(profile => (
              <tr key={profile.id}>
                <td style={{fontFamily: 'monospace', color: 'var(--accent-color)'}}>{profile.ip_address}</td>
                <td>{new Date(profile.first_seen).toLocaleString()}</td>
                <td>{new Date(profile.last_seen).toLocaleString()}</td>
                <td><strong>{profile.total_attacks}</strong></td>
                <td>{profile.frequent_ports}</td>
                <td>
                  <span className={`badge ${getBadgeClass(profile.classification)}`}>
                    {profile.classification.toUpperCase()}
                  </span>
                </td>
              </tr>
             )) : <tr><td colSpan="6" style={{textAlign: 'center', padding: '2rem'}}>No intelligence gathered yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );

  const exportReport = () => {
    // Basic CSV export logic
    const headers = ["IP", "Total Attacks", "Classification", "Ports"].join(",");
    const rows = profiles.map(p => `${p.ip_address},${p.total_attacks},${p.classification},${p.frequent_ports}`).join("\n");
    const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows;
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "threat_intelligence_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderReports = () => (
    <div className="glass-panel" style={{animation: 'fade-in 0.3s ease-in'}}>
       <h2><ShieldAlert size={20} /> Threat Intelligence Reporting</h2>
       <p style={{color: 'var(--text-secondary)', marginBottom: '1.5rem'}}>
         Generate portable intelligence reports for integration with SIEMs and automated defense systems.
       </p>
       
       <button 
          onClick={exportReport}
          style={{
            background: 'var(--accent-color)', 
            color: 'white', 
            border: 'none', 
            padding: '0.75rem 1.5rem', 
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontWeight: '600',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => e.target.style.background = 'var(--accent-hover)'}
          onMouseOut={(e) => e.target.style.background = 'var(--accent-color)'}
       >
         <Download size={18} /> Export as CSV
       </button>
    </div>
  );

  if (loading) return <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>Initializing Defense Systems...</div>;

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <ShieldAlert className="brand-icon" size={28} />
          <span>AegisNet</span>
        </div>
        
        <ul className="nav-links">
          <li className={`nav-item ${activeTab === 'live' ? 'active' : ''}`} onClick={() => setActiveTab('live')}>
            <Activity size={20} />
            Live Traffic
          </li>
          <li className={`nav-item ${activeTab === 'profiles' ? 'active' : ''}`} onClick={() => setActiveTab('profiles')}>
            <Users size={20} />
            Attacker Profiles
          </li>
          <li className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`} onClick={() => setActiveTab('reports')}>
            <Server size={20} />
            Threat Reports
          </li>
        </ul>
        
        <div style={{marginTop: 'auto', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.75rem'}}>
          Environment: Safe Isolation<br/>
          Status: <span style={{color: 'var(--success)'}}>Active</span>
        </div>
      </aside>

      <main className="main-content">
        <h1>Deception Dashboard</h1>
        
        <div className="dashboard-grid">
           <div className="glass-panel status-card">
              <span className="status-label">Total Attacks Logged</span>
              <span className="status-value">{logs.length}</span>
           </div>
           <div className="glass-panel status-card">
              <span className="status-label">Unique Adversary Profiles</span>
              <span className="status-value">{profiles.length}</span>
           </div>
           <div className="glass-panel status-card">
              <span className="status-label">Active Honeypots</span>
              <span className="status-value" style={{color: 'var(--success)'}}>3</span>
           </div>
        </div>

        {activeTab === 'live' && renderLiveTraffic()}
        {activeTab === 'profiles' && renderProfiles()}
        {activeTab === 'reports' && renderReports()}

      </main>
    </div>
  );
}

export default App;
