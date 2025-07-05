import { useState } from 'react';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); 

  const handleSignup = async (e) => {
    e.preventDefault();
    setMessage('');

    if (password !== confirmPassword) {
      setMessage('Passwords do not match.');
      setMessageType('error');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        setMessage('Account created successfully. You can now log in.');
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || 'Sign up failed');
        setMessageType('error');
      }
    } catch (err) {
      console.error('Network error:', err);
      setMessage('Server is unreachable.');
      setMessageType('error');
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-900 text-white">
      <form
        onSubmit={handleSignup}
        className="bg-gray-800 p-8 rounded-lg shadow-lg w-96 space-y-6"
      >
        <h2 className="text-2xl font-bold text-center">Sign Up</h2>

        {message && (
        <p
            className={`text-sm text-center ${
            messageType === 'error' ? 'text-red-400' : 'text-green-400'
            }`}
        >
            {message}
        </p>
        )}


        <div>
          <label htmlFor="username" className="block text-sm font-medium">
            Username
          </label>
          <input
            type="text"
            id="username"
            className="w-full mt-1 p-2 rounded bg-gray-700 text-white"
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
            className="w-full mt-1 p-2 rounded bg-gray-700 text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium">
            Confirm Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            className="w-full mt-1 p-2 rounded bg-gray-700 text-white"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 rounded text-white font-semibold"
        >
          Sign Up
        </button>

        <p
          className="text-sm text-center text-blue-400 cursor-pointer"
          onClick={() => window.location.href = '/'}
        >
          Already have an account? Log in
        </p>
      </form>
    </div>
  );
};

export default Signup;
