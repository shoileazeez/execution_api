const ivm = require('isolated-vm');

async function executeJavaScript(code, inputData = "") {
    try {
        const isolate = new ivm.Isolate({ memoryLimit: 128 });
        const context = isolate.createContext();
        const jail = context.global;

        jail.setSync('inputData', inputData);
        const script = isolate.compileScriptSync(code);
        let result = script.runSync(context);

        // Handle non-serializable values:
        if (typeof result === 'function') {
            result = result.toString(); // Convert functions to strings
        } else if (typeof result === 'object' && result !== null) {
            try {
                result = JSON.parse(JSON.stringify(result)); // Attempt deep copy for serializable objects
            } catch (e) {
                result = "Non-serializable object"; // Or handle differently (e.g., custom serialization)
            }
        }

        isolate.dispose();
        return { result: result };
    } catch (error) {
        return { error: error.message };
    }
}

const code = process.argv[2];
const inputData = process.argv[3] || "";

executeJavaScript(code, inputData)
    .then(result => console.log(JSON.stringify({ output: result })))
    .catch(error => {
        console.error(JSON.stringify({ output: { error: error.message } }));
        process.exit(1);
    });