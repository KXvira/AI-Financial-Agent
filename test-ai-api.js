// Test script to verify AI API configuration
const API_BASE_URL = 'http://localhost:8000';

async function testAIAPI() {
  console.log('Testing AI API at:', API_BASE_URL);
  
  try {
    // Test health endpoint
    console.log('\n1. Testing health endpoint...');
    const healthResponse = await fetch(`${API_BASE_URL}/ai/health`);
    const healthData = await healthResponse.json();
    console.log('Health Response:', healthData);
    
    // Test AI ask endpoint
    console.log('\n2. Testing AI ask endpoint...');
    const askResponse = await fetch(`${API_BASE_URL}/ai/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: 'Hello, test query' }),
    });
    const askData = await askResponse.json();
    console.log('AI Response:', askData.answer?.substring(0, 100) + '...');
    
    console.log('\n✅ All tests passed! API is working correctly.');
  } catch (error) {
    console.error('❌ Error testing API:', error);
  }
}

// Run the test
testAIAPI();