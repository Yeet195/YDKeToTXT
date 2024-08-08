document.addEventListener('DOMContentLoaded', function() {
	const parseButton = document.getElementById('parseButton');
	const resultElement = document.getElementById('result');
	const loadingSpinner = document.getElementById('loading-spinner');

	parseButton.addEventListener('click', () => {
		const ydkeUrl = document.getElementById('ydkeUrl').value;

		// Show the loading spinner
		loadingSpinner.style.display = 'block';
		resultElement.textContent = ''; // Clear previous result

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
				resultElement.textContent = `Error: ${data.error}`;
			} else {
				let resultText = "";
				for (const [category, names] of Object.entries(data)) {
					for (const [name, count] of Object.entries(names)) {
						resultText += `${count}x ${name}\n`;
					}
					resultText += "\n";
				}
				resultElement.textContent = resultText;
			}
		})
		.catch(error => {
			resultElement.textContent = `Fetch error: ${error}`;
		})
		.finally(() => {
			// Hide the loading spinner
			loadingSpinner.style.display = 'none';
		});
	});
});
