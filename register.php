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
    // Validate and sanitize inputs
    $name = validateInput($_POST['name'] ?? '');
    $email = validateInput($_POST['email'] ?? '');
    $age = validateInput($_POST['age'] ?? '');

    $errors = [];

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

    // If no errors, proceed with database insertion
    if (empty($errors)) {
        // Use prepared statements to prevent SQL injection
        $stmt = $conn->prepare("INSERT INTO students (name, email, age) VALUES (?, ?, ?)");
        $stmt->bind_param("ssi", $name, $email, $age);
        
        if ($stmt->execute()) {
            $success = true;
            $message = "Student registered successfully!";
        } else {
            $error = $stmt->error;
            // Check for duplicate email
            if (strpos($error, 'Duplicate entry') !== false) {
                $errors[] = "Email already exists";
            } else {
                $errors[] = "Error: " . $error;
            }
        }
        $stmt->close();
    }
}
?>

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="theme.css">
<title>Register</title>
</head>
<body>

<div class="navbar">
<a href="register.html">Register</a>
<a href="view.php">View</a>
</div>

<div class="page">
<div class="container">

<?php if (isset($success) && $success): ?>
    <h1>Success ✅</h1>
    <p style="text-align: center; color: #4ade80;"><?= $message ?></p>
    <a href="register.html"><button style="margin-top: 15px;">Register Another</button></a>
<?php elseif (!empty($errors)): ?>
    <h1>Error ❌</h1>
    <ul style="color: #f87171; margin-left: 20px;">
        <?php foreach ($errors as $error): ?>
            <li><?= $error ?></li>
        <?php endforeach; ?>
    </ul>
    <a href="register.html"><button style="margin-top: 15px;">Go Back</button></a>
<?php else: ?>
    <h1>Register Student</h1>
    <form action="register.php" method="post">
        <input name="name" placeholder="Name" required value="<?= isset($name) ? $name : '' ?>">
        <input name="email" type="email" placeholder="Email" required value="<?= isset($email) ? $email : '' ?>">
        <input name="age" type="number" placeholder="Age" required value="<?= isset($age) ? $age : '' ?>">
        <button>Register</button>
    </form>
<?php endif; ?>

</div>
</div>

</body>
</html>
