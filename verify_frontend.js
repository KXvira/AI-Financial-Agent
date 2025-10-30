#!/usr/bin/env node
/**
 * Frontend Integration Verification Script
 * Tests Next.js frontend API calls and component rendering
 */

const http = require('http');
const https = require('https');

const COLORS = {
  RESET: '\x1b[0m',
  GREEN: '\x1b[32m',
  RED: '\x1b[31m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  BOLD: '\x1b[1m',
};

class FrontendVerifier {
  constructor(frontendUrl = 'http://localhost:3000', backendUrl = 'http://localhost:8000') {
    this.frontendUrl = frontendUrl;
    this.backendUrl = backendUrl;
    this.results = {
      passed: [],
      warnings: [],
      failed: [],
    };
  }

  log(message, type = 'info') {
    const icons = {
      success: '✅',
      warning: '⚠️ ',
      error: '❌',
      info: 'ℹ️ ',
    };
    const colors = {
      success: COLORS.GREEN,
      warning: COLORS.YELLOW,
      error: COLORS.RED,
      info: COLORS.BLUE,
    };

    console.log(`${colors[type]}${icons[type]} ${message}${COLORS.RESET}`);
    this.results[type === 'success' ? 'passed' : type === 'warning' ? 'warnings' : type === 'error' ? 'failed' : 'info'].push(message);
  }

  logHeader(message) {
    console.log(`\n${COLORS.BOLD}${'='.repeat(70)}`);
    console.log(`  ${message}`);
    console.log(`${'='.repeat(70)}${COLORS.RESET}\n`);
  }

  async makeRequest(url, method = 'GET', headers = {}, body = null) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const client = urlObj.protocol === 'https:' ? https : http;
      
      const options = {
        hostname: urlObj.hostname,
        port: urlObj.port,
        path: urlObj.pathname + urlObj.search,
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
      };

      const req = client.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
          try {
            resolve({
              status: res.statusCode,
              headers: res.headers,
              data: data ? JSON.parse(data) : null,
            });
          } catch (e) {
            resolve({
              status: res.statusCode,
              headers: res.headers,
              data: data,
            });
          }
        });
      });

      req.on('error', reject);
      
      if (body) {
        req.write(JSON.stringify(body));
      }
      
      req.end();
    });
  }

  async testFrontendAccessibility() {
    this.logHeader('Phase 1: Frontend Accessibility');

    const pages = [
      { path: '/', name: 'Home/Dashboard' },
      { path: '/login', name: 'Login Page' },
      { path: '/register', name: 'Register Page' },
      { path: '/invoices', name: 'Invoices Page' },
      { path: '/payments', name: 'Payments Page' },
      { path: '/receipts', name: 'Receipts Page' },
      { path: '/reports', name: 'Reports Page' },
      { path: '/customers', name: 'Customers Page' },
    ];

    for (const page of pages) {
      try {
        const response = await this.makeRequest(`${this.frontendUrl}${page.path}`);
        
        if (response.status === 200) {
          this.log(`${page.name} (${page.path}) - Accessible`, 'success');
        } else if (response.status === 307 || response.status === 308) {
          this.log(`${page.name} (${page.path}) - Redirects (auth required)`, 'warning');
        } else {
          this.log(`${page.name} (${page.path}) - Status ${response.status}`, 'warning');
        }
      } catch (error) {
        this.log(`${page.name} (${page.path}) - Not accessible: ${error.message}`, 'error');
      }
    }
  }

  async testBackendEndpoints() {
    this.logHeader('Phase 2: Backend API Endpoints');

    // Test public endpoints
    const publicEndpoints = [
      { method: 'POST', path: '/api/auth/login', name: 'Login Endpoint' },
      { method: 'POST', path: '/api/auth/register', name: 'Register Endpoint' },
    ];

    for (const endpoint of publicEndpoints) {
      try {
        const response = await this.makeRequest(
          `${this.backendUrl}${endpoint.path}`,
          endpoint.method,
          {},
          endpoint.method === 'POST' ? {} : null
        );
        
        if (response.status < 500) {
          this.log(`${endpoint.name} - Responding (${response.status})`, 'success');
        } else {
          this.log(`${endpoint.name} - Server error (${response.status})`, 'error');
        }
      } catch (error) {
        this.log(`${endpoint.name} - Not accessible: ${error.message}`, 'error');
      }
    }

    // Test authentication
    try {
      const loginResponse = await this.makeRequest(
        `${this.backendUrl}/api/auth/login`,
        'POST',
        {},
        { email: 'admin@finagent.com', password: 'admin123' }
      );

      if (loginResponse.status === 200 && loginResponse.data?.access_token) {
        this.log('Authentication - Token obtained successfully', 'success');
        this.token = loginResponse.data.access_token;

        // Test protected endpoints with token
        await this.testProtectedEndpoints();
      } else {
        this.log('Authentication - Failed to obtain token', 'warning');
      }
    } catch (error) {
      this.log(`Authentication - Error: ${error.message}`, 'error');
    }
  }

  async testProtectedEndpoints() {
    this.logHeader('Phase 3: Protected Endpoints');

    const headers = {
      'Authorization': `Bearer ${this.token}`,
    };

    const endpoints = [
      { method: 'GET', path: '/api/dashboard/stats', name: 'Dashboard Stats' },
      { method: 'GET', path: '/api/invoices?page=1&page_size=5', name: 'Invoice List' },
      { method: 'GET', path: '/api/payments?page=1&page_size=5', name: 'Payment List' },
      { method: 'GET', path: '/receipts/?page=1&page_size=5', name: 'Receipt List' },
      { method: 'GET', path: '/reports/types', name: 'Report Types' },
      { method: 'GET', path: '/reports/income-statement?start_date=2024-01-01&end_date=2024-12-31', name: 'Income Statement' },
      { method: 'GET', path: '/reports/customers', name: 'Customer List' },
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await this.makeRequest(
          `${this.backendUrl}${endpoint.path}`,
          endpoint.method,
          headers
        );
        
        if (response.status === 200) {
          const dataSize = JSON.stringify(response.data).length;
          this.log(`${endpoint.name} - Working (${dataSize} bytes)`, 'success');
        } else if (response.status === 401) {
          this.log(`${endpoint.name} - Auth failed (${response.status})`, 'error');
        } else {
          this.log(`${endpoint.name} - Status ${response.status}`, 'warning');
        }
      } catch (error) {
        this.log(`${endpoint.name} - Error: ${error.message}`, 'error');
      }
    }
  }

  async testAPIResponseStructure() {
    this.logHeader('Phase 4: API Response Structure Validation');

    if (!this.token) {
      this.log('Skipping - no auth token', 'warning');
      return;
    }

    const headers = { 'Authorization': `Bearer ${this.token}` };

    // Test dashboard stats structure
    try {
      const response = await this.makeRequest(
        `${this.backendUrl}/api/dashboard/stats`,
        'GET',
        headers
      );

      if (response.status === 200 && response.data) {
        const requiredFields = ['total_revenue', 'total_expenses', 'invoices_count', 'payments_count'];
        const hasAllFields = requiredFields.every(field => field in response.data);
        
        if (hasAllFields) {
          this.log('Dashboard Stats - Response structure valid', 'success');
        } else {
          this.log('Dashboard Stats - Missing required fields', 'warning');
        }
      }
    } catch (error) {
      this.log(`Dashboard Stats structure - Error: ${error.message}`, 'error');
    }

    // Test invoice list structure
    try {
      const response = await this.makeRequest(
        `${this.backendUrl}/api/invoices?page=1&page_size=1`,
        'GET',
        headers
      );

      if (response.status === 200 && response.data) {
        const hasInvoices = Array.isArray(response.data) || 'invoices' in response.data;
        
        if (hasInvoices) {
          this.log('Invoice List - Response structure valid', 'success');
        } else {
          this.log('Invoice List - Unexpected structure', 'warning');
        }
      }
    } catch (error) {
      this.log(`Invoice List structure - Error: ${error.message}`, 'error');
    }
  }

  async testCORS() {
    this.logHeader('Phase 5: CORS Configuration');

    try {
      const response = await this.makeRequest(
        `${this.backendUrl}/api/auth/login`,
        'OPTIONS'
      );

      const corsHeaders = {
        'access-control-allow-origin': response.headers['access-control-allow-origin'],
        'access-control-allow-methods': response.headers['access-control-allow-methods'],
        'access-control-allow-headers': response.headers['access-control-allow-headers'],
      };

      if (corsHeaders['access-control-allow-origin']) {
        if (corsHeaders['access-control-allow-origin'] === '*') {
          this.log('CORS allows all origins (⚠️  not recommended for production)', 'warning');
        } else {
          this.log(`CORS configured: ${corsHeaders['access-control-allow-origin']}`, 'success');
        }
      } else {
        this.log('CORS headers not found', 'warning');
      }
    } catch (error) {
      this.log(`CORS test - Error: ${error.message}`, 'error');
    }
  }

  generateReport() {
    this.logHeader('Final Report');

    const total = this.results.passed.length + this.results.warnings.length + this.results.failed.length;
    const score = total > 0 
      ? ((this.results.passed.length + this.results.warnings.length * 0.5) / total) * 100 
      : 0;

    console.log(`${COLORS.BOLD}Test Statistics:${COLORS.RESET}`);
    console.log(`  Total Tests: ${total}`);
    console.log(`  ${COLORS.GREEN}✅ Passed: ${this.results.passed.length}${COLORS.RESET}`);
    console.log(`  ${COLORS.YELLOW}⚠️  Warnings: ${this.results.warnings.length}${COLORS.RESET}`);
    console.log(`  ${COLORS.RED}❌ Failed: ${this.results.failed.length}${COLORS.RESET}`);
    console.log(`\n${COLORS.BOLD}Overall Score: ${score.toFixed(1)}/100${COLORS.RESET}`);

    if (score >= 90) {
      console.log(`${COLORS.GREEN}${COLORS.BOLD}Status: PRODUCTION READY ✅${COLORS.RESET}`);
    } else if (score >= 75) {
      console.log(`${COLORS.YELLOW}${COLORS.BOLD}Status: NEEDS MINOR FIXES ⚠️${COLORS.RESET}`);
    } else {
      console.log(`${COLORS.RED}${COLORS.BOLD}Status: NEEDS ATTENTION ❌${COLORS.RESET}`);
    }

    // Save report
    const fs = require('fs');
    const reportFile = `frontend_audit_report_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    fs.writeFileSync(reportFile, JSON.stringify({
      timestamp: new Date().toISOString(),
      frontendUrl: this.frontendUrl,
      backendUrl: this.backendUrl,
      statistics: {
        total,
        passed: this.results.passed.length,
        warnings: this.results.warnings.length,
        failed: this.results.failed.length,
        score,
      },
      results: this.results,
    }, null, 2));

    console.log(`\n${COLORS.BLUE}Report saved to: ${reportFile}${COLORS.RESET}\n`);
  }

  async runAllTests() {
    console.log(`\n${COLORS.BOLD}${'='.repeat(70)}`);
    console.log('     FRONTEND INTEGRATION VERIFICATION SCRIPT');
    console.log('     Testing Next.js Frontend & Backend Integration');
    console.log(`${'='.repeat(70)}${COLORS.RESET}\n`);

    await this.testFrontendAccessibility();
    await this.testBackendEndpoints();
    await this.testAPIResponseStructure();
    await this.testCORS();
    this.generateReport();
  }
}

// Main execution
const verifier = new FrontendVerifier();
verifier.runAllTests().catch(error => {
  console.error(`${COLORS.RED}Fatal error: ${error.message}${COLORS.RESET}`);
  process.exit(1);
});
