// Navbar.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebookF, faLinkedinIn, faInstagram } from '@fortawesome/free-brands-svg-icons';

const Navbar = () => {
  return (
    <header className= "z-50 overflow-hidden" id="top" style={{ padding: '1rem 4vw', backgroundColor: '#ffffff' }}>
      <div style={{ maxWidth: '100%', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2rem' }}>
        
        {/* Logo */}
        <div>
          <a href="https://tenstep.fr/en/tenstep-2">
            <img
              src="https://tenstep.fr/wp-content/uploads/2024/02/Tenstep-logo-Color-H-01.svg"
              alt="Tenstep Logo"
              style={{ height: '2.5rem' }}
            />
          </a>
        </div>
        
        {/* Navigation Links */}
        <nav aria-label="Main Menu" style={{ flex: 1, textAlign: 'center' }}>
          <ul style={{ display: 'inline-flex', listStyle: 'none', gap: '2rem', margin: 0, padding: 0 }}>
            <li><a href="/" style={{ color: '#1d2f6f', fontWeight: '500', textDecoration: 'none' }}>Home</a></li>
            <li><a href="/about" style={{ color: '#1d2f6f', textDecoration: 'none', fontWeight: '500' }}>About us</a></li>
            <li><a href="/training" style={{ color: '#1d2f6f', textDecoration: 'none', fontWeight: '500' }}>Training</a></li>
            <li><a href="/solutions" style={{ color: '#1d2f6f', textDecoration: 'none', fontWeight: '500' }}>Solutions</a></li>
            <li><a href="/chat_with_expert" style={{ color: '#d22', textDecoration: 'none', fontWeight: 'bold' }}>Chat with our Expert</a></li>
            <li><a href="/contact" style={{ color: '#1d2f6f', textDecoration: 'none', fontWeight: '500' }}>Contact</a></li>
          </ul>
        </nav>
        
        {/* Social Icons and Language */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <a href="https://facebook.com" style={{ color: '#1d2f6f', fontSize: '1.25rem', textDecoration: 'none' }}>
            <FontAwesomeIcon icon={faFacebookF} />
          </a>
          <a href="https://linkedin.com" style={{ color: '#1d2f6f', fontSize: '1.25rem', textDecoration: 'none' }}>
            <FontAwesomeIcon icon={faLinkedinIn} />
          </a>
          <a href="https://instagram.com" style={{ color: '#1d2f6f', fontSize: '1.25rem', textDecoration: 'none' }}>
            <FontAwesomeIcon icon={faInstagram} />
          </a>
          <span style={{ color: '#1d2f6f', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <img
              src="https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg"
              alt="British Flag"
              style={{ width: '1.5rem', height: '1rem' }}
            />
            English
          </span>
        </div>
      </div>
      
    </header>
  );
};

export default Navbar;
