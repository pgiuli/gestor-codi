document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.querySelector('#toggle-theme');

  if (!themeToggle) { 
    throw new Error('No #toggle-theme element found');
  }

  const currentTheme = localStorage.getItem('theme') || 'light';

  if (currentTheme === 'dark') {
    document.documentElement.classList.add('dark');
  }

  themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
  });
});