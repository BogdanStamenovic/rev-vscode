import './styles.css';
import { App } from './app';

function boot(): void {
  const root = document.getElementById('app') ?? document.body.appendChild(document.createElement('div'));
  root.id = 'app';
  new App(root);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
