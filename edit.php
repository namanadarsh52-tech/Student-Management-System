<?php
include 'db.php';

// Validate ID parameter
if (!isset($_GET['id']) || empty($_GET['id'])) {
    die("Error: Student ID is required");
}

$id = $_GET['id'];

// Validate ID is numeric
if (!is_numeric($id)) {
    die("Error: Invalid Student ID");
}

// Use prepared statement to prevent SQL injection
$stmt = $conn->prepare("SELECT * FROM students WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $stmt->close();
    die("Error: Student not found");
}

$d = $result->fetch_assoc();
$stmt->close();
?>

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="theme.css">
</head>
<body>

<div class="navbar">
<a href="register.html">Register</a>
<a href="view.php">View</a>
</div>

<div class="page">
<div class="container">
<h1>Edit</h1>

<form action="update.php" method="post">
<input type="hidden" name="id" value="<?= htmlspecialchars($d['id']) ?>">
<input name="name" value="<?= htmlspecialchars($d['name']) ?>">
<input name="email" value="<?= htmlspecialchars($d['email']) ?>">
<input name="age" value="<?= htmlspecialchars($d['age']) ?>">
<button>Update</button>
</form>

</div>

</body>
</html>
