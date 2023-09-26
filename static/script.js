var currentDate = new Date();
var year = currentDate.getFullYear();
var month = currentDate.getMonth() + 1; // Months are zero-based
var day = currentDate.getDate();
var maps = true;
var city = "";

function showMessagesForDate(year, month, day) {
    fetch(`/get_messages?year=${year}&month=${month}&day=${day}`)
        .then(response => response.json())
        .then(messages => displayMessages(messages));
}

function displayMessages(messages) {
    var messageContainer = document.getElementById('message-container');
    if (messages.length === 0) {
        messageContainer.innerHTML = '<p>No messages for this date.</p>';
    } else {
        var messagesHtml = messages.map(message => '<p>' + message + '</p>').join('');
        messageContainer.innerHTML = messagesHtml;
    }
}

function showLocationsForDate(year, month, day) {
    fetch(`/get_locations?year=${year}&month=${month}&day=${day}`)
        .then(response => response.json())
        .then(locations => displayLocations(locations));
}


function displayLocations(locations) {
    var locationContainer = document.getElementById('locations-container');
    console.log(locations)
    if (locations.length === 0) {
        locationContainer.innerHTML = '<p>No locations for this date.</p>';
    } else {
        var locationsHtml = locations.map(location => '<p>' + location + '</p>').join('');
        console.log(locationsHtml)
        locationContainer.innerHTML = locationsHtml;
    }
}


function showPhotosForDate(year, month, day) {
    fetch(`/get_photos?year=${year}&month=${month}&day=${day}`)
        .then(response => response.json())
        .then(photos => displayPhotos(photos));
}

function displayPhotos(photos) {
    var photoContainer = document.getElementById('photo-container');
    photoContainer.innerHTML = ''; // Clear existing content

    if (photos.length === 0) {
        photoContainer.innerHTML = '<p>No photos for this date.</p>';
    } else {
        var photosHtml = photos.map(photo => {
        if (photo.url.includes('mp4')) {
            return `
                <div class="photo">
                <p>${photo.time}</p>
                    <video controls class="video">
                        <source src="${photo.url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            `;
        } else {
            return `
                <div class="photo">
                <p>${photo.time}</p>
                    <img src="${photo.url}" alt="Photo" class="photo" >
                </div>
            `;
        }
        }).join('');

        photoContainer.innerHTML = photosHtml;
    }
}


function updateCalendarDisplay(year, month) {
    // Update the displayed year and month
    document.getElementById('current-year').textContent = year;
    document.getElementById('current-month').textContent = getMonthName(month);
    
    // Update the calendar table
    if (!maps){
    	fetchCalendarMessages(year, month);
    } else{
    	fetchCalendarLocations(year, month);
    }
}

// Inside your fetchCalendar function
function fetchCalendarMessages(year, month) {
    fetch(`/get_calendar?year=${year}&month=${month}`)
        .then(response => response.json())
        .then(data => {
            fetch(`/get_messages_count?year=${year}&month=${month}`)
                .then(response => response.json())
                .then(messagesCount => {
                    var calendarBody = document.getElementById('calendar-body');
                    calendarBody.innerHTML = ''; // Clear existing content

                    data.forEach((week, weekIndex) => {
                        var row = document.createElement('tr');
                        week.forEach((day, dayIndex) => {
                            var cell = document.createElement('td');
                            cell.textContent = day;
                            cell.classList.add('calendar-cell'); // Apply common class
                            
                            var dayMessagesCount = messagesCount[weekIndex][dayIndex];
                            cell.dataset.messagesCount = dayMessagesCount; // Store messages count as a data attribute
                            
                            // Calculate background color based on messages count
                            var bgColor = calculateBackgroundColor(dayMessagesCount);
                            cell.style.backgroundColor = bgColor;

                            cell.onclick = function() {
                                showMessagesForDate(year, month, day);
                                showLocationsForDate(year, month, day);
                                showPhotosForDate(year, month, day);
                            };
                            row.appendChild(cell);
                        });
                        calendarBody.appendChild(row);
                    });
                });
        });
}

function fetchCalendarLocations(year, month) {
    fetch(`/get_calendar?year=${year}&month=${month}`)
        .then(response => response.json())
        .then(data => {
            fetch(`/get_locations_count?year=${year}&month=${month}`)
                .then(response => response.json())
                .then(locationsCount => {
                    var calendarBody = document.getElementById('calendar-body');
                    calendarBody.innerHTML = ''; // Clear existing content

                    data.forEach((week, weekIndex) => {
                        var row = document.createElement('tr');
                        week.forEach((day, dayIndex) => {
                            var cell = document.createElement('td');
                            cell.textContent = day;
                            cell.classList.add('calendar-cell'); // Apply common class
                            
                            var dayLocationsCount = locationsCount[weekIndex][dayIndex];
                            cell.dataset.locationsCount = dayLocationsCount; // Store messages count as a data attribute
                            
                            // Calculate background color based on messages count
                            var bgColor = calculateBackgroundColor(dayLocationsCount);
                            cell.style.backgroundColor = bgColor;

                            cell.onclick = function() {
                                showMessagesForDate(year, month, day);
                                showLocationsForDate(year, month, day);
                                showPhotosForDate(year, month, day); 
                            };
                            row.appendChild(cell);
                        });
                        calendarBody.appendChild(row);
                    });
                });
        });
}
function calculateBackgroundColor(messagesCount) {
    // Define color thresholds and corresponding colors
    if (messagesCount == 0) {
    	return `rgb(0, 0, 0)`;
    }else{
    	return `rgb(159,193,249)`;
    }
}



function previousMonth() {
    month -= 1;
    if (month < 1) {
        month = 12;
        year -= 1;
    }
    updateCalendarDisplay(year, month);
}

function nextMonth() {
    month += 1;
    if (month > 12) {
        month = 1;
        year += 1;
    }
    updateCalendarDisplay(year, month);
}

function getMonthName(month) {
    var months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    return months[month - 1];
}



window.onload = function() {
    updateCalendarDisplay(year, month);
    document.getElementById('form-chat').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    
    // Get the search query from the input field
    var searchKeyWord = document.getElementById('keyword').value;
    
    fetch(`/keyword?keyword=${searchKeyWord}`)
    	.then(response => response.json())  // Parse the response as JSON
        .then(data => {
            if (data.message === "OK") {
                console.log('Server response: OK');
                maps=false
                updateCalendarDisplay(year, month);
            } else {
                console.log('Server response: Not OK');
            }
        })
	});

	document.getElementById('form-map').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    
    // Get the search query from the input field
    var searchCity = document.getElementById('city').value;
    
    fetch(`/city?city=${searchCity}`)
    	.then(response => response.json())  // Parse the response as JSON
        .then(data => {
            if (data.message === "OK") {
                console.log('Server response: OK');
                maps=true
                updateCalendarDisplay(year, month);
            } else {
                console.log('Server response: Not OK');
            }
        })
	});
};

