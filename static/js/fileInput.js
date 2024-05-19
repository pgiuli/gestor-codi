document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('dropzone-file');
  const fileInputText = document.getElementById('dropzone-text');

  console.log(fileInput);

  fileInput.addEventListener('change', (e) => {
    fileInputText.innerText = e.target.files[0].name;
  });
});