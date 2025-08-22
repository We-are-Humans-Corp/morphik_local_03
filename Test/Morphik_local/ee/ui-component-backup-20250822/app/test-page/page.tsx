export default function TestPage() {
  return (
    <div style={{ padding: '50px', fontSize: '24px', color: 'red', background: 'white' }}>
      <h1>TEST PAGE WORKS!</h1>
      <p>UI is running on port 3001.</p>
      <p>Next.js app router is working.</p>
      <br />
      <a href="/login" style={{ color: 'blue', textDecoration: 'underline' }}>Go to Login</a>
    </div>
  )
}