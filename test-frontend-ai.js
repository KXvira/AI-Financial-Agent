// Test the exact frontend AI call
const fetch = require('node-fetch');

async function testAIHealth() {
  try {
    console.log('Testing AI health endpoint...');
    const response = await fetch('http://localhost:8000/ai/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
    
    const data = await response.json();
    console.log('Response data:', JSON.stringify(data, null, 2));
    
    if (response.ok) {
      console.log('✅ AI Health check successful');
    } else {
      console.log('❌ AI Health check failed');
    }
  } catch (error) {
    console.error('❌ Error calling AI health:', error.message);
  }
}

testAIHealth();
