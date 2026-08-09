import { useState, useEffect, FormEvent } from 'react';

// --- TYPES ---
interface ServerStatus {
  status: 'online' | 'offline';
  latency: number | null;
  uptime?: string;
  minecraft_target?: string;
  version?: string;
  host?: string;
  port?: number;
}

interface ActionResponse {
  success: boolean;
  message: string;
}

export default function App() {
  // --- STATE ---
  const [currentRoute, setCurrentRoute] = useState<string>(window.location.pathname);
  const [success, setSuccess] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);
  
  // Admin & Dashboard Stats
  const [uptime, setUptime] = useState<string>('00:00:00');
  const [messagesSent, setMessagesSent] = useState<number>(0);
  const [startTime] = useState<string>(new Date().toISOString().replace('T', ' ').substring(0, 19));
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null);
  
  const serverAddress = `${process.env.REACT_APP_TARGET_HOST || 'localhost'}:${process.env.REACT_APP_TARGET_PORT || '36000'}`;
  const mcVersion = process.env.REACT_APP_MC_VERSION || 'v1.21.11';

  // Simple Router Sync
  useEffect(() => {
    const handlePopState = () => setCurrentRoute(window.location.pathname);
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentRoute(path);
    setSuccess(false);
    setErrorMessage(null);
    setLoginError(null);
  };

  // --- API ACTIONS ---
  const handleContactSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const subject = formData.get('subject') as string;
    const message = formData.get('message') as string;

    if (!subject || !message) {
      setErrorMessage('All fields are required.');
      return;
    }

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, message }),
      });
      
      if (res.ok) {
        setSuccess(true);
        setMessagesSent((prev) => prev + 1);
        setErrorMessage(null);
      } else {
        const data = await res.json();
        setErrorMessage(data.message || 'Error sending notification.');
      }
    } catch (err: any) {
      setErrorMessage(`Error sending notification: ${err.message}`);
    }
  };

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const password = formData.get('password') as string;

    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      if (res.ok) {
        navigate('/admin');
      } else {
        setLoginError('Incorrect password. Please try again.');
      }
    } catch (err) {
      setLoginError('Login failed. Please try again.');
    }
  };

  const handleAdminAction = async (action: 'flush' | 'reload') => {
    try {
      const res = await fetch('/api/admin/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const data: ActionResponse = await res.json();
      if (data.success && action === 'flush') {
        setMessagesSent(0);
      }
      alert(data.message);
    } catch (err) {
      alert('Action failed to execute.');
    }
  };

  // --- VIEWS ---
  if (currentRoute === '/login') {
    return (
      <div className="login-container">
        <h2>Admin Login</h2>
        {loginError && <p className="error">{loginError}</p>}
        <form onSubmit={handleLogin}>
          <input type="password" name="password" placeholder="Admin Password" required />
          <button type="submit">Login</button>
        </form>
        <button onClick={() => navigate('/')}>Back to Home</button>
      </div>
    );
  }

  if (currentRoute === '/admin') {
    return (
      <div className="admin-container">
        <h2>Admin Dashboard</h2>
        <p><strong>Uptime:</strong> {uptime}</p>
        <p><strong>Messages Sent:</strong> {messagesSent}</p>
        <p><strong>Start Time:</strong> {startTime}</p>
        <p><strong>Server Address:</strong> {serverAddress}</p>
        <p><strong>MC Version:</strong> {mcVersion}</p>
        
        <div className="admin-actions">
          <button onClick={() => handleAdminAction('flush')}>Flush Metrics Cache</button>
          <button onClick={() => handleAdminAction('reload')}>Reload Config</button>
          <button onClick={() => navigate('/logout')}>Logout</button>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <h1>Welcome to {serverAddress}</h1>
      <p>Minecraft Version: {mcVersion}</p>
      
      {success && <p className="success">Message sent successfully!</p>}
      {errorMessage && <p className="error">{errorMessage}</p>}

      <form onSubmit={handleContactSubmit}>
        <input type="text" name="subject" placeholder="Subject" required />
        <textarea name="message" placeholder="Message" required />
        <button type="submit">Send Notification</button>
      </form>

      <button onClick={() => navigate('/login')}>Admin Login</button>
    </div>
  );
}