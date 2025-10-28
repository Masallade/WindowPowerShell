<?php
// Enable output buffering for better performance
ob_start();

// Set appropriate headers for persistent connections
header('Connection: Keep-Alive');
header('Keep-Alive: timeout=600, max=1000');
header('Content-Type: application/json');

// Disable output compression if enabled
if (ini_get('zlib.output_compression')) {
    ini_set('zlib.output_compression', 'Off');
}

// Set PHP configuration for persistent connections
ini_set('mysql.allow_persistent', 'On');
ini_set('mysql.max_persistent', -1);
ini_set('mysql.max_links', -1);
ini_set('mysql.connect_timeout', 600);
ini_set('default_socket_timeout', 600);

// Increase PHP memory limit if needed
ini_set('memory_limit', '256M');

// Import files
require_once 'db_connection_crm2.0.0.php';
require_once 'get_employee_shift_info.php';

// Function to send JSON response
function sendJsonResponse($data) {
    echo json_encode($data);
    ob_end_flush();
    if (ob_get_level() > 0) {
        ob_end_clean();
    }
    flush();
}

// Get input data
$input = file_get_contents("php://input");
$data = json_decode($input, true);

// Get the current date and time
$current_date = date('Y-m-d');
$current_time_str = date('Y-m-d H:i:s');
$current_time = date('h:i:s A');

// Main execution
$employeeId = getEmployeeId($data, $conn);
if ($employeeId == null) {
    exit; // getEmployeeId already sends error response
}

$lastRecord = getLastRecord($employeeId);
$employeeShiftDetails = fetchEmployeeShiftDetails($conn, 9, $employeeId);

if ($lastRecord == "none") {
    if (isItAfterShiftTime($employeeShiftDetails['shift_out']) == "true") {
        sendJsonResponse([
            "status" => "error",
            "message" => "This is your first record and you are not in the shift time"
        ]);
        exit;
    }
    
    $employeeShiftDetails['shift_in_difference'] = calculateShiftCurrentTimeDifference($employeeShiftDetails['shift_in']);
    insertFirstRecordOfDay($employeeShiftDetails["employees"], $current_date, $current_time, $current_time_str, $employeeShiftDetails["shift_in_difference"]);
    exit; // insertFirstRecordOfDay already sends response
}

// Rest of your original logic without try-catch...
// Your existing code for handling records, overtime, etc.

?> 