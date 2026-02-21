function tryParseJson(input) {
  try {
    return JSON.parse(input);
  } catch (error) {
    // Attempt to extract JSON object or array from the input string
    const objectStart = input.indexOf('{');
    const objectEnd = input.lastIndexOf('}');
    if (objectStart !== -1 && objectEnd > objectStart) {
      try {
        return JSON.parse(input.slice(objectStart, objectEnd + 1));
      } catch {}
    }

    const arrayStart = input.indexOf('[');
    const arrayEnd = input.lastIndexOf(']');
    if (arrayStart !== -1 && arrayEnd > arrayStart) {
      try {
        return JSON.parse(input.slice(arrayStart, arrayEnd + 1));
      } catch {}
    }

    // Throw the original error if parsing fails
    throw error;
  }
}

function collectTestEntries(data) {
  const testEntries = [];

  function traverse(node, path) {
    if (!node) return;

    if (Array.isArray(node)) {
      node.forEach(child => traverse(child, path));
    } else if (typeof node === 'object') {
      // Check if the node represents a test entry
      if (node.title && node.status) {
        const fullPath = path.concat(node.title).join(' > ');
        testEntries.push({
          title: fullPath,
          status: node.status,
          duration: node.duration || null,
        });
      }

      // Recursively traverse child nodes
      Object.keys(node).forEach(key => traverse(node[key], path.concat(key)));
    }
  }

  traverse(data, []);
  return testEntries;
}

module.exports = { tryParseJson, collectTestEntries };