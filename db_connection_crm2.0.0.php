<?php
// Enable detailed error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Database configuration
$host = "p:localhost";  // "p:" prefix for persistent connection
$db_name = "baselinepractice_crm";
$db_user = "baselinepractice_crm";
$db_pass = "BXfe36QKLZwy8";

// Create a global connection
global $conn;

// Initialize connection
$conn = mysqli_init();

// Set connection options for better performance
mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 300);
mysqli_options($conn, MYSQLI_OPT_READ_TIMEOUT, 300);
mysqli_options($conn, MYSQLI_OPT_INT_AND_FLOAT_NATIVE, 1);

// Connect to the database with persistent connection
if (!mysqli_real_connect($conn, $host, $db_user, $db_pass, $db_name)) {
    die(json_encode([
        "error" => "Database connection failed: " . mysqli_connect_error(),
        "errno" => mysqli_connect_errno()
    ]));
}

// Set connection properties
$conn->set_charset("utf8mb4");

// Configure connection for better performance
$conn->query("SET SESSION sql_mode = 'NO_ENGINE_SUBSTITUTION'");
$conn->query("SET SESSION wait_timeout = 28800"); // 8 hours
$conn->query("SET SESSION interactive_timeout = 28800"); // 8 hours
$conn->query("SET SESSION net_read_timeout = 300");
$conn->query("SET SESSION net_write_timeout = 300");

// Set the default timezone
date_default_timezone_set('Asia/Karachi');

// Return the connection
return $conn;
?> 