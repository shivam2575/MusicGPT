import { useState } from 'react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
  
    try {
      console.log(username)
      console.log(password)

      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log('Login successful:', data.message);
        localStorage.setItem('isAuthenticated', 'true');
        window.location.href = '/chat';
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      console.error('Network error:', err);
      setError('Unable to connect to server');
    }
  };
  

  return (
    <div className="flex justify-center items-center h-screen bg-gray-900 text-white">
      <form
        onSubmit={handleLogin}
        className="bg-gray-800 p-8 rounded-lg shadow-lg w-96 space-y-6"
      >
        <h2 className="text-2xl font-bold text-center">MusicGPT Login</h2>

        {error && <p className="text-red-400 text-sm text-center">{error}</p>}

        <div>
          <label htmlFor="username" className="block text-sm font-medium">
            Username
          </label>
          <input
            type="text"
            id="username"
            className="w-full mt-1 p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring focus:ring-blue-500"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            type="password"
            id="password"
            className="w-full mt-1 p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring focus:ring-blue-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold"
        >
          Login
        </button>

        <button
        type="button"
        className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 rounded text-white font-semibold"
        onClick={() => window.location.href = '/signup'}
      >
        Sign Up
      </button>

      </form>
    </div>
  );
};

export default Login;
