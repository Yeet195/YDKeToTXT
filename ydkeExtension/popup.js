document.addEventListener('DOMContentLoaded', function() {
	document.getElementById('parseButton').addEventListener('click', () => {
	  const ydkeUrl = document.getElementById('ydkeUrl').value;
	  fetch('https://ydke-txt-45790110621c.herokuapp.com//process', {  // Update URL here
		method: 'POST',
		headers: {
		  'Content-Type': 'application/json'
		},
		body: JSON.stringify({ url: ydkeUrl })
	  })
	  .then(response => response.json())
	  .then(data => {
		if (data.error) {
		  document.getElementById('result').textContent = `Error: ${data.error}`;
		} else {
		  let resultText = "";
		  for (const [category, names] of Object.entries(data)) {
			for (const [name, count] of Object.entries(names)) {
			  resultText += `${count}x ${name}\n`;
			}
			resultText += "\n";
		  }
		  document.getElementById('result').textContent = resultText;
		}
	  })
	  .catch(error => {
		document.getElementById('result').textContent = `Fetch error: ${error}`;
	  });
	});
  });
  