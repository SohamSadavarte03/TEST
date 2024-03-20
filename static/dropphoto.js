const dropArea = document.getElementById('drop-area');

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

// Highlight drop area when a draggable item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, highlight, false);
});

// Unhighlight drop area when a draggable item leaves it
['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, unhighlight, false);
});

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight() {
  dropArea.classList.add('highlight');
}

function unhighlight() {
  dropArea.classList.remove('highlight');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  
    // Print names of dropped files to console
    // for (let i = 0; i < files.length; i++) {
    //   console.log('Dropped file:', files[i].name);
    // }
  }


let images = [];
let deletedImages = [];

function handleFiles(files) {
    // for (let i = 0; i < files.length; i++) {
    //   console.log('Dropped file:', files[i].name);
    // }
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function() {
          images.push({file: file, dataUrl: reader.result});
          renderImages();
        }
        reader.readAsDataURL(file);
      }
    }
  }
  
function renderImages() {
  const previewArea = $('#image-preview');
  previewArea.empty();
  images.forEach((image, index) => {
    const imgElement = $('<img class="preview-img">').attr('src', image.dataUrl);
    const deleteBtn = $('<button class="delete-btn">X</button>').click(() => {
      images.splice(index, 1);
      deletedImages.push(image);
      renderImages();
    });
    previewArea.append($('<div class="preview-container">').append(imgElement, deleteBtn));
  });
}

$('#upload-btn').click(function() {
    // Filter out deleted images
    const remainingImages = images.filter(image => !deletedImages.includes(image));
    
    // Create FormData object to send images to the server
    const formData = new FormData();
    remainingImages.forEach(image => {
        formData.append('file', image.file);
    });
  
    // Log FormData contents before sending the request
    console.log('FormData contents:');
    for (let pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
    }
    
    // Send images to the server using AJAX
    $.ajax({
        url: '/dropphoto',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            // Handle success response if needed
            console.log('Upload successful');
        },
        error: function(xhr, status, error) {
            console.error('Error uploading file:', error);
        }
    });
});