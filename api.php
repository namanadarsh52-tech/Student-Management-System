<?php
// api.php - Perplexity Search API proxy

header('Content-Type: application/json');

// 1) Read query from GET or POST
$query = $_GET['q'] ?? $_POST['q'] ?? null;

if (!$query) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing parameter: q'
    ]);
    exit;
}

// 2) Your Perplexity API key
$apiKey = 'YOUR_PPLX_API_KEY_HERE';

// 3) Build request payload for Search API
$payload = [
    "query" => $query,
    // Optional: tune these if you want
    "max_results" => 5,           // 1–20 allowed
    // "country" => "IN",         // ISO country code (optional)
    // "search_domain_filter" => ["example.com"], // optional allowlist/denylist
];

// 4) Initialize cURL
$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => 'https://api.perplexity.ai/search',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Authorization: ' . 'Bearer ' . $apiKey,
    ],
    CURLOPT_POSTFIELDS => json_encode($payload),
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($response === false) {
    $error = curl_error($ch);
    curl_close($ch);

    http_response_code(500);
    echo json_encode([
        'error' => 'cURL error: ' . $error
    ]);
    exit;
}

curl_close($ch);

// 5) Decode and handle API response
$data = json_decode($response, true);

if ($httpCode >= 400) {
    http_response_code($httpCode);
    echo json_encode([
        'error' => $data['error']['message'] ?? 'API error',
        'status' => $httpCode
    ]);
    exit;
}

// If you want to return only the result list:
$results = $data['results'] ?? [];

echo json_encode([
    'query' => $query,
    'results' => $results,
    // 'raw' => $data, // uncomment if you want the full original payload
]);
