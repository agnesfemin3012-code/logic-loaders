export function renderErrorPage(): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Something went wrong</title>
</head>
<body>
  <main>
    <h1>Something went wrong</h1>
    <p>An unexpected error occurred while loading this page.</p>
    <button onclick="window.location.reload()">Try again</button>
  </main>
</body>
</html>`
}
