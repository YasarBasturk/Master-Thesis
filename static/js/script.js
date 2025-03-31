document.addEventListener('DOMContentLoaded', function() {
    const processImageForm = document.getElementById('processImageForm');
    const saveBtn = document.getElementById('saveBtn');
    const spinner = document.getElementById('spinner');
    const imageContainer = document.getElementById('imageContainer');
    const originalImageContainer = document.getElementById('originalImageContainer');
    const textResults = document.getElementById('textResults');
    const saveResult = document.getElementById('saveResult');
    const processResult = document.getElementById('processResult');
    
    let ocrData = null;
    let editedItems = new Set();
    
    // If template is available, show a message
    if (window.hasTemplate) {
        console.log('Template is loaded. Only non-template text will be editable.');
    }

    // Handle image processing form
    if (processImageForm) {
        processImageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const imageFile = document.getElementById('imageFile').files[0];
            
            if (!imageFile) {
                alert('Image file is required');
                return;
            }
            
            const formData = new FormData();
            formData.append('image_file', imageFile);
            
            // Show loading spinner and processing message
            spinner.classList.remove('d-none');
            processResult.innerHTML = '<div class="alert alert-info"><i class="bi bi-hourglass-split"></i> Processing your image, please wait...</div>';
            
            // Clear previous data
            textResults.innerHTML = '<p class="text-muted">Processing image...</p>';
            imageContainer.innerHTML = '<p class="text-muted">Processing image...</p>';
            originalImageContainer.innerHTML = '<p class="text-muted">Processing image...</p>';
            
            fetch('/process_image', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Server error: ' + response.status);
                    }).catch(() => {
                        // If we can't parse the JSON, just throw the HTTP error
                        throw new Error('Network response was not ok: ' + response.status);
                    });
                }
                return response.json();
            })
            .then(data => {
                // Hide spinner
                spinner.classList.add('d-none');
                
                // Even with a successful HTTP response, check if the data indicates an error
                if (!data.success) {
                    throw new Error(data.error || 'Unknown server error');
                }
                
                // Save OCR data
                if (!data.ocr_results || !Array.isArray(data.ocr_results)) {
                    throw new Error('Invalid OCR data received from server');
                }
                
                ocrData = data.ocr_results;
                
                // Display original and annotated images
                if (data.original_image) {
                    displayOriginalImage(data.original_image);
                }
                
                if (data.image) {
                    displayAnnotatedImage(data.image);
                }
                
                // Display text results (only handwritten/editable text)
                displayTextResults(ocrData);
                
                // Enable save button
                saveBtn.disabled = false;
                
                // Show success message
                processResult.innerHTML = `<div class="alert alert-success">
                    <i class="bi bi-check-circle"></i> Image processed successfully!
                    <br>
                    <small>${ocrData.length} text elements detected</small>
                </div>`;
            })
            .catch(error => {
                spinner.classList.add('d-none');
                console.error('Error:', error);
                processResult.innerHTML = `<div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Error processing image: ${error.message}
                </div>`;
                
                // Reset containers
                textResults.innerHTML = '<p class="text-muted">Upload an image to view and edit detected text</p>';
                imageContainer.innerHTML = '<p class="text-muted">Upload an image to see annotated results</p>';
                originalImageContainer.innerHTML = '<p class="text-muted">Upload an image to see it here</p>';
            });
        });
    }

    // Display original image
    function displayOriginalImage(base64Image) {
        if (!base64Image) {
            originalImageContainer.innerHTML = '<p class="text-danger">Unable to load original image</p>';
            return;
        }
        
        originalImageContainer.innerHTML = `
            <div class="img-container">
                <img src="data:image/jpeg;base64,${base64Image}" alt="Original Image" class="img-fluid">
            </div>
        `;
    }

    // Display annotated image
    function displayAnnotatedImage(base64Image) {
        if (!base64Image) {
            imageContainer.innerHTML = '<p class="text-danger">Unable to load annotated image</p>';
            return;
        }
        
        imageContainer.innerHTML = `
            <div class="img-container">
                <img src="data:image/jpeg;base64,${base64Image}" alt="Annotated Image" class="img-fluid">
                <div class="image-legend mt-3">
                    <div class="d-flex align-items-center mb-2">
                        <span class="legend-color-box" style="background-color: rgb(0, 255, 0);"></span>
                        <span class="ms-2">Editable text (handwritten, not in template)</span>
                    </div>
                    <div class="d-flex align-items-center">
                        <span class="legend-color-box" style="background-color: rgb(255, 0, 0);"></span>
                        <span class="ms-2">Non-editable text (printed, in template)</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Display text results with editing capability
    function displayTextResults(results) {
        if (!results || results.length === 0) {
            textResults.innerHTML = '<div class="no-results">No OCR results available</div>';
            return;
        }
        
        // Clean up results - ensure all items have valid text
        results.forEach(item => {
            if (!item.text || item.text === 'undefined' || item.text === 'NO_TEXT_DETECTED') {
                item.text = '';
                console.log('Fixed item with missing/undefined text:', item);
            }
        });
        
        // Filter out template items - only keep handwritten/editable items
        const editableItems = results.filter(item => {
            // Trust the server's handwritten flag without additional checks
            return item.handwritten === true;
        });
        
        // Log the filtering results for debugging
        console.log("All items:", results);
        console.log("Filtered editable items:", editableItems);
        
        // Count how many handwritten (editable) items we have
        const handwrittenCount = editableItems.length;
        
        console.log(`Total items: ${results.length}, Editable items: ${handwrittenCount}`);
        
        // If we have a template but no handwritten text, show a helpful message
        if (handwrittenCount === 0 && window.hasTemplate) {
            textResults.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle-fill"></i>
                    <strong>No editable text found.</strong> All detected text appears to be part of the template.
                    <br>
                    If you were expecting editable content, try one of these:
                    <ul>
                        <li>Adjust the template matching threshold in the backend</li>
                        <li>Check if the uploaded image has the same orientation as the template</li>
                        <li>Verify that the OCR has correctly detected handwritten content</li>
                    </ul>
                </div>
            `;
            return;
        }
        
        // Add filter controls and information
        let html = `
            <div class="mb-4">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 
                    <strong>Template-Based Mode:</strong> 
                    ${window.hasTemplate ? 
                      'Only text that doesn\'t match the template is shown below and can be edited.' : 
                      'No template found. All text is displayed and can be toggled for editing.'}
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <h4>Editable Text Items (${handwrittenCount})</h4>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="toggleEdited" ${editedItems.size > 0 ? 'checked' : ''}>
                        <label class="form-check-label" for="toggleEdited">Show only edited items</label>
                    </div>
                </div>
            </div>
            <div class="row" id="textItemsContainer">
        `;
        
        // Only display handwritten/editable items
        editableItems.forEach((item, i) => {
            // Get the original index from the full results array
            const index = results.indexOf(item);
            const isEdited = editedItems.has(index);
            const editedClass = isEdited ? 'text-item-edited' : '';
            
            html += `
                <div class="col-md-6 col-lg-4 text-item-container" 
                     data-edited="${isEdited}" 
                     data-index="${index}">
                    <div class="text-item text-item-handwritten ${editedClass}" data-index="${index}">
                        <div class="d-flex justify-content-between align-items-start">
                            <span class="text-index">Item #${index}</span>
                            <button class="btn btn-sm btn-primary btn-edit" data-index="${index}">Edit</button>
                        </div>
                        <div class="text-content mt-2">
                            <div class="text-type-badge badge-handwritten">
                                Editable
                            </div>
                            ${item.text || '<i>Empty text</i>'}
                        </div>
                        <div class="text-coords">Region: ${JSON.stringify(item.text_region)}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        textResults.innerHTML = html;
        
        // Add toggle functionality for edited items
        const toggleEditedCheck = document.getElementById('toggleEdited');
        if (toggleEditedCheck) {
            toggleEditedCheck.addEventListener('change', function() {
                filterEditedItems(this.checked);
            });
            
            // Initial state based on checkbox
            if (toggleEditedCheck.checked) {
                filterEditedItems(true);
            }
        }
        
        // Add event listeners to edit buttons
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                const item = ocrData[index];
                
                const textItem = document.querySelector(`.text-item[data-index="${index}"]`);
                const textContent = textItem.querySelector('.text-content');
                
                // Get the current text
                const currentText = item.text;
                
                // Replace content with textarea
                textContent.innerHTML = `
                    <div class="text-type-badge badge-handwritten">Editable</div>
                    <textarea class="form-control mb-2">${currentText}</textarea>
                    <div class="d-flex justify-content-end">
                        <button class="btn btn-sm btn-secondary me-2 btn-cancel">Cancel</button>
                        <button class="btn btn-sm btn-success btn-save">Save</button>
                    </div>
                `;
                
                // Add event listeners to cancel and save buttons
                textContent.querySelector('.btn-cancel').addEventListener('click', function() {
                    textContent.innerHTML = `
                        <div class="text-type-badge badge-handwritten">Editable</div>
                        ${currentText}
                    `;
                });
                
                textContent.querySelector('.btn-save').addEventListener('click', function() {
                    const newText = textContent.querySelector('textarea').value.trim();
                    if (newText === '') return;
                    
                    // Show spinner
                    spinner.classList.remove('d-none');
                    
                    // Send update to server
                    fetch('/update_text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            index: index,
                            text: newText
                        })
                    })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => {
                                throw new Error(data.error || 'Error updating text');
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Hide spinner
                        spinner.classList.add('d-none');
                        
                        if (data.success) {
                            // Update local data
                            ocrData[index].text = newText;
                            
                            // Update UI
                            textContent.innerHTML = `
                                <div class="text-type-badge badge-handwritten">Editable</div>
                                ${newText}
                            `;
                            textItem.classList.add('text-item-edited');
                            
                            // Track edited items
                            editedItems.add(index);
                            
                            // Update container attribute for filtering
                            const container = textItem.closest('.text-item-container');
                            if (container) {
                                container.dataset.edited = 'true';
                            }
                            
                            // Update image
                            displayAnnotatedImage(data.image);
                        } else {
                            alert('Error updating text');
                        }
                    })
                    .catch(error => {
                        spinner.classList.add('d-none');
                        console.error('Error:', error);
                        alert(error.message);
                    });
                });
            });
        });
    }
    
    // Filter to show only edited items
    function filterEditedItems(showOnlyEdited) {
        const containers = document.querySelectorAll('.text-item-container');
        containers.forEach(container => {
            if (showOnlyEdited) {
                container.style.display = container.dataset.edited === 'true' ? '' : 'none';
            } else {
                container.style.display = '';
            }
        });
    }

    // Handle save button
    saveBtn.addEventListener('click', function() {
        if (!ocrData) {
            alert('No data to save');
            return;
        }
        
        // Show spinner
        spinner.classList.remove('d-none');
        
        // Send save request
        fetch('/save', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            // Hide spinner
            spinner.classList.add('d-none');
            
            if (data.success) {
                saveResult.innerHTML = `Successfully saved to: <strong>${data.path}</strong>`;
                saveResult.className = 'success';
            } else {
                saveResult.innerHTML = `Error: ${data.error}`;
                saveResult.className = 'error';
            }
        })
        .catch(error => {
            spinner.classList.add('d-none');
            console.error('Error:', error);
            saveResult.innerHTML = `Error: ${error.message}`;
            saveResult.className = 'error';
        });
    });
}); 