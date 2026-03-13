// Simple test to verify backend connectivity from frontend
async function testBackendConnection() {
  try {
    console.log("Testing connection to backend...");
    
    // Test basic connectivity
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log(`Health check status: ${response.status}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Health check response:', data);
      
      // Test the sign-up endpoint
      console.log("Testing sign-up endpoint...");
      const signupResponse = await fetch('http://localhost:8000/sign-up', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'Password123!',
          name: 'Test User'
        })
      });
      
      console.log(`Sign-up status: ${signupResponse.status}`);
      
      if (signupResponse.ok) {
        const signupData = await signupResponse.json();
        console.log('Sign-up response:', signupData);
      } else {
        const errorData = await signupResponse.json();
        console.log('Sign-up error:', errorData);
      }
    } else {
      console.log('Health check failed');
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Run the test
testBackendConnection();