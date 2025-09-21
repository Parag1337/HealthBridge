// This file contains the JavaScript for the application.

// Function to handle appointment booking
function bookAppointment(doctorId, patientId, date, time) {
    // AJAX request to book an appointment
    $.ajax({
        url: '/find_doctors',
        method: 'POST',
        data: {
            doctor_id: doctorId,
            patient_id: patientId,
            date: date,
            time: time
        },
        success: function(response) {
            alert('Appointment booked successfully!');
            // Optionally, refresh the appointments list
            loadAppointments();
        },
        error: function(error) {
            alert('Error booking appointment. Please try again.');
        }
    });
}

// Function to load appointments
function loadAppointments() {
    $.ajax({
        url: '/get_appointments',
        method: 'GET',
        success: function(data) {
            // Populate appointments on the page
            $('#appointmentsList').empty();
            data.forEach(function(appointment) {
                $('#appointmentsList').append('<li>' + appointment.date + ' - ' + appointment.time + '</li>');
            });
        },
        error: function(error) {
            alert('Error loading appointments.');
        }
    });
}

// Function to set medicine reminders
function setMedicineReminder(medicineName, dosage, time) {
    // AJAX request to set a reminder
    $.ajax({
        url: '/set_reminder',
        method: 'POST',
        data: {
            medicine_name: medicineName,
            dosage: dosage,
            time: time
        },
        success: function(response) {
            alert('Reminder set successfully!');
        },
        error: function(error) {
            alert('Error setting reminder. Please try again.');
        }
    });
}

// Function to initialize the chatbot
function initChatbot() {
    // Code to initialize the chatbot goes here
    // This could involve setting up event listeners or loading a chatbot library
}

// Document ready function
$(document).ready(function() {
    loadAppointments(); // Load appointments on page load
    initChatbot(); // Initialize the chatbot
});