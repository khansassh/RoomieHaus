// Example: Fetch greeting from Flask backend
fetch('http://localhost:5000/api/greeting') // Or 'http://backend:5000' when in Docker
  .then(response => response.json())
  .then(data => {
    console.log(data.greeting); // "Hello from RoomieHaus backend!"
    document.getElementById('greeting').innerText = data.greeting;
  })
  .catch(error => console.error('Error:', error));
