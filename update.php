<?php
include 'db.php';

// Input validation function
function validateInput($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Check if form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $id = $_POST['id'] ?? '';
    $name = validateInput($_POST['name'] ?? '');
    $email = validateInput($_POST['email'] ?? '');
    $age = validateInput($_POST['age'] ?? '');

    $errors = [];

    // Validate ID
    if (empty($id) || !is_numeric($id)) {
        $errors[] = "Invalid student ID";
    }

    // Name validation
    if (empty($name)) {
        $errors[] = "Name is required";
    } elseif (strlen($name) < 2) {
        $errors[] = "Name must be at least 2 characters";
    }

    // Email validation
    if (empty($email)) {
        $errors[] = "Email is required";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Invalid email format";
    }

    // Age validation
    if (empty($age)) {
        $errors[] = "Age is required";
    } elseif (!is_numeric($age) || $age < 1 || $age > 150) {
        $errors[] = "Please enter a valid age";
    }

    // If no errors, proceed with database update
    if (empty($errors)) {
        // Use prepared statements to prevent SQL injection
        $stmt = $conn->prepare("UPDATE students SET name = ?, email = ?, age = ? WHERE id = ?");
        $stmt->bind_param("ssii", $name, $email, $age, $id);
        
        if ($stmt->execute()) {
            header("location:view.php");
            exit();
        } else {
            $error = $stmt->error;
            if (strpos($error, 'Duplicate entry') !== false) {
                $errors[] = "Email already exists";
            } else {
                $errors[] = "Error: " . $error;
            }
        }
        $stmt->close();
    }
} else {
    // Redirect if not POST request
    header("location:view.php");
    exit();
}
?>

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="theme.css">
<title>Update Error</title>
</head>
<body>

<div class="navbar">
<a href="register.html">Register</a>
<a href="view.php">View</a>
</div>

<div class="page">
<div class="container">
    <h1>Error ❌</h1>
    <?php if (!empty($errors)): ?>
        <ul style="color: #f87171; margin-left: 20px;">
            <?php foreach ($errors as $error): ?>
                <li><?= $error ?></li>
            <?php endforeach; ?>
        </ul>
    <?php endif; ?>
    <a href="view.php"><button style="margin-top: 15px;">Go Back</button></a>
</div>
</div>

</body>
</html>
