const ivm = require('isolated-vm');

async function executeJavaScript(code, inputData = "") {
  try {
    const isolate = new ivm.Isolate({ memoryLimit: 128 }); // Adjust as needed
    const context = isolate.createContext();
    const jail = context.global;

    jail.setSync('inputData', inputData); // Set input data

    const script = isolate.compileScriptSync(code);
    const result = script.runSync(context);

    isolate.dispose(); // Release resources
    return result;
  } catch (error) {
    console.error("Error executing JavaScript:", error);
    return { error: error.message }; // Return error as an object
  }
}

// Get code and input from command-line arguments:
const code = process.argv[2];
const inputData = process.argv[3] || "";

executeJavaScript(code, inputData)
  .then(result => {
    console.log(JSON.stringify(result)); // Send result as JSON
  })
  .catch(error => {
    console.error(JSON.stringify(error)); // Send error as JSON
    process.exit(1); // Indicate an error
  });