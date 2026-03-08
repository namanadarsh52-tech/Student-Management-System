<?php
$conn = mysqli_connect("localhost", "root", "", "sseas");

if(!$conn){
    die("Connection failed: " . mysqli_connect_error());
}

if(isset($_GET['id'])){
    $id = $_GET['id'];

    $sql = "DELETE FROM students WHERE student_id='$id'";

    if(mysqli_query($conn, $sql)){
        echo "Record deleted successfully";
    } else {
        echo "Error deleting record: " . mysqli_error($conn);
    }
}

mysqli_close($conn);
?>