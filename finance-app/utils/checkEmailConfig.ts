/**
 * Utility to check if email service is properly configured
 */

interface EmailConfigResponse {
  configured: boolean;
  service?: string;
  from_email?: string;
  from_name?: string;
  smtp_host?: string;
  smtp_port?: number;
}

interface CheckEmailResult {
  isConfigured: boolean;
  config?: EmailConfigResponse;
  error?: string;
}

/**
 * Check if email service is configured and ready to send emails
 * @returns Promise with configuration status and details
 */
export async function checkEmailConfig(): Promise<CheckEmailResult> {
  try {
    const response = await fetch('http://localhost:8000/automation/email/config');
    
    if (!response.ok) {
      return {
        isConfigured: false,
        error: `Failed to check email config: ${response.statusText}`
      };
    }

    const data: EmailConfigResponse = await response.json();
    
    return {
      isConfigured: data.configured,
      config: data
    };
  } catch (error) {
    console.error('Error checking email configuration:', error);
    return {
      isConfigured: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

/**
 * Send a test email to verify configuration
 * @param toEmail Recipient email address
 * @returns Promise with test result
 */
export async function sendTestEmail(toEmail: string): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`http://localhost:8000/automation/email/test?recipient=${encodeURIComponent(toEmail)}`, {
      method: 'POST',
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        message: data.detail || 'Failed to send test email'
      };
    }

    return {
      success: true,
      message: data.message || 'Test email sent successfully'
    };
  } catch (error) {
    console.error('Error sending test email:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}
