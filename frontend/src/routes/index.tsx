import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  return (
    <main>
      <h1>Logic Loaders</h1>
      <p>Welcome to Logic Loaders.</p>
    </main>
  )
}
