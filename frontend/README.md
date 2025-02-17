## Installation and Running the Frontend

To set up and run the frontend application, follow these steps:

1. **Ensure Node.js is installed**:  
   The frontend requires Node.js. You can check if Node.js is installed by running:
   ```bash
   node -v
   ```
   If Node.js is not installed, download and install it from [nodejs.org](https://nodejs.org/).

2. **Navigate to the frontend directory**:  
   Open your terminal and navigate to the `frontend` directory of the project:
   ```bash
   cd frontend
   ```

3. **Install dependencies**:  
   Use npm to install the necessary dependencies:
   ```bash
   npm install
   ```

4. **Run the development server**:  
   Start the development server to run the application locally:
   ```bash
   npm run dev
   ```
   The application will be running, and you can access it at `http://localhost:5173/` by default.

5. **Build for production**:  
   To create an optimized production build, run:
   ```bash
   npm run build
   ```
   The build output will be located in the `dist` directory.

6. **Preview the production build**:  
   To preview the production build locally, use:
   ```bash
   npm run preview
   ```
   This will serve the production build on a local server for testing purposes.
