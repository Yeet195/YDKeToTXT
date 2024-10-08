document.addEventListener('DOMContentLoaded', function() {
	const parseButton = document.getElementById('parseButton');
	const resultElement = document.getElementById('result');
	const loadingSpinner = document.getElementById('loading-spinner');
	const copyMessage = document.getElementById('copy-message');
	const contentElement = document.getElementById('content');

	parseButton.addEventListener('click', () => {
		const ydkeUrl = document.getElementById('ydkeUrl').value;

		// Hide the content and show the loading spinner
		contentElement.style.display = 'none';
		loadingSpinner.style.display = 'flex';
		copyMessage.style.display = 'none';
		resultElement.textContent = ''; // Clear previous result

		fetch('https://ydke-txt-45790110621c.herokuapp.com/process', {
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

				// Copy the result to the clipboard
				navigator.clipboard.writeText(resultText).then(() => {
					// Show the copy message
					copyMessage.style.display = 'block';
				}).catch(err => {
					console.error('Could not copy text: ', err);
				});
			}
		})
		.catch(error => {
			resultElement.textContent = `Fetch error: ${error}`;
		})
		.finally(() => {
			// Hide the loading spinner and show the content again
			loadingSpinner.style.display = 'none';
			contentElement.style.display = 'block';
		});
	});
});
