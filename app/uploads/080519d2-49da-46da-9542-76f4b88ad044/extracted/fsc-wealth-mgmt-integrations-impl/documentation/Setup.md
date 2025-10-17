## Setup Steps

### Connect your Salesforce and MuleSoft Instances

1. From Setup, in the Quick Find box, enter Integrations Setup, and then select **Integrations > MuleSoft > MuleSoft Direct**.
2. In Financial Services Cloud Integrations, click **I accept the terms and conditions**.
3. Turn on Financial Services Cloud Integrations.
4. Click **Connect to MuleSoft Instance**.
5. Select a server and click **Next**.
6. Enter your MuleSoft username and password and sign in.
7. Grant access to your MuleSoft account.
    -  It takes a few minutes for Salesforce to connect to MuleSoft.
    - Your Salesforce and MuleSoft instances are now connected. You can view the connection details and available integrations.

### Enable the Integration Between Salesforce and the Core Banking System

1. On the Integrations Setup page, in the Available Integrations section, from the list of available integrations, select the integration that you want to enable, and then click **Enable**.
2. Select the business group that you want to enable the integration for.
3. Select the environment where you want to enable the integration.
4. Enter the app name. Make sure that the app name is unique for your MuleSoft instance.
5. Click **Next**.
6. To connect to the core banking system, select the authentication protocol for the integration and its dependent apps, and then enter the relevant details.
7. Enable the integration and wait for the process to be completed. A named credential is created for the enabled integration.
8. From Setup, enter Named Credential in the Quick Find box, and then select Named Credentials.
9. Verify that a named credential was added for the connected MuleSoft instance.