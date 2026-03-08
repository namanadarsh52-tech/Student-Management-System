<?php
include 'db.php';

// Use prepared statement to prevent SQL injection
$stmt = $conn->prepare("SELECT * FROM students ORDER BY id DESC");
$stmt->execute();
$result = $stmt->get_result();

if (!$result) {
    die("Query error: " . $stmt->error);
}
?>

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="theme.css">
<title>View Students</title>
</head>
<body>

<div class="navbar">
<a href="register.html">Register</a>
<a href="view.php">View</a>
</div>

<div class="page">
<div class="container" style="width:700px">
<h1>Students</h1>

<?php if ($result->num_rows === 0): ?>
    <p style="text-align: center; color: #a78bfa;">No students found. <a href="register.html">Register one!</a></p>
<?php else: ?>
<table>
<tr>
<th>ID</th><th>Name</th><th>Email</th><th>Age</th><th>Status</th><th>Action</th>
</tr>

<?php while($row = $result->fetch_assoc()): 
    // Compute status on the fly, no need for a database column
    $ageStatus = ($row['age'] >= 18) ? 'Adult' : 'Minor';
?>
<tr>
<td><?= htmlspecialchars($row['id']) ?></td>
<td><?= htmlspecialchars($row['name']) ?></td>
<td><?= htmlspecialchars($row['email']) ?></td>
<td><?= htmlspecialchars($row['age']) ?></td>
<td><?= $ageStatus ?></td>
<td>
<a class="action" href="edit.php?id=<?= $row['id'] ?>">Edit</a> |
<a class="action" href="delete.php?id=<?= $row['id'] ?>" onclick="return confirm('Are you sure?')">Delete</a>
</td>
</tr>
<?php endwhile; ?>
</table>
<?php endif; $stmt->close(); ?>

</div>
</div>

</body>
</html>
