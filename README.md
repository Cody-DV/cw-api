## Installation and Running the App

To install the necessary dependencies and run the `cardwatch-reporting-api` application, follow these steps:

1. **Ensure Python 3.12 is installed**:  
   The application requires Python version 3.12 or higher. You can check your Python version by running:
   ```bash
   python --version
   ```

2. **Install `uv`**:  
   `uv` is a tool for managing Python dependencies. You can install it using pip:
   ```bash
   pip install uv
   ```

3. **Install dependencies**:  
   Use `uv` to install the dependencies:
   ```bash
   uv pip install -r pyproject.toml
   ```

4. **Run the application**:  
   Start the Flask application by executing:
   ```bash
   python app.py
   ```

The application will be running in debug mode and can be accessed at `http://localhost:5000/`.

5. **Create a `.env` file**:  
   The application requires an OpenAI API key to function properly. Create a `.env` file in the root directory of the project and add your OpenAI API key and organization ID in the following format:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   Replace `your_openai_api_key_here` with your actual OpenAI API key and organization ID.

6. **Test the `/prompt` route**:  
   To test the `/prompt` route of the application, you can use a tool like `curl` or Postman. This route will generate a dietary report based on mock data.

   **Using `curl`:**
   ```bash
   curl -X GET http://localhost:5000/prompt
   ```

   **Using Postman:**
   - Open Postman and create a new GET request.
   - Enter the URL: `http://localhost:5000/prompt`
   - Click "Send" to execute the request.

   The response will be a JSON object containing the dietary report, which includes total nutrient intake and dietary notes based on the mock data.

