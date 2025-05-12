import { useState, useEffect } from 'react';
    import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

    const App = () => {
      const [user, setUser] = useState(null);

      useEffect(() => {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.ready();
          setUser(window.Telegram.WebApp.initDataUnsafe.user);
        }
      }, []);

      return (
        <BrowserRouter>
          <div className="container mx-auto p-4">
            <nav className="bg-blue-500 text-white p-4 rounded mb-8">
              <ul className="flex space-x-4 justify-center">
                <li><Link to="/">Home</Link></li>
                <li><Link to="/gallery">NFT Gallery</Link></li>
              </ul>
            </nav>
            <Routes>
              <Route path="/" element={<h1>Welcome to TON Game!</h1>} />
              <Route path="/gallery" element={<h1>NFT Gallery</h1>} />
            </Routes>
          </div>
        </BrowserRouter>
      );
    };

    export default App;
